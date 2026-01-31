# 💻 Installation Guide

**English** | [한국어](./INSTALLATION.ko.md)

This guide provides detailed instructions for installing and running the AI wedding invitation locally.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Installation Process](#installation-process)
- [Environment Variable Setup](#environment-variable-setup)
- [Configuration Files](#configuration-files)
- [Running and Testing](#running-and-testing)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Required

**Operating System:**
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Linux (Ubuntu 20.04+, Debian, etc.)

**Software:**
- Python 3.8+ (Recommended: 3.11)
- pip (Python package manager)
- Git (Version control)

**Hardware:**
- CPU: Dual-core or higher
- RAM: Minimum 2GB (Recommended 4GB)
- Disk: 500MB+ free space

### Optional

- PostgreSQL 15+ (Production environment)
- Node.js 18+ (For Railway CLI)
- Text editor (VS Code, Sublime Text, etc.)

## Installation Process

### 1. Check Python Installation

**Windows:**
```bash
# In PowerShell or CMD
python --version
```

If Python is not installed:
1. Visit [Python official site](https://www.python.org/downloads/)
2. Download latest version (3.11 recommended)
3. During installation, check "Add Python to PATH"

**macOS:**
```bash
# Install with Homebrew
brew install python@3.11

# Or use official installer
# Download from python.org
```

**Linux (Ubuntu/Debian):**
```bash
# Update system
sudo apt update
sudo apt upgrade

# Install Python
sudo apt install python3.11 python3-pip python3-venv
```

**Verify Installation:**
```bash
python --version
# Output: Python 3.11.x

pip --version
# Output: pip 23.x.x
```

### 2. Check Git Installation

```bash
git --version
```

If Git is not installed:

**Windows:**
- Download and install [Git for Windows](https://git-scm.com/download/win)

**macOS:**
```bash
brew install git
```

**Linux:**
```bash
sudo apt install git
```

### 3. Clone Project

```bash
# Clone GitHub repository
git clone https://github.com/yourusername/wedding-invitation.git

# Navigate to project directory
cd wedding-invitation

# Check directory structure
ls -la
```

Expected output:
```
.
├── app/
├── config/
├── static/
├── templates/
├── scripts/
├── main.py
├── requirements.txt
└── .env.example
```

### 4. Create Virtual Environment

Virtual environments allow independent Python package management per project.

**Create:**
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

**Activate:**
```bash
# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

Verify activation:
```bash
# (venv) appears before prompt
(venv) user@computer:~/wedding-invitation$
```

### 5. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

Main packages installed:
- fastapi - Web framework
- uvicorn - ASGI server
- langchain - LLM framework
- langgraph - Workflow management
- openai - OpenAI API client
- chromadb - Vector database
- psycopg2-binary - PostgreSQL driver
- jinja2 - Template engine

Verify installation:
```bash
pip list
```

### 6. Create Environment File

```bash
# Copy .env.example to .env
cp .env.example .env

# On Windows
copy .env.example .env
```

Open `.env` file in text editor for modification.

## Environment Variable Setup

### Required Environment Variables

**`.env` file:**
```bash
# ===========================================
# OpenAI API Settings (for AI chatbot)
# ===========================================
OPENAI_API_KEY=sk-your-openai-api-key-here

# Model selection
CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Generation parameters
CHAT_TEMPERATURE=0.7
MAX_TOKENS=300
TOP_K_RESULTS=3

# ===========================================
# Admin Account Settings
# ===========================================
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your-generated-hash-here

# ===========================================
# Session Security Key
# ===========================================
SECRET_KEY=your-secret-key-here

# ===========================================
# Database (optional for local)
# ===========================================
# DATABASE_URL=postgresql://user:password@localhost:5432/wedding
# If not set, SQLite will be used

# ===========================================
# KakaoTalk Sharing (optional)
# ===========================================
KAKAO_APP_KEY=your-kakao-app-key

# ===========================================
# LangSmith Tracing (optional)
# ===========================================
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your-langsmith-key
# LANGSMITH_PROJECT=wedding-chatbot
```

### Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Log in or sign up
3. Click "API Keys" menu
4. Click "Create new secret key"
5. Enter key name (e.g., wedding-chatbot)
6. Copy generated key (shown only once!)
7. Paste into `OPENAI_API_KEY` in `.env` file

**Security Note:**
- ⚠️ Never commit API keys to GitHub
- ⚠️ Never share publicly
- ✅ `.env` file is included in `.gitignore`

### Set Admin Password

**1. Generate password hash:**
```bash
python scripts/generate_password_hash.py
```

**2. Execution screen:**
```
🔐 Admin Password Hash Generation Tool
========================================

Enter new password: [input]
Re-enter password: [input]

✅ Password hash generated!
========================================

📋 Add to .env file:

ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

**3. Copy to `.env` file:**
```bash
ADMIN_PASSWORD_HASH=a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
```

### Generate SECRET_KEY

Generate random key for session encryption:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output:
```
xK8vN2pQmR5wT1yU3zL7hA9bC4dE6fG8
```

Add to `.env` file:
```bash
SECRET_KEY=xK8vN2pQmR5wT1yU3zL7hA9bC4dE6fG8
```

### Get Kakao App Key (Optional)

To use KakaoTalk sharing:

1. Visit [Kakao Developers](https://developers.kakao.com/)
2. Log in and create app
3. "My Applications" → Select app
4. Copy "JavaScript Key" from "App Keys" section
5. Add to `.env` file:
   ```bash
   KAKAO_APP_KEY=your-javascript-key
   ```

## Configuration Files

### 1. Wedding Information Setup (config.json)

Edit `config/config.json` to enter actual wedding information.

**Basic structure:**
```json
{
  "wedding": {
    "groom": {
      "name_kr": "John Kim",
      "name_en": "John",
      "display_name": "John",
      "birth_order": "First Son",
      "parents": {
        "father": "Father Kim",
        "mother": "Mother Kim"
      }
    },
    "bride": {
      "name_kr": "Jane Cho",
      "name_en": "Jane",
      "display_name": "Jane",
      "birth_order": "First Daughter",
      "parents": {
        "father": "Father Cho",
        "mother": "Mother Cho"
      }
    },
    "date": {
      "year": 2026,
      "month": 5,
      "day": 17,
      "time": "14:00",
      "day_of_week": "Sunday",
      "display_time": "2:00 PM"
    },
    "venue": {
      "name": "Lacitta Theater",
      "address": "1F, 16 Maeheon-ro, Seocho-gu, Seoul"
    }
  }
}
```

See [Configuration Guide](./CONFIGURATION.md) for detailed setup.

### 2. AI Chatbot Knowledge Base

Edit `config/couple_knowledge.json` to write content for chatbot responses.

**Minimum example:**
```json
[
  {
    "id": "first_meeting",
    "topic": "First Meeting",
    "content": "We first met at university in 2018."
  },
  {
    "id": "proposal",
    "topic": "Proposal",
    "content": "He proposed in February 2025."
  },
  {
    "id": "honeymoon",
    "topic": "Honeymoon",
    "content": "We're planning to go to Dubai, Maldives, and Singapore."
  }
]
```

See [AI Chatbot Guide](./CHATBOT.md) for detailed writing instructions.

### 3. Prepare Gallery Images

**Image location:**
```
static/assets/images/wedding-snaps/
```

**Image optimization:**
```bash
# Resize and convert to WebP
python scripts/resize_image.py
```

**Image rules:**
- Filenames: `1.webp`, `2.webp`, ... `n.webp`
- Format: WebP (recommended) or JPG
- Size: Max 1920px (longest side)

**Set count in config.json:**
```json
{
  "content": {
    "gallery": {
      "total_photos": 28
    }
  }
}
```

## Running and Testing

### 1. Initialize Database

```bash
# Database initializes automatically when running application
python main.py
```

Check logs:
```
INFO:     Started server process
INFO:     Waiting for application startup.
✅ guestbook table verified/created
✅ rsvp table verified/created
🤖 LangGraph chatbot successfully initialized!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Access in Browser

**Main page:**
```
http://localhost:8000
```

**Admin page:**
```
http://localhost:8000/admin/login
```

### 3. Test Features

**Checklist:**

- [ ] Main page loads
- [ ] D-Day counter works
- [ ] Gallery images display
- [ ] Map displays
- [ ] Background music plays
- [ ] AI chatbot responds
- [ ] Create guestbook entry
- [ ] Submit RSVP
- [ ] Admin login
- [ ] Admin dashboard

### 4. Run in Development Mode

Auto-restart on code changes:

```bash
# Add --reload option
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Check Logs

```bash
# Real-time logs
python main.py

# Or development mode
uvicorn main:app --reload --log-level debug
```

## Troubleshooting

### Python Version Error

**Symptom:**
```
SyntaxError: invalid syntax
```

**Solution:**
```bash
# Check Python version
python --version

# Upgrade if not 3.8+
```

### Package Installation Failure

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solution 1: Upgrade pip**
```bash
pip install --upgrade pip
```

**Solution 2: Install individually**
```bash
# Install only problematic packages
pip install fastapi
pip install langchain
```

**Solution 3: Reinstall Python**
```bash
# Delete and recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### OpenAI API Error

**Symptom:**
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solution:**
1. Check `OPENAI_API_KEY` in `.env` file
2. Remove spaces before/after API key
3. Enter without quotes
4. Verify key validity on OpenAI platform

### Database Error

**Symptom:**
```
sqlite3.OperationalError: no such table: guestbook
```

**Solution:**
```bash
# Delete and recreate database file
rm wedding.db
python main.py
```

### Port Conflict

**Symptom:**
```
ERROR: [Errno 48] Address already in use
```

**Solution 1: Use different port**
```bash
# Add to .env file
PORT=8080

# Or specify directly
python main.py --port 8080
```

**Solution 2: Kill existing process**
```bash
# macOS/Linux
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID_number> /F
```

### Environment Variables Not Loading

**Symptom:**
Chatbot not working or admin login fails

**Solution:**
```bash
# Check .env file location
ls -la .env

# Check file contents
cat .env

# Reinstall python-dotenv
pip install --upgrade python-dotenv
```

### Virtual Environment Activation Issue (Windows)

**Symptom:**
```
cannot be loaded because running scripts is disabled on this system
```

**Solution:**
```powershell
# Run PowerShell as administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use CMD
venv\Scripts\activate.bat
```

### Images Not Displaying

**Symptom:**
Gallery empty or 404 error

**Solution:**
```bash
# Check image file paths
ls static/assets/images/wedding-snaps/

# Check count in config.json
# "total_photos": 28 → Must match actual image count

# Check image permissions
chmod 644 static/assets/images/wedding-snaps/*
```

### Chatbot Not Responding

**Symptom:**
No response when asking chatbot questions

**Solution:**
```bash
# Check logs
python main.py

# Test OpenAI API key
python -c "from openai import OpenAI; client = OpenAI(); print(client.models.list())"

# Check knowledge base file
cat config/couple_knowledge.json
```

## Next Steps

After installation:

1. **Customize Settings**
   - [Configuration Guide](./CONFIGURATION.md)
   - [Chatbot Guide](./CHATBOT.md)

2. **Modify Design**
   - [Customization Guide](./CUSTOMIZATION.md)

3. **Prepare Deployment**
   - [Railway Deployment Guide](./DEPLOYMENT.md)

4. **Testing**
   - Test thoroughly before sharing with guests
   - Check on mobile devices

## Additional Help

### Useful Commands

**Restart development server:**
```bash
# Stop with Ctrl+C then
python main.py
```

**Deactivate virtual environment:**
```bash
deactivate
```

**Update project:**
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

**Backup database:**
```bash
# SQLite
cp wedding.db wedding.db.backup

# PostgreSQL
pg_dump wedding > backup.sql
```

### Recommended Development Tools

**Text Editors:**
- [Visual Studio Code](https://code.visualstudio.com/) (Recommended)
- [Sublime Text](https://www.sublimetext.com/)
- [Atom](https://atom.io/)

**VS Code Extensions:**
- Python
- Pylance
- SQLite Viewer
- GitLens

**Debugging Tools:**
- Chrome DevTools (F12)
- Python Debugger (pdb)

## Need Help?

- 📧 [Email](mailto:your.email@example.com)
- 💬 [Discord Community](https://discord.gg/your-server)
- 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)
- 📖 [FAQ](./FAQ.md)

---

**Congratulations! 🎉**

Local environment setup is complete. You're now ready to customize the invitation and share it with guests!