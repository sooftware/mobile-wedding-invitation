# 🤖 AI Chatbot Guide

**English** | [한국어](./CHATBOT.ko.md)

This guide explains how to configure and customize the AI chatbot feature of the wedding invitation.

## 📋 Table of Contents

- [Overview](#overview)
- [How the Chatbot Works](#how-the-chatbot-works)
- [Writing the Knowledge Base](#writing-the-knowledge-base)
- [Customizing Prompts](#customizing-prompts)
- [Advanced Settings](#advanced-settings)
- [Troubleshooting](#troubleshooting)

## Overview

The AI chatbot is built on LangGraph and LangChain, using RAG (Retrieval-Augmented Generation) to answer questions about the bride and groom.

### Key Features

- 📚 **Knowledge Base Search**: Semantic search using vector database
- 🔄 **Auto Retry**: Retry with exponential backoff on failure
- ⏱️ **Timeout Handling**: Prevent infinite loops
- 📊 **LangSmith Tracing**: (Optional) Monitor conversation flow

### Chatbot Workflow

```
User Question
    ↓
Keyword Extraction (LLM)
    ↓
Document Search (Vector DB)
    ↓
Confidence Calculation
    ↓
Generate Response (LLM) or Fallback
    ↓
Response to User
```

## How the Chatbot Works

### 1. Keyword Extraction
Extract key keywords from user's question using LLM.

```python
"How did you two meet?" 
→ ["meet", "first meeting", "beginning"]
```

### 2. Vector Search
Search related documents in Chroma vector database using extracted keywords.

### 3. Confidence Calculation
Calculate confidence based on number and relevance of retrieved documents.

```python
confidence = min(0.8, num_docs * 0.3)
should_fallback = confidence < 0.3
```

### 4. Response Generation
- High confidence: Generate response based on retrieved context
- Low confidence: Return predefined fallback message

## Writing the Knowledge Base

The knowledge base is written in JSON format in `config/couple_knowledge.json`.

### Basic Structure

```json
[
  {
    "id": "unique_identifier",
    "topic": "Topic Name",
    "content": "Actual response content"
  }
]
```

### Writing Guide

#### 1. Essential Information

**First Meeting**
```json
{
  "id": "first_meeting",
  "topic": "First Meeting",
  "content": "We first met in 2018 at university through a 'Mobile Programming' class."
}
```

**Dating Anniversary**
```json
{
  "id": "start_date",
  "topic": "Dating Anniversary",
  "content": "We started dating on May 5th, 2019 (Children's Day)! 💕"
}
```

**Proposal**
```json
{
  "id": "proposal",
  "topic": "Proposal",
  "content": "The groom proposed in February 2025 at the bride's house during dinner. The groom was so nervous he made many mistakes, and the bride was completely surprised."
}
```

**Honeymoon**
```json
{
  "id": "honeymoon",
  "topic": "Honeymoon",
  "content": "We're planning to travel to Dubai, Maldives, and Singapore! We leave the day after the wedding. ✈️"
}
```

#### 2. Personal Information

**Hobbies**
```json
{
  "id": "hobbies_groom",
  "topic": "Groom's Hobbies",
  "content": "The groom enjoys coding, reading, and watching movies."
},
{
  "id": "hobbies_bride",
  "topic": "Bride's Hobbies",
  "content": "The bride loves cooking and baking, and enjoys traveling."
}
```

**Occupations**
```json
{
  "id": "job_groom",
  "topic": "Groom's Job",
  "content": "The groom is an AI engineer working at a startup called Tunip."
},
{
  "id": "job_bride",
  "topic": "Bride's Job",
  "content": "The bride works at Cheil Worldwide in data analysis and marketing strategy."
}
```

#### 3. Wedding Information

**Wedding Venue**
```json
{
  "id": "wedding_venue",
  "topic": "Wedding Venue",
  "content": "The wedding will be held on May 17th, 2026 at 2 PM at Lacitta Theater. Address: 1st Floor, 16 Maeheon-ro, Seocho-gu, Seoul."
}
```

**Dress Code**
```json
{
  "id": "dress_code",
  "topic": "Dress Code",
  "content": "Please come in comfortable and neat attire. There's no specific dress code!"
}
```

#### 4. Fun Episodes

**First Date**
```json
{
  "id": "first_date",
  "topic": "First Date",
  "content": "After midterms in 2019, we went to watch the newly released Avengers movie together! 💕"
}
```

**Memorable Moment**
```json
{
  "id": "memorable_moment",
  "topic": "Memorable Moment",
  "content": "Last year's Paris trip was the most memorable. The photos we took in front of the Eiffel Tower are now in our wedding invitation!"
}
```

### Writing Tips

#### ✅ Good Examples

**Natural Tone**
```json
{
  "content": "We first met at university in 2018. We were in the same class and became friends through a team project!"
}
```

**Using Emojis**
```json
{
  "content": "We're going to Dubai, Maldives, and Singapore for our honeymoon! ✈️ So excited!"
}
```

**Specific Information**
```json
{
  "content": "We started dating on May 5th, 2019 (Children's Day). It's been 7 years already!"
}
```

#### ❌ Examples to Avoid

**Too Formal**
```json
{
  "content": "Met in 2018. Became acquainted through university class."
}
```

**Unclear Information**
```json
{
  "content": "We met sometime. Don't remember exactly."
}
```

**Too Long**
```json
{
  "content": "We took the Mobile Programming class in the first semester of 2018 at university and we were assigned to the same team project and that's when we started getting closer and later we got even closer eating meals together and watching movies and eventually started dating."
}
```

### Complete Example

```json
[
  {
    "id": "first_meeting",
    "topic": "First Meeting",
    "content": "We first met in 2018 when the bride was 21 and the groom was 24, in a 'Mobile Programming' class at university."
  },
  {
    "id": "first_date",
    "topic": "First Date",
    "content": "Our first date was in 2019 after midterms when we went to watch the newly released Avengers movie! 💕"
  },
  {
    "id": "start_date",
    "topic": "Dating Anniversary",
    "content": "We started dating on May 5th, 2019 (Children's Day)!"
  },
  {
    "id": "proposal",
    "topic": "Proposal",
    "content": "In February 2025, the groom proposed during dinner at the bride's house. The groom was so nervous he made several mistakes, and the bride was completely surprised."
  },
  {
    "id": "honeymoon",
    "topic": "Honeymoon",
    "content": "We're going to Dubai, Maldives, and Singapore - three countries! We leave the day after the wedding! ✈️"
  },
  {
    "id": "age",
    "topic": "Age",
    "content": "The groom was born in 1995 and the bride in 1998. (As of 2026, groom is 32 and bride is 29 in Korean age)"
  },
  {
    "id": "job_groom",
    "topic": "Groom's Job",
    "content": "The groom is an AI engineer. He's currently a co-founder at a startup called 'Tunip'."
  },
  {
    "id": "job_bride",
    "topic": "Bride's Job",
    "content": "The bride works at 'Cheil Worldwide' in data analysis and marketing strategy."
  },
  {
    "id": "wedding_venue",
    "topic": "Wedding Venue",
    "content": "The wedding will be held on May 17th, 2026 at 2 PM at Lacitta Theater. Address: 1st Floor, 16 Maeheon-ro, Seocho-gu, Seoul."
  }
]
```

## Customizing Prompts

You can customize the chatbot's tone and personality in the `app/chatbot/prompts.json` file.

### Prompt Structure

```json
{
  "keyword_extraction": {
    "system": "Keyword extraction system prompt",
    "user_template": "User message template"
  },
  "chatbot_response": {
    "system_template": "Chatbot response system prompt",
    "user_template": "User question template"
  },
  "messages": {
    "fallback": "Message when no information available",
    "error": "Message on error"
  }
}
```

### Personality Settings

Modify the `chatbot_response.system_template` section to change the chatbot's personality.

#### Example 1: Friendly and Cute (Default)
```json
{
  "system_template": "You are an AI assistant for {groom_name} and {bride_name}'s wedding.\n\nPersonality:\n- Use friendly and cute language\n- Use emojis appropriately\n- Be polite but not overly formal\n\nResponse Guidelines:\n- Answer accurately based on provided information\n- Keep responses to 2-3 sentences\n\nRelated Information:\n{context}"
}
```

#### Example 2: Formal and Elegant
```json
{
  "system_template": "You are an AI assistant guiding {groom_name} and {bride_name}'s wedding.\n\nPersonality:\n- Use formal and elegant language\n- Maintain polite and respectful tone\n- Answer with congratulatory and respectful sentiments\n\nResponse Guidelines:\n- Provide clear and accurate information\n- Write concise yet warm responses\n\nRelated Information:\n{context}"
}
```

#### Example 3: Fun and Humorous
```json
{
  "system_template": "You are {groom_name} and {bride_name}'s fun wedding guide! 😄\n\nPersonality:\n- Use humorous and fun language\n- Use lots of emojis for liveliness\n- Chat like a friend, comfortably and fun\n\nResponse Guidelines:\n- Information accurately, expression fun!\n- Mix in appropriate jokes and humor\n- Make guests enjoy reading\n\nRelated Information:\n{context}"
}
```

### Customizing Fallback Messages

Modify messages displayed when information is unavailable.

```json
{
  "messages": {
    "fallback": "Sorry 😅 I don't have information about that question 😢 Feel free to ask about something else!",
    "error": "Oops! Something went wrong 😅 Please try again in a moment!",
    "thinking": "Thinking... 🤔"
  }
}
```

### Setting Suggested Questions

Set suggested questions in the `config.json` file's `content.chatbot.welcome.suggested_questions` section.

```json
{
  "content": {
    "chatbot": {
      "welcome": {
        "suggested_questions": [
          "How did you two meet?",
          "Where was your first date?",
          "Where are you going for your honeymoon?",
          "What are your hobbies?"
        ]
      }
    }
  }
}
```

## Advanced Settings

### Environment Variable Configuration

You can adjust chatbot-related settings in the `.env` file.

```bash
# OpenAI Settings
OPENAI_API_KEY=your_api_key
CHAT_MODEL=gpt-4o-mini              # Or gpt-4, gpt-3.5-turbo
CHAT_TEMPERATURE=0.7                # 0.0 (precise) ~ 1.0 (creative)
MAX_TOKENS=300                      # Max response length

# Embedding Settings
EMBEDDING_MODEL=text-embedding-3-small  # Or text-embedding-3-large

# Search Settings
TOP_K_RESULTS=3                     # Number of documents to search

# LangSmith Tracing (optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=wedding-chatbot
```

### Model Selection Guide

#### GPT-4o-mini (Default, Recommended)
- **Pros**: Fast and cheap
- **Cons**: May be slightly insufficient for complex questions
- **Cost**: $0.15 / 1M tokens (input)
- **Recommended**: Sufficient for most cases

#### GPT-4
- **Pros**: Most accurate and natural responses
- **Cons**: Slow and expensive
- **Cost**: $5.00 / 1M tokens (input)
- **Recommended**: When premium experience desired

#### GPT-3.5-turbo
- **Pros**: Very fast and cheap
- **Cons**: Response quality may be lower
- **Cost**: $0.50 / 1M tokens (input)
- **Recommended**: When budget is very limited

### Temperature Settings

```bash
CHAT_TEMPERATURE=0.7  # Default
```

- **0.0-0.3**: Very accurate and consistent responses (recommended)
- **0.4-0.6**: Accurate with some creativity
- **0.7-1.0**: Creative but may be inconsistent

### Search Document Count (TOP_K)

```bash
TOP_K_RESULTS=3  # Default
```

- **1-2**: Fast but may lack information
- **3-5**: Good balance (recommended)
- **6-10**: Slow but more context

### LangSmith Tracing Setup

LangSmith allows detailed monitoring of chatbot operations.

1. Sign up at [LangSmith](https://smith.langchain.com/)
2. Generate API key
3. Add to `.env` file

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=my-wedding-chatbot
```

Information visible on LangSmith dashboard:
- Complete flow of each conversation
- LLM call count and cost
- Retrieved document content
- Response time analysis

## Troubleshooting

### Chatbot Not Responding

**Cause 1: OpenAI API Key Error**
```bash
# Check .env file
OPENAI_API_KEY=sk-...  # Verify correct API key
```

**Cause 2: Network Error**
```bash
# Check logs
python main.py
# Check error messages in console
```

**Cause 3: Empty Knowledge Base**
```json
// Check config/couple_knowledge.json file
// Verify at least 5-10 items exist
```

### Chatbot Giving Wrong Answers

**Solution 1: Improve Knowledge Base**
- Write more specific and clear content
- Include related keywords
- Organize duplicate information

**Solution 2: Lower Temperature**
```bash
CHAT_TEMPERATURE=0.3  # More accurate answers
```

**Solution 3: Improve Prompts**
```json
{
  "system_template": "... Always answer based only on provided information. Do not guess or make up information. ..."
}
```

For details, see [Chatbot Guide](./CHATBOT.md).

### Chatbot Response Too Slow

**Solution 1: Change Model**
```bash
CHAT_MODEL=gpt-3.5-turbo  # Faster model
```

**Solution 2: Reduce Document Count**
```bash
TOP_K_RESULTS=2  # Reduce search documents
```

**Solution 3: Reduce Max Tokens**
```bash
MAX_TOKENS=200  # Shorter responses
```

### Chatbot Costs Too Much

**Solution 1: Use Cheaper Model**
```bash
CHAT_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
```

**Solution 2: Limit Max Tokens**
```bash
MAX_TOKENS=200  # Cost reduction
```

**Solution 3: Use Caching**
- Cache responses to frequently asked questions
- (Advanced) Integrate cache server like Redis

### Fallback Message Appears Too Often

**Solution 1: Expand Knowledge Base**
- Add information on more diverse topics
- Add multiple entries for same topic with different expressions

**Solution 2: Lower Confidence Threshold**
```python
# Modify app/chatbot/chatbot.py
should_fallback = confidence < 0.2  # Change from 0.3 to 0.2
```

**Solution 3: Increase TOP_K**
```bash
TOP_K_RESULTS=5  # Search more documents
```

## Testing and Improvement

### 1. Local Testing

```bash
# Start server
python main.py

# Test in browser
http://localhost:8000
```

### 2. Test Various Questions

Test with questions like:
- "How did you two meet?"
- "Where was your first date?"
- "What are the groom's hobbies?"
- "When is the wedding?"
- "Where are you going for honeymoon?"

### 3. Collect Feedback

Improve based on actual guest feedback:

1. Identify frequently asked questions
2. Supplement insufficient answers
3. Adjust tone and emoji usage

## Next Steps

- [Configuration Guide](./CONFIGURATION.md) - Overall invitation setup
- [Customization Guide](./CUSTOMIZATION.md) - Design and feature customization
- [FAQ](./FAQ.md) - Frequently Asked Questions

## Need Help?

- 📧 [Email](mailto:your.email@example.com)
- 💬 [Discord Community](https://discord.gg/your-server)
- 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)