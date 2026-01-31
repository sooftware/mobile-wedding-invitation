"""
Licensed under the Creative Commons Attribution-NonCommercial-ShareAlike (CC BY-NC-SA) License.

AI Wedding Chatbot with LangGraph & LangSmith.

A RAG-based wedding information chatbot using LangGraph for state management,
including retry logic, infinite loop prevention, and timeout handling.

Author:
    Soohwan Kim (2025.10)

Features:
    - LangGraph-based state management workflow
    - RAG (Retrieval-Augmented Generation) system
    - Automatic retry with exponential backoff
    - Infinite loop prevention (recursion_limit)
    - Timeout handling
    - LangSmith tracing integration

Example:
    >>> chatbot = WeddingChatbotGraph()
    >>> result = await chatbot.get_response("How did you two meet?")
    >>> print(result['response'])
    "We first met at university in 2018..."
"""

import os
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, TypedDict, Annotated, Optional

from operator import add

# LangChain imports
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnableConfig

# LangGraph imports
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Local imports
from .schemas import ChatbotConfig

# LangSmith import (optional)
try:
    from langsmith import traceable
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False
    def traceable(func):
        """Fallback decorator when LangSmith is not available."""
        return func

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== State Definition ====================
class ChatbotState(TypedDict):
    """
    TypedDict defining the state of the LangGraph chatbot.

    Attributes:
        query: User question (original user input)
        search_queries: List of generated search queries (multi-query retrieval)
        chat_history: Previous conversation history
        keywords: List of extracted keywords
        retrieved_docs: List of retrieved documents
        matched_topics: List of matched topics
        confidence: Response confidence score (0.0 ~ 1.0)
        should_fallback: Whether to use fallback response
        response: Final response text
        is_valid_response: Whether response is valid (based on context)
        validation_reason: Reason for validation result
        error: Error message (None if no error)
        messages: Conversation history (accumulated)
        retry_count: int
        max_retries: int
        failed_nodes: List of failed node names
        use_stronger_model: Whether to use GPT-4o instead of GPT-4o-mini
        stronger_model_attempted: Whether GPT-4o has already been tried
    """
    query: str
    search_queries: List[str]
    chat_history: List[Dict[str, str]]
    keywords: List[str]
    retrieved_docs: List[Document]
    matched_topics: List[str]
    confidence: float
    should_fallback: bool
    response: str
    is_valid_response: bool
    validation_reason: str
    error: Optional[str]
    messages: Annotated[List[Dict], add]
    retry_count: int
    max_retries: int
    failed_nodes: List[str]
    use_stronger_model: bool
    stronger_model_attempted: bool


class WeddingChatbotGraph:
    """
    LangGraph-based wedding information chatbot.

    Uses RAG (Retrieval-Augmented Generation) to search the couple's
    knowledge base and generate natural responses.

    Attributes:
        config: Chatbot configuration (model, temperature, etc.)
        wedding_config: Wedding information configuration
        prompts: Prompt template dictionary
        embeddings: Embedding model
        llm: LLM model
        vectorstore: Vector store
        keyword_chain: Keyword extraction chain
        graph: LangGraph workflow
        app: Compiled graph application

    Example:
        >>> chatbot = WeddingChatbotGraph(
        ...     config_path="config/config.json",
        ...     knowledge_path="config/couple_knowledge.json"
        ... )
        >>> result = await chatbot.get_response("Where are you going for honeymoon?")
    """

    def __init__(
        self,
        config_path: str = "config/config.json",
        knowledge_path: str = "config/couple_knowledge.json"
    ) -> None:
        """
        Initialize WeddingChatbotGraph.

        Args:
            config_path: Path to wedding configuration file.
                Defaults to "config/config.json".
            knowledge_path: Path to couple knowledge base file.
                Defaults to "config/couple_knowledge.json".

        Raises:
            FileNotFoundError: If configuration file is not found
            Exception: If error occurs during initialization
        """
        self.config = self._load_chatbot_config()
        self.wedding_config = self._load_wedding_config(config_path)
        self.prompts = self._load_prompts()
        self.knowledge_path = knowledge_path  # Store for fallback retrieval

        # Initialize LangChain components
        self.embeddings = OpenAIEmbeddings(
            model=self.config.embedding_model,
            api_key=self.config.openai_api_key
        )

        self.llm = ChatOpenAI(
            model=self.config.chat_model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=self.config.openai_api_key
        )

        # Initialize Vector Store
        self.vectorstore = self._create_vectorstore(knowledge_path)

        # Build chains
        self.keyword_chain = self._create_keyword_extraction_chain()
        self.query_chain = self._create_query_generation_chain()
        self.validation_chain = self._create_answer_validation_chain()
        self.fallback_retrieval_chain = self._create_fallback_retrieval_chain()

        # Create LangGraph
        self.graph = self._create_graph()
        self.app = self.graph.compile(checkpointer=MemorySaver())

        logger.info("🤖 LangGraph chatbot successfully initialized!")

    def _load_chatbot_config(self) -> ChatbotConfig:
        """
        Load chatbot configuration from environment variables.

        Returns:
            ChatbotConfig object with loaded settings

        Note:
            Uses default values if environment variables are not set
        """
        return ChatbotConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            chat_model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("CHAT_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "300")),
            top_k=int(os.getenv("TOP_K_RESULTS", "3"))
        )

    def _load_wedding_config(self, config_path: str) -> Dict:
        """
        Load wedding information configuration from JSON file.

        Args:
            config_path: Path to configuration file

        Returns:
            Dictionary containing wedding information

        Note:
            Returns empty dict if file is not found
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            return {}

    def _load_prompts(self) -> Dict:
        """
        Load prompt templates from JSON file.

        Returns:
            Dictionary containing prompt templates

        Note:
            Returns default prompts if file is not found
        """
        prompt_path = Path(__file__).parent / "prompts.json"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Prompts file not found: {prompt_path}")
            return {
                "messages": {
                    "fallback": "Sorry 😅 I don't have information about that 😢",
                    "error": "Oops! Something went wrong 😅 Please try again later!"
                }
            }

    def _create_vectorstore(self, knowledge_path: str) -> Chroma:
        """
        Create Chroma vector store from knowledge base.

        Args:
            knowledge_path: Path to knowledge base JSON file

        Returns:
            Chroma vector store instance

        Note:
            Creates empty store with placeholder if no documents found
        """
        documents = self._load_knowledge_documents(knowledge_path)

        if not documents:
            logger.warning("Knowledge base is empty.")
            return Chroma.from_documents(
                documents=[Document(page_content="Empty document", metadata={"id": "empty"})],
                embedding=self.embeddings,
                collection_name="wedding_knowledge"
            )

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )

        split_documents = text_splitter.split_documents(documents)

        vectorstore = Chroma.from_documents(
            documents=split_documents,
            embedding=self.embeddings,
            collection_name="wedding_knowledge"
        )

        logger.info(f"📚 Created vector store with {len(split_documents)} documents.")
        return vectorstore

    def _load_knowledge_documents(self, knowledge_path: str) -> List[Document]:
        """
        Load knowledge base as Document objects.

        Args:
            knowledge_path: Path to knowledge base JSON file

        Returns:
            List of Document objects

        Note:
            Returns empty list if file not found or error occurs
        """
        documents = []

        try:
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            items_data = data if isinstance(data, list) else data.get('knowledge_items', [])

            for item in items_data:
                doc = Document(
                    page_content=f"{item['topic']}: {item['content']}",
                    metadata={
                        "id": item['id'],
                        "topic": item['topic']
                    }
                )
                documents.append(doc)

        except FileNotFoundError:
            logger.warning(f"Knowledge base file not found: {knowledge_path}")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")

        return documents

    def _create_keyword_extraction_chain(self):
        """
        Create keyword extraction chain using LCEL.

        Returns:
            Runnable chain: prompt | llm | json_parser

        Note:
            Uses system prompt from prompts.json
        """
        keyword_prompts = self.prompts.get("keyword_extraction", {})

        prompt = ChatPromptTemplate.from_messages([
            ("system", keyword_prompts.get("system", "Extract keywords.")),
            ("human", "{question}")
        ])

        # Build chain with LCEL
        return prompt | self.llm | JsonOutputParser()

    def _create_query_generation_chain(self):
        """
        Create query generation chain for multi-turn conversations using LCEL.

        Returns:
            Runnable chain: prompt | llm | json_parser

        Note:
            Uses system prompt from prompts.json
            Generates search query based on conversation history
        """
        query_prompts = self.prompts.get("query_generation", {})

        prompt = ChatPromptTemplate.from_messages([
            ("system", query_prompts.get("system", "Generate search query.")),
            ("human", query_prompts.get("user_template", "대화 히스토리:\n{chat_history}\n\n현재 질문: {question}"))
        ])

        # Build chain with LCEL
        return prompt | self.llm | JsonOutputParser()

    def _create_answer_validation_chain(self):
        """
        Create answer validation chain using LCEL.

        Returns:
            Runnable chain: prompt | llm | json_parser

        Note:
            Uses system prompt from prompts.json
            Validates if generated answer is based on context
        """
        validation_prompts = self.prompts.get("answer_validation", {})

        prompt = ChatPromptTemplate.from_messages([
            ("system", validation_prompts.get("system", "Validate the answer.")),
            ("human", validation_prompts.get("user_template", "컨텍스트:\n{context}\n\n질문:\n{question}\n\n생성된 답변:\n{answer}"))
        ])

        # Build chain with LCEL
        return prompt | self.llm | JsonOutputParser()

    def _create_fallback_retrieval_chain(self):
        """
        Create fallback retrieval chain using LCEL.

        Returns:
            Runnable chain: prompt | llm | json_parser

        Note:
            Uses system prompt from prompts.json
            Extracts relevant document IDs from entire knowledge base
        """
        fallback_prompts = self.prompts.get("fallback_retrieval", {})

        prompt = ChatPromptTemplate.from_messages([
            ("system", fallback_prompts.get("system", "Extract relevant information.")),
            ("human", fallback_prompts.get("user_template", "질문: {question}\n\n전체 지식 베이스:\n{knowledge_base}"))
        ])

        # Build chain with LCEL
        return prompt | self.llm | JsonOutputParser()

    def _load_all_knowledge_for_fallback(self) -> str:
        """
        Load entire knowledge base as formatted string for fallback retrieval.

        Returns:
            Formatted string with all knowledge items

        Note:
            Format: "- id: xxx, topic: xxx"
        """
        try:
            with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            items_data = data if isinstance(data, list) else data.get('knowledge_items', [])

            formatted_items = []
            for item in items_data:
                formatted_items.append(f"  - id: \"{item['id']}\", topic: \"{item['topic']}\"")

            return "\n".join(formatted_items)

        except Exception as e:
            logger.error(f"Error loading knowledge base for fallback: {e}")
            return ""

    def _with_retry(self, node_func, node_name: str):
        """
        Wrap a node function with retry logic.

        Args:
            node_func: Original node function to wrap
            node_name: Name of the node for logging

        Returns:
            Wrapped function with error handling

        Note:
            Catches exceptions and adds node to failed_nodes list
        """
        @traceable(name=f"{node_name}_with_retry")
        def wrapper(state: ChatbotState, config: RunnableConfig) -> ChatbotState:
            try:
                result = node_func(state, config)
                result["error"] = None
                return result
            except Exception as e:
                logger.error(f"❌ {node_name} failed: {e}")
                return {
                    **state,
                    "error": str(e),
                    "failed_nodes": state.get("failed_nodes", []) + [node_name]
                }
        return wrapper

    @traceable(name="extract_keywords_node")
    def extract_keywords_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Extract keywords from user query using LLM.

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with extracted keywords

        Note:
            Falls back to empty list if extraction fails
        """
        logger.info(f"🔍 Extracting keywords: {state['query']}")

        try:
            result = self.keyword_chain.invoke({"question": state["query"]}, config=config)

            if isinstance(result, dict):
                keywords = result.get("keywords", [])
            else:
                keywords = []
                logger.warning(f"Keyword extraction result is not dict: {result}")

            logger.info(f"Extracted keywords: {keywords}")

            return {
                **state,
                "keywords": keywords,
                "messages": [{"role": "system", "content": f"Keywords extracted: {keywords}"}]
            }

        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return {
                **state,
                "keywords": [],
                "messages": [{"role": "system", "content": "Keyword extraction failed, using original query"}]
            }

    @traceable(name="generate_query_node")
    def generate_query_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Generate multiple search queries based on conversation history (multi-query retrieval).

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with generated search queries

        Note:
            Generates multiple queries to retrieve comprehensive information
            Falls back to original query if generation fails
        """
        logger.info(f"🔎 Generating search queries from: {state['query']}")

        try:
            # Format chat history for prompt
            chat_history = state.get("chat_history", [])
            if chat_history:
                history_text = "\n".join([
                    f"{'사용자' if msg['role'] == 'user' else '챗봇'}: {msg['content']}"
                    for msg in chat_history[-5:]  # 최근 5개 대화만 사용
                ])
            else:
                history_text = "(이전 대화 없음)"

            result = self.query_chain.invoke({
                "chat_history": history_text,
                "question": state["query"]
            }, config=config)

            if isinstance(result, dict):
                search_queries = result.get("search_queries", [state["query"]])
                # Ensure it's a list
                if not isinstance(search_queries, list):
                    search_queries = [state["query"]]
            else:
                search_queries = [state["query"]]
                logger.warning(f"Query generation result is not dict: {result}")

            logger.info(f"Generated {len(search_queries)} search queries: {search_queries}")

            return {
                **state,
                "search_queries": search_queries,
                "messages": [{"role": "system", "content": f"Search queries generated: {search_queries}"}]
            }

        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return {
                **state,
                "search_queries": [state["query"]],  # Fallback to original query
                "messages": [{"role": "system", "content": "Query generation failed, using original query"}]
            }

    @traceable(name="retrieve_documents_node")
    def retrieve_documents_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Retrieve relevant documents using multiple search queries (multi-query retrieval).

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with retrieved documents from all queries

        Note:
            Searches with each query and combines results, removing duplicates
            Provides more comprehensive context for answering
        """
        search_queries = state.get("search_queries", [state["query"]])
        logger.info(f"📚 Retrieving documents for {len(search_queries)} queries: {search_queries}")

        try:
            all_docs = []
            all_doc_ids = set()  # Track unique documents by content

            # Retrieve documents for each query
            for query in search_queries:
                logger.info(f"🔍 Searching: {query}")
                docs = self.vectorstore.similarity_search(
                    query,
                    k=self.config.top_k
                )

                # Add unique documents only
                for doc in docs:
                    doc_id = f"{doc.metadata.get('id', '')}_{doc.page_content[:50]}"
                    if doc_id not in all_doc_ids:
                        all_docs.append(doc)
                        all_doc_ids.add(doc_id)

                logger.info(f"  → Found {len(docs)} documents")

            matched_topics = list(set([doc.metadata.get('topic', 'Unknown') for doc in all_docs]))
            logger.info(f"✅ Total {len(all_docs)} unique documents retrieved, topics: {matched_topics}")

            return {
                **state,
                "retrieved_docs": all_docs,
                "matched_topics": matched_topics,
                "messages": [{"role": "system", "content": f"Documents retrieved: {len(all_docs)} from {len(search_queries)} queries"}]
            }

        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            return {
                **state,
                "retrieved_docs": [],
                "matched_topics": [],
                "error": str(e),
                "messages": [{"role": "system", "content": f"Document retrieval failed: {e}"}]
            }

    @traceable(name="calculate_confidence_node")
    def calculate_confidence_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Calculate confidence score based on retrieved documents.

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with confidence score

        Note:
            Confidence = min(0.8, num_docs * 0.3)
            Fallback if confidence < 0.3
        """
        docs = state.get("retrieved_docs", [])

        if not docs:
            confidence = 0.0
            should_fallback = True
        else:
            confidence = min(0.8, len(docs) * 0.3)
            should_fallback = confidence < 0.3

        logger.info(f"📊 Confidence: {confidence:.2f}, Fallback: {should_fallback}")

        return {
            **state,
            "confidence": confidence,
            "should_fallback": should_fallback,
            "messages": [{"role": "system", "content": f"Confidence: {confidence:.2f}"}]
        }

    @traceable(name="generate_response_node")
    def generate_response_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Generate response using LLM based on retrieved context and chat history.

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with generated response

        Note:
            Uses context from retrieved documents, chat history, and system prompt
            If use_stronger_model is True, uses GPT-4o instead of GPT-4o-mini for better quality
        """
        # Determine which model to use
        use_stronger = state.get("use_stronger_model", False)

        if use_stronger:
            logger.info("✍️ Generating response with GPT-4o (stronger model)...")
            # Create a temporary stronger LLM instance
            llm_to_use = ChatOpenAI(
                model="gpt-4o",
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=self.config.openai_api_key
            )
        else:
            logger.info("✍️ Generating response with standard model...")
            llm_to_use = self.llm

        try:
            response_prompts = self.prompts.get("chatbot_response", {})
            groom_name = self.wedding_config.get('wedding', {}).get('groom', {}).get('name_kr', 'Groom')
            bride_name = self.wedding_config.get('wedding', {}).get('bride', {}).get('name_kr', 'Bride')

            # Format retrieved documents
            docs = state.get("retrieved_docs", [])
            if not docs:
                context = "(검색된 정보 없음)"
            else:
                formatted = []
                for doc in docs:
                    formatted.append(f"Topic: {doc.metadata.get('topic', 'Unknown')}\nContent: {doc.page_content}")
                context = "\n\n---\n\n".join(formatted)

            # Format chat history
            chat_history = state.get("chat_history", [])
            if chat_history:
                history_text = "\n".join([
                    f"{'사용자' if msg['role'] == 'user' else '챗봇'}: {msg['content']}"
                    for msg in chat_history[-6:]  # 최근 6개 메시지 (3턴)
                ])
            else:
                history_text = "(이전 대화 없음)"

            system_prompt = response_prompts.get("system_template", "Please answer.").format(
                groom_name=groom_name,
                bride_name=bride_name,
                chat_history=history_text,
                context=context
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{question}")
            ])

            chain = prompt | llm_to_use | StrOutputParser()
            response = chain.invoke({"question": state["query"]}, config=config)

            logger.info(f"✅ Response generation completed (model: {'GPT-4o' if use_stronger else 'standard'})")

            return {
                **state,
                "response": response,
                "stronger_model_attempted": use_stronger or state.get("stronger_model_attempted", False),
                "messages": [{"role": "assistant", "content": response}]
            }

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            error_message = self.prompts.get("messages", {}).get("error", "Something went wrong 😅")

            return {
                **state,
                "response": error_message,
                "error": str(e),
                "messages": [{"role": "assistant", "content": error_message}]
            }

    @traceable(name="validate_answer_node")
    def validate_answer_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Validate if generated answer is based on retrieved context.

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with validation result

        Note:
            Checks if response uses only information from retrieved documents
            If invalid, will trigger fallback
        """
        logger.info("🔍 Validating answer against context...")

        try:
            docs = state.get("retrieved_docs", [])
            response = state.get("response", "")

            # Skip validation for fallback-like responses
            if "모르" in response or "정보가 없" in response or "답변할 수 없" in response:
                logger.info("✅ Fallback-style response, validation skipped")
                return {
                    **state,
                    "is_valid_response": True,
                    "validation_reason": "Fallback response",
                    "messages": [{"role": "system", "content": "Validation: Valid (fallback)"}]
                }

            # Format context for validation
            if not docs:
                context = "(검색된 정보 없음)"
            else:
                context = "\n\n".join([doc.page_content for doc in docs])

            # Run validation
            result = self.validation_chain.invoke({
                "context": context,
                "question": state["query"],
                "answer": response
            }, config=config)

            is_valid = result.get("is_valid", False)
            reason = result.get("reason", "No reason provided")

            if is_valid:
                logger.info(f"✅ Answer validation passed: {reason}")
            else:
                logger.warning(f"❌ Answer validation failed: {reason}")

            return {
                **state,
                "is_valid_response": is_valid,
                "validation_reason": reason,
                "messages": [{"role": "system", "content": f"Validation: {'Valid' if is_valid else 'Invalid'} - {reason}"}]
            }

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            # On validation error, assume valid to avoid breaking the flow
            return {
                **state,
                "is_valid_response": True,
                "validation_reason": f"Validation error: {e}",
                "messages": [{"role": "system", "content": "Validation error, assuming valid"}]
            }

    @traceable(name="fallback_retrieval_node")
    def fallback_retrieval_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Fallback retrieval using LLM to extract relevant docs from entire knowledge base.

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with retrieved documents from fallback

        Note:
            Used when vector search fails to find relevant documents
            LLM directly examines entire knowledge base (small dataset)
        """
        logger.info("🔍 Attempting fallback retrieval with LLM...")

        try:
            # Load entire knowledge base as formatted string
            knowledge_base = self._load_all_knowledge_for_fallback()

            if not knowledge_base:
                logger.warning("Knowledge base is empty for fallback")
                return {
                    **state,
                    "messages": [{"role": "system", "content": "Fallback retrieval failed: empty knowledge base"}]
                }

            # Use LLM to extract relevant document IDs
            result = self.fallback_retrieval_chain.invoke({
                "question": state["query"],
                "knowledge_base": knowledge_base
            }, config=config)

            relevant_ids = result.get("relevant_ids", [])
            logger.info(f"📋 LLM found relevant IDs: {relevant_ids}")

            if not relevant_ids:
                logger.info("No relevant documents found by LLM")
                return {
                    **state,
                    "messages": [{"role": "system", "content": "Fallback retrieval: no relevant docs"}]
                }

            # Load full documents for the relevant IDs
            relevant_docs = []
            try:
                with open(self.knowledge_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                items_data = data if isinstance(data, list) else data.get('knowledge_items', [])

                for item in items_data:
                    if item['id'] in relevant_ids:
                        doc = Document(
                            page_content=f"{item['topic']}: {item['content']}",
                            metadata={
                                "id": item['id'],
                                "topic": item['topic']
                            }
                        )
                        relevant_docs.append(doc)

            except Exception as e:
                logger.error(f"Error loading full documents: {e}")

            matched_topics = list(set([doc.metadata.get('topic', 'Unknown') for doc in relevant_docs]))
            logger.info(f"✅ Fallback retrieval found {len(relevant_docs)} documents: {matched_topics}")

            return {
                **state,
                "retrieved_docs": relevant_docs,
                "matched_topics": matched_topics,
                "confidence": min(0.8, len(relevant_docs) * 0.3),  # Recalculate confidence
                "should_fallback": len(relevant_docs) == 0,
                "messages": [{"role": "system", "content": f"Fallback retrieval found {len(relevant_docs)} docs"}]
            }

        except Exception as e:
            logger.error(f"Fallback retrieval failed: {e}")
            return {
                **state,
                "error": str(e),
                "messages": [{"role": "system", "content": f"Fallback retrieval error: {e}"}]
            }

    @traceable(name="fallback_response_node")
    def fallback_response_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Generate fallback response when confidence is low.

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with fallback response

        Note:
            Used when no relevant information is found
        """
        logger.info("⚠️ Using fallback response")

        fallback_message = self.prompts.get("messages", {}).get("fallback", "No information available 😅")

        return {
            **state,
            "response": fallback_message,
            "messages": [{"role": "assistant", "content": fallback_message}]
        }

    def retry_handler_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Handle retry logic with exponential backoff.

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with incremented retry count

        Note:
            Wait time = min(2^retry_count, 10) seconds
        """
        retry_count = state.get("retry_count", 0) + 1

        logger.info(f"🔄 Retry attempt {retry_count}")

        wait_time = min(2 ** retry_count, 10)
        time.sleep(wait_time)

        return {
            **state,
            "retry_count": retry_count,
            "error": None,
            "messages": state.get("messages", []) + [
                {"role": "system", "content": f"Retry attempt {retry_count}"}
            ]
        }

    def check_retry_needed(self, state: ChatbotState) -> str:
        """
        Check if retry is needed based on error state.

        Args:
            state: Current chatbot state

        Returns:
            "continue" if no error
            "retry" if should retry
            "fail" if max retries reached
        """
        if not state.get("error"):
            return "continue"

        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)

        if retry_count >= max_retries:
            logger.warning(f"⚠️ Max retries reached ({retry_count}/{max_retries})")
            return "fail"

        return "retry"

    def route_after_retry(self, state: ChatbotState) -> str:
        """
        Route to appropriate node after retry.

        Args:
            state: Current chatbot state

        Returns:
            Node name to route to, or "give_up" if no failed nodes
        """
        failed_nodes = state.get("failed_nodes", [])

        if failed_nodes:
            return failed_nodes[-1]

        return "give_up"

    def should_use_fallback_retrieval(self, state: ChatbotState) -> str:
        """
        Determine whether to use fallback retrieval based on confidence.

        Args:
            state: Current chatbot state

        Returns:
            "fallback_retrieval" if should try LLM-based retrieval
            "generate" if should generate response normally
        """
        # If confidence is low, try fallback retrieval first
        if state.get("should_fallback", False):
            return "fallback_retrieval"
        return "generate"

    def route_after_fallback_retrieval(self, state: ChatbotState) -> str:
        """
        Route after fallback retrieval based on results.

        Args:
            state: Current chatbot state

        Returns:
            "generate" if documents were found
            "fallback" if no documents found
        """
        docs = state.get("retrieved_docs", [])
        if docs and len(docs) > 0:
            logger.info(f"✅ Fallback retrieval succeeded with {len(docs)} docs, proceeding to generate")
            return "generate"
        else:
            logger.info("❌ Fallback retrieval found no docs, using fallback response")
            return "fallback"

    def check_answer_validity(self, state: ChatbotState) -> str:
        """
        Check if generated answer is valid based on validation result.

        Args:
            state: Current chatbot state

        Returns:
            "valid" if answer is valid
            "retry_with_stronger_model" if should retry with GPT-4o
            "invalid" if answer needs fallback (after stronger model already tried)
        """
        if state.get("is_valid_response", True):
            return "valid"

        # If validation failed and we haven't tried stronger model yet, retry with GPT-4o
        if not state.get("stronger_model_attempted", False):
            logger.info("⚡ Validation failed, will retry with GPT-4o for better quality")
            return "retry_with_stronger_model"

        # If we already tried stronger model and still failed, use fallback
        logger.warning("⚠️ Validation failed even with GPT-4o, using fallback response")
        return "invalid"

    def prepare_stronger_model_retry_node(self, state: ChatbotState, config: RunnableConfig) -> ChatbotState:
        """
        Prepare state for retry with stronger model (GPT-4o).

        Args:
            state: Current chatbot state
            config: Runnable configuration

        Returns:
            Updated state with use_stronger_model flag set to True
        """
        logger.info("🔄 Preparing retry with GPT-4o (stronger model)")

        return {
            **state,
            "use_stronger_model": True,
            "is_valid_response": True,  # Reset validation flag
            "messages": state.get("messages", []) + [
                {"role": "system", "content": "Retrying with GPT-4o for better quality"}
            ]
        }

    def _create_graph(self) -> StateGraph:
        """
        Create LangGraph workflow with nodes and edges.

        Returns:
            StateGraph instance with complete workflow

        Note:
            Graph structure:
            generate_query → extract_keywords → retrieve_documents → calculate_confidence
            → (fallback_retrieval? → generate_response → validate_answer | fallback_response) → END

            If vector search fails (low confidence), try LLM-based fallback retrieval
            Validation ensures response is based on context
            If validation fails, retry with GPT-4o for better quality
            Retry logic is integrated at each major node
        """
        workflow = StateGraph(ChatbotState)

        # Add nodes
        workflow.add_node("generate_query", self._with_retry(self.generate_query_node, "generate_query"))
        workflow.add_node("extract_keywords", self._with_retry(self.extract_keywords_node, "extract_keywords"))
        workflow.add_node("retrieve_documents", self._with_retry(self.retrieve_documents_node, "retrieve_documents"))
        workflow.add_node("calculate_confidence", self.calculate_confidence_node)
        workflow.add_node("fallback_retrieval", self._with_retry(self.fallback_retrieval_node, "fallback_retrieval"))
        workflow.add_node("generate_response", self._with_retry(self.generate_response_node, "generate_response"))
        workflow.add_node("validate_answer", self.validate_answer_node)
        workflow.add_node("prepare_stronger_model", self.prepare_stronger_model_retry_node)
        workflow.add_node("fallback_response", self.fallback_response_node)
        workflow.add_node("retry_handler", self.retry_handler_node)

        # Define edges
        workflow.set_entry_point("generate_query")

        workflow.add_conditional_edges(
            "generate_query",
            self.check_retry_needed,
            {
                "continue": "extract_keywords",
                "retry": "retry_handler",
                "fail": "fallback_response"
            }
        )

        workflow.add_conditional_edges(
            "extract_keywords",
            self.check_retry_needed,
            {
                "continue": "retrieve_documents",
                "retry": "retry_handler",
                "fail": "fallback_response"
            }
        )

        workflow.add_conditional_edges(
            "retrieve_documents",
            self.check_retry_needed,
            {
                "continue": "calculate_confidence",
                "retry": "retry_handler",
                "fail": "fallback_response"
            }
        )

        workflow.add_conditional_edges(
            "calculate_confidence",
            self.should_use_fallback_retrieval,
            {
                "generate": "generate_response",
                "fallback_retrieval": "fallback_retrieval"
            }
        )

        workflow.add_conditional_edges(
            "fallback_retrieval",
            self.route_after_fallback_retrieval,
            {
                "generate": "generate_response",
                "fallback": "fallback_response"
            }
        )

        workflow.add_conditional_edges(
            "generate_response",
            self.check_retry_needed,
            {
                "continue": "validate_answer",  # Go to validation instead of END
                "retry": "retry_handler",
                "fail": "fallback_response"
            }
        )

        workflow.add_conditional_edges(
            "validate_answer",
            self.check_answer_validity,
            {
                "valid": END,  # Valid answer → done
                "retry_with_stronger_model": "prepare_stronger_model",  # Retry with GPT-4o
                "invalid": "fallback_response"  # Invalid answer after GPT-4o → use fallback
            }
        )

        # After preparing stronger model, go back to generate_response
        workflow.add_edge("prepare_stronger_model", "generate_response")

        workflow.add_conditional_edges(
            "retry_handler",
            self.route_after_retry,
            {
                "generate_query": "generate_query",
                "extract_keywords": "extract_keywords",
                "retrieve_documents": "retrieve_documents",
                "fallback_retrieval": "fallback_retrieval",
                "generate_response": "generate_response",
                "give_up": "fallback_response"
            }
        )

        workflow.add_edge("fallback_response", END)

        return workflow

    @traceable(name="chat")
    async def get_response(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        thread_id: str = "default",
        max_retries: int = 3,
        recursion_limit: int = 25,
        timeout: float = 60.0
    ) -> Dict:
        """
        Generate response for user query with multi-turn conversation support.

        Main interface for the chatbot. Executes the complete workflow
        including query generation, keyword extraction, document retrieval, and response generation.

        Args:
            query: User question
            chat_history: Previous conversation history.
                List of dicts with 'role' and 'content' keys.
                Defaults to None (empty history).
            thread_id: Conversation thread ID for session management.
                Defaults to "default".
            max_retries: Maximum number of retry attempts.
                Defaults to 3.
            recursion_limit: Maximum recursion depth to prevent infinite loops.
                Defaults to 25.
            timeout: Maximum execution time in seconds.
                Defaults to 60.0.

        Returns:
            Dictionary containing:
                - success (bool): Whether response generation succeeded
                - response (str): Generated response text
                - keywords (List[str]): Extracted keywords
                - matched_topics (List[str]): Matched topics
                - confidence (float): Response confidence score
                - search_query (str): Generated search query
                - error (Optional[str]): Error message if failed
                - retry_count (int): Number of retries performed

        Raises:
            RecursionError: If recursion limit is exceeded
            asyncio.TimeoutError: If timeout is exceeded
            Exception: For other unexpected errors

        Example:
            >>> chatbot = WeddingChatbotGraph()
            >>> result = await chatbot.get_response(
            ...     query="How did you meet?",
            ...     chat_history=[],
            ...     max_retries=3,
            ...     timeout=30.0
            ... )
            >>> print(result['response'])
        """
        logger.info(f"🔍 Processing query: {query}")

        try:
            initial_state = {
                "query": query,
                "search_queries": [query],  # Initialize with original query as list
                "chat_history": chat_history or [],
                "keywords": [],
                "retrieved_docs": [],
                "matched_topics": [],
                "confidence": 0.0,
                "should_fallback": False,
                "response": "",
                "is_valid_response": True,  # Default to valid
                "validation_reason": "",
                "error": None,
                "messages": [],
                "retry_count": 0,
                "max_retries": max_retries,
                "failed_nodes": [],
                "use_stronger_model": False,  # Start with standard model
                "stronger_model_attempted": False  # Track if GPT-4o has been tried
            }

            config = {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": recursion_limit
            }

            try:
                final_state = await asyncio.wait_for(
                    self.app.ainvoke(initial_state, config=config),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"⏰ Timeout ({timeout}s)")
                raise Exception(f"Response generation exceeded {timeout}s")

            result = {
                "success": not final_state.get("error") and final_state.get("response"),
                "response": final_state.get("response", ""),
                "keywords": final_state.get("keywords", []),
                "matched_topics": final_state.get("matched_topics", []),
                "confidence": final_state.get("confidence", 0.0),
                "search_queries": final_state.get("search_queries", [query]),
                "error": final_state.get("error"),
                "retry_count": final_state.get("retry_count", 0)
            }

            if result["retry_count"] > 0:
                logger.warning(f"⚠️ Completed after {result['retry_count']} retries")

            logger.info(f"✅ Response completed (confidence: {result['confidence']:.2f})")
            return result

        except RecursionError as e:
            logger.error(f"🔄 Infinite loop detected: {e}")
            error_message = self.prompts.get("messages", {}).get("error", "Something went wrong 😅")

            return {
                "success": False,
                "response": error_message,
                "error": "Maximum recursion depth exceeded"
            }

        except Exception as e:
            logger.error(f"❌ Response generation failed: {str(e)}", exc_info=True)
            error_message = self.prompts.get("messages", {}).get("error", "Something went wrong 😅")

            return {
                "success": False,
                "response": error_message,
                "error": str(e)
            }


# ==================== Global Instance Management ====================
_chatbot_instance = None


def get_chatbot() -> WeddingChatbotGraph:
    """
    Get singleton chatbot instance.

    Returns:
        WeddingChatbotGraph instance

    Note:
        Creates new instance if one doesn't exist
    """
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = WeddingChatbotGraph()
    return _chatbot_instance


def initialize_chatbot(
    config_path: str = "config/config.json",
    knowledge_path: str = "config/couple_knowledge.json"
) -> WeddingChatbotGraph:
    """
    Initialize chatbot with custom configuration.

    Args:
        config_path: Path to wedding configuration file
        knowledge_path: Path to couple knowledge base file

    Returns:
        Initialized WeddingChatbotGraph instance
    """
    global _chatbot_instance
    _chatbot_instance = WeddingChatbotGraph(config_path, knowledge_path)
    return _chatbot_instance


def setup_langsmith() -> None:
    """
    Setup LangSmith tracing if available.

    Configures LangSmith environment variables for tracing
    if LANGCHAIN_API_KEY is set.

    Note:
        Tracing is optional and will be disabled if LangSmith
        is not installed or API key is not provided.
    """
    if LANGSMITH_AVAILABLE and os.getenv("LANGCHAIN_API_KEY"):
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "wedding-chatbot-graph")
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
        logger.info("🔍 LangSmith tracing enabled.")
    else:
        logger.info("LangSmith tracing disabled.")


# Initialize LangSmith on module import
setup_langsmith()