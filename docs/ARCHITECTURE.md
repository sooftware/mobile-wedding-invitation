# 🏗️ System Architecture

**English** | [한국어](./ARCHITECTURE.ko.md)

This document explains the system architecture and design decisions of the AI wedding invitation project.

## 📋 Table of Contents

- [Overall Architecture](#overall-architecture)
- [Backend Structure](#backend-structure)
- [AI Chatbot Architecture](#ai-chatbot-architecture)
- [Database Design](#database-design)
- [Frontend Structure](#frontend-structure)
- [Deployment Architecture](#deployment-architecture)
- [Security Design](#security-design)
- [Performance Optimization](#performance-optimization)

## Overall Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Users (Guests)                       │
│                    Browser / Mobile Device                   │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Railway Platform                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                      │  │
│  │  ┌────────────┐  ┌──────────────┐  ┌─────────────┐ │  │
│  │  │   Static   │  │   Templates  │  │     API     │ │  │
│  │  │   Files    │  │   (Jinja2)   │  │  Endpoints  │ │  │
│  │  └────────────┘  └──────────────┘  └─────────────┘ │  │
│  │                                                       │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │          LangGraph AI Chatbot                  │ │  │
│  │  │  ┌──────────┐  ┌───────────┐  ┌────────────┐ │ │  │
│  │  │  │ Keyword  │→ │  Vector   │→ │  Response  │ │ │  │
│  │  │  │Extraction│  │  Search   │  │ Generation │ │ │  │
│  │  │  └──────────┘  └───────────┘  └────────────┘ │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │                          │                           │  │
│  │                          ▼                           │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │              Session Management                 │ │  │
│  │  │          (Admin Auth / CSRF Protection)         │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └───────────────────────┬──────────────────────────────┘  │
│                          │                                  │
│                          ▼                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │Guestbook │  │   RSVP   │  │  Admin Sessions  │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │  OpenAI API  │  │  Chroma DB   │  │  LangSmith (opt) │ │
│  │   (GPT-4)    │  │   (Vector)   │  │    (Tracing)     │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

**1. Web Server (FastAPI)**
- Asynchronous request handling
- RESTful API provision
- Static file serving
- Template rendering

**2. AI Chatbot (LangGraph)**
- State management workflow
- RAG-based knowledge retrieval
- Retry logic

**3. Database (PostgreSQL/SQLite)**
- Guestbook storage
- RSVP management
- Session storage

**4. External Services**
- OpenAI: LLM inference
- Chroma: Vector search
- LangSmith: Tracing (optional)

## Backend Structure

### Directory Structure

```
app/
├── chatbot/              # AI chatbot module
│   ├── __init__.py
│   ├── chatbot.py       # LangGraph chatbot implementation
│   ├── schemas.py       # Pydantic schemas
│   └── prompts.json     # Prompt templates
├── database/            # Database layer
│   ├── __init__.py
│   └── queries.py       # SQL query functions
├── admin/               # Admin features
│   ├── __init__.py
│   └── auth.py          # Authentication & sessions
└── __init__.py
```

### Layer Architecture

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │
│   (FastAPI Routes / Templates)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Business Logic Layer            │
│  (Chatbot / Admin Auth / Validation)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│          Data Access Layer              │
│        (Database Queries)               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│           Database Layer                │
│     (PostgreSQL / SQLite)               │
└─────────────────────────────────────────┘
```

### Main Endpoints

**Public API:**
```python
GET  /                    # Main page
GET  /guestbook          # Guestbook page
POST /guestbook          # Create guestbook entry
PUT  /guestbook/{id}     # Update guestbook entry
DELETE /guestbook/{id}   # Delete guestbook entry
GET  /api/guestbook      # Get guestbook entries
POST /rsvp               # Submit RSVP
POST /chat               # AI chatbot conversation
```

**Admin API:**
```python
GET  /admin/login        # Login page
POST /admin/login        # Login processing
GET  /admin              # Admin dashboard
GET  /admin/guestbook    # Guestbook management
GET  /admin/rsvp         # RSVP management
GET  /admin/rsvp/export  # Export RSVP CSV
POST /admin/logout       # Logout
```

## AI Chatbot Architecture

### LangGraph Workflow

```
User Input
    │
    ▼
┌────────────────────────┐
│  Extract Keywords Node │
│  (Extract key keywords │
│   using LLM)           │
│  → ["honeymoon", ...]  │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Document Retrieval    │
│  Node                  │
│  - Chroma vector search│
│  - Similarity ranking  │
└───────────┬────────────┘
            │
            ▼
┌────────────────────────┐
│  Confidence Check Node │
│  - Check # of results  │
│  - Calculate confidence│
└───────────┬────────────┘
            │
      ┌─────┴─────┐
      │           │
   High conf   Low conf
      │           │
      ▼           ▼
┌────────────┐ ┌────────────┐
│ Generate   │ │  Fallback  │
│ Response   │ │  Message   │
│  (LLM)     │ │            │
└─────┬──────┘ └──────┬─────┘
      │               │
      └───────┬───────┘
              ▼
         Final Response
```

### State Management

```python
class ChatbotState(TypedDict):
    """Chatbot state"""
    question: str              # User question
    keywords: List[str]        # Extracted keywords
    documents: List[Document]  # Retrieved documents
    confidence: float          # Confidence score
    should_fallback: bool      # Whether to fallback
    response: str              # Final response
    iterations: int            # Iteration count (prevent infinite loop)
```

### RAG (Retrieval-Augmented Generation)

**1. Building Knowledge Base**
```python
# couple_knowledge.json → Chroma Vector Store
knowledge = load_json("config/couple_knowledge.json")
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(
    documents=knowledge,
    embedding=embeddings
)
```

**2. Retrieval**
```python
# Keyword-based vector search
results = vectorstore.similarity_search(
    query=keywords,
    k=TOP_K_RESULTS  # Default: 3
)
```

**3. Generation**
```python
# Generate response with retrieved context
response = llm.invoke(
    f"Context: {context}\nQuestion: {question}"
)
```

### Retry and Error Handling

```python
# Exponential Backoff
max_retries = 3
for attempt in range(max_retries):
    try:
        response = llm.invoke(prompt)
        break
    except Exception as e:
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            await asyncio.sleep(wait_time)
        else:
            return fallback_message
```

## Database Design

### ERD (Entity-Relationship Diagram)

```
┌─────────────────────┐
│     guestbook       │
├─────────────────────┤
│ id (PK)             │
│ guest_name          │
│ message             │
│ password_hash       │
│ created_at          │
│ updated_at          │
└─────────────────────┘

┌─────────────────────┐
│        rsvp         │
├─────────────────────┤
│ id (PK)             │
│ guest_name          │
│ which_side          │ ← Groom/Bride side
│ can_attend          │ ← Attend/Not attend
│ phone_last_digits   │ ← Distinguish same names
│ created_at          │
└─────────────────────┘

┌─────────────────────┐
│   admin_sessions    │
├─────────────────────┤
│ session_id (PK)     │
│ username            │
│ created_at          │
│ expires_at          │
└─────────────────────┘
```

### Table Details

**guestbook table**
```sql
CREATE TABLE guestbook (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT NOT NULL,
    message TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**rsvp table**
```sql
CREATE TABLE rsvp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_name TEXT NOT NULL,
    which_side TEXT NOT NULL,  -- 'Groom' or 'Bride'
    can_attend TEXT NOT NULL,  -- 'Attending' or 'Not Attending'
    phone_last_digits TEXT,    -- Optional, distinguish same names
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**admin_sessions table**
```sql
CREATE TABLE admin_sessions (
    session_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);
```

### Indexes

```sql
-- Indexes for performance optimization
CREATE INDEX idx_guestbook_created_at ON guestbook(created_at DESC);
CREATE INDEX idx_rsvp_which_side ON rsvp(which_side);
CREATE INDEX idx_rsvp_can_attend ON rsvp(can_attend);
CREATE INDEX idx_admin_sessions_expires_at ON admin_sessions(expires_at);
```

## Frontend Structure

### File Structure

```
static/
├── css/
│   ├── variables.css    # CSS variables (colors, fonts)
│   ├── reset.css        # CSS reset
│   ├── main.css         # Main styles
│   ├── animations.css   # Animations
│   └── admin.css        # Admin page styles
├── js/
│   ├── main.js          # Main logic
│   ├── chatbot.js       # Chatbot UI
│   ├── guestbook.js     # Guestbook UI
│   ├── rsvp.js          # RSVP UI
│   ├── animations.js    # Petal animations
│   └── admin.js         # Admin features
└── assets/
    ├── images/          # Image files
    ├── audio/           # Background music
    └── icons/           # Icons

templates/
├── index.html           # Main page
├── guestbook.html       # Guestbook write page
└── admin.html           # Admin dashboard
```

### JavaScript Modules

**main.js** - Page initialization
```javascript
// D-Day calculation
// Background music control
// Scroll animations
// Sharing functionality
```

**chatbot.js** - Chatbot interface
```javascript
// Message sending
// Response rendering
// Suggested questions handling
```

**guestbook.js** - Guestbook CRUD
```javascript
// Get guestbook entries
// Create/update/delete messages
// Pagination
```

**animations.js** - Petal animations
```javascript
// Natural falling physics
// Performance optimization
// Responsive handling
```

### CSS Architecture

**CSS Variables (Design Tokens)**
```css
:root {
  /* Colors */
  --primary-color: #B59493;
  --background-color: #FFFFFF;
  --text-primary: #333333;
  
  /* Typography */
  --font-family-main: 'Noto Sans KR', sans-serif;
  --font-size-base: 16px;
  
  /* Spacing */
  --spacing-sm: 10px;
  --spacing-md: 20px;
  --spacing-lg: 40px;
  
  /* Layout */
  --max-width: 800px;
  --section-spacing: 80px;
}
```

**BEM Methodology**
```css
/* Block */
.chatbot { }

/* Element */
.chatbot__message { }
.chatbot__input { }

/* Modifier */
.chatbot__message--user { }
.chatbot__message--bot { }
```

## Deployment Architecture

### Railway Deployment

```
┌─────────────────────────────────────────────┐
│           GitHub Repository                  │
│  (Push to main → auto deploy)               │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Railway Build Process                │
│  1. Detect Python                            │
│  2. Install dependencies (requirements.txt)  │
│  3. Run main.py                              │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│        Railway Runtime Environment           │
│  ┌──────────────────────────────────────┐  │
│  │  FastAPI Application (uvicorn)       │  │
│  │  Port: $PORT (auto-assigned)         │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │  PostgreSQL Database                 │  │
│  │  DATABASE_URL (auto-configured)      │  │
│  └──────────────────────────────────────┘  │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│         Railway Edge Network                 │
│  - Auto HTTPS                                │
│  - Custom domain support                     │
│  - DDoS protection                           │
└─────────────────────────────────────────────┘
```

### Environment Separation

**Development (Local)**
```bash
DATABASE_URL=sqlite:///wedding.db
DEBUG=true
LOG_LEVEL=debug
```

**Production (Railway)**
```bash
DATABASE_URL=postgresql://... (auto-configured)
DEBUG=false
LOG_LEVEL=info
```

## Security Design

### Authentication and Authorization

**Admin Authentication Flow**
```
1. User accesses /admin/login
2. Enter username + password
3. Server verifies password_hash
4. Create session on success
5. Send session ID as cookie
6. Verify session ID on subsequent requests
```

**Session Management**
```python
# Create session
session_id = secrets.token_urlsafe(32)
expires_at = datetime.now() + timedelta(hours=24)

# Verify session
def verify_session(session_id: str) -> bool:
    session = get_session(session_id)
    if not session:
        return False
    if session.expires_at < datetime.now():
        delete_session(session_id)
        return False
    return True
```

### Password Protection

**Guestbook Password**
```python
import hashlib

# Store
password_hash = hashlib.sha256(
    password.encode()
).hexdigest()

# Verify
input_hash = hashlib.sha256(
    input_password.encode()
).hexdigest()
is_valid = input_hash == stored_hash
```

**Admin Password**
```python
# Generate hash with script
python scripts/generate_password_hash.py

# Store in .env
ADMIN_PASSWORD_HASH=a665a4592042...
```

### Input Validation

**Pydantic Schemas**
```python
from pydantic import BaseModel, validator

class GuestbookEntry(BaseModel):
    guest_name: str
    message: str
    password: str
    
    @validator('guest_name')
    def name_length(cls, v):
        if len(v) > 50:
            raise ValueError('Name must be 50 characters or less')
        return v
    
    @validator('message')
    def message_length(cls, v):
        if len(v) > 500:
            raise ValueError('Message must be 500 characters or less')
        return v
```

### HTTPS and CORS

**HTTPS**
- Railway automatically issues Let's Encrypt SSL certificates
- All HTTP requests redirected to HTTPS

**CORS**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Performance Optimization

### Backend Optimization

**Asynchronous Processing**
```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # Call LLM asynchronously
    response = await chatbot.ainvoke(request.message)
    return response
```

**Database Connection Pooling**
```python
# SQLAlchemy engine configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=5,        # Max 5 connections
    max_overflow=10,    # Allow 10 additional
    pool_pre_ping=True  # Check connection validity
)
```

### Frontend Optimization

**Image Optimization**
```bash
# WebP conversion (60-80% size reduction)
python scripts/resize_image.py

# Lazy loading
<img loading="lazy" src="...">
```

**CSS/JS Optimization**
```html
<!-- Load CSS first -->
<link rel="stylesheet" href="/static/css/main.css">

<!-- Load JS with defer -->
<script defer src="/static/js/main.js"></script>
```

**Caching Strategy**
```python
# Static file caching (1 year)
@app.get("/static/{path:path}")
async def static_files(path: str):
    return FileResponse(
        f"static/{path}",
        headers={
            "Cache-Control": "public, max-age=31536000"
        }
    )
```

### AI Chatbot Optimization

**Vector Search Optimization**
```python
# Adjust TOP_K (more = accurate but slower)
TOP_K_RESULTS = 3  # Default

# Embedding caching
@lru_cache(maxsize=100)
def get_embeddings(text: str):
    return embeddings.embed_query(text)
```

**LLM Call Optimization**
```python
# Token limit
MAX_TOKENS = 300  # Limit response length

# Lower temperature for speed
CHAT_TEMPERATURE = 0.3

# Use cheaper model
CHAT_MODEL = "gpt-4o-mini"  # Instead of gpt-4
```

## Monitoring and Logging

### Logging Strategy

```python
import logging

# Development
logging.basicConfig(level=logging.DEBUG)

# Production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Chatbot logging
logger.info(f"Question: {question}")
logger.info(f"Response: {response}")
logger.error(f"Error: {error}")
```

### LangSmith Tracing (Optional)

```python
# .env configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGSMITH_PROJECT=wedding-chatbot

# Automatically traces all LLM calls
# Check dashboard for:
# - Execution time per step
# - Input/output content
# - Cost calculation
```

## Scalability

### Horizontal Scaling

```
┌─────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴───┐
   │       │
   ▼       ▼
┌────┐  ┌────┐
│App1│  │App2│  ← Stateless applications
└─┬──┘  └─┬──┘
  │       │
  └───┬───┘
      ▼
┌──────────┐
│Shared DB │
└──────────┘
```

### Feature Extension

**Potential additions:**
- Real-time notifications (WebSocket)
- Image upload (S3/CloudFlare)
- Email notifications (SendGrid)
- Multi-language support (i18n)
- A/B testing
- Analytics dashboard

## Technical Decisions

### Why FastAPI?

✅ **Advantages:**
- Fast performance (Starlette-based)
- Async support
- Automatic API docs (Swagger)
- Pydantic integration

### Why LangGraph?

✅ **Advantages:**
- Easy state management
- Complex workflow implementation
- Convenient debugging
- LangSmith integration

### Why SQLite/PostgreSQL?

✅ **SQLite (Development):**
- No setup required
- File-based
- Fast prototyping

✅ **PostgreSQL (Production):**
- Concurrency support
- Stability
- Railway integration

### Why Vanilla JS?

✅ **Advantages:**
- Fast loading
- Small bundle size
- No framework overhead
- Suitable for simple projects

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Railway Documentation](https://docs.railway.app/)

---

**Last Updated**: 2025-01-22  
**Version**: 1.0.0