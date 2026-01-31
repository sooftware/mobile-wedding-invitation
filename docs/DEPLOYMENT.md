# 🚂 Railway Deployment Guide

**English** | [한국어](./DEPLOYMENT.ko.md)

This guide provides step-by-step instructions for deploying the AI wedding invitation using Railway.

## 📋 Table of Contents

- [What is Railway?](#what-is-railway)
- [Pre-deployment Checklist](#pre-deployment-checklist)
- [Deploy with CLI](#deploy-with-cli)
- [Deploy with GitHub](#deploy-with-github)
- [PostgreSQL Setup](#postgresql-setup)
- [Environment Variables](#environment-variables)
- [Custom Domain](#custom-domain)
- [Troubleshooting](#troubleshooting)

## What is Railway?

[Railway](https://railway.app/) is a cloud application deployment platform.

### Why Railway?

✅ **Free Tier**
- $5 monthly credit
- Sufficient for small projects

✅ **Easy Deployment**
- Auto-deploy with Git push
- No complex configuration

✅ **PostgreSQL Integration**
- One-click database creation
- Auto-connection setup

✅ **Auto SSL**
- Automatic HTTPS
- No certificate management

✅ **Zero Config**
- Auto Dockerfile generation
- Auto environment detection

### Cost Guide

**Hobby Plan (Free)**
- $5 monthly credit
- 512 MB RAM
- 1 GB disk
- Suitable for small weddings (~200 guests)

**Estimated Usage**
```
Web service: ~$3/month
PostgreSQL: ~$1/month
Total: ~$4/month (within free tier)
```

**After Wedding?**
- Pause project
- Data preserved
- Resume anytime

## Pre-deployment Checklist

### 1. Create Railway Account

1. Visit [Railway website](https://railway.app/)
2. Click "Sign Up"
3. Log in with GitHub account

### 2. Verify Required Files

Ensure these files exist:

```
wedding-invitation/
├── main.py
├── requirements.txt
├── .env.example
├── config/
│   ├── config.json
│   └── couple_knowledge.json
└── (other files)
```

### 3. Prepare Environment Variables

Prepare these values:

- `OPENAI_API_KEY`: OpenAI API key
- `ADMIN_USERNAME`: Admin ID
- `ADMIN_PASSWORD_HASH`: Admin password hash
- `SECRET_KEY`: Session encryption key
- `KAKAO_APP_KEY`: (Optional) Kakao app key

**Generate admin password hash:**
```bash
python scripts/generate_password_hash.py
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Deploy with CLI

Deploy using Railway CLI.

### 1. Install Railway CLI

```bash
# Using npm
npm i -g @railway/cli

# Or Homebrew (macOS)
brew install railway
```

### 2. Login to Railway

```bash
railway login
```

Browser opens for authorization.

### 3. Initialize Project

```bash
# Navigate to project directory
cd wedding-invitation

# Create Railway project
railway init
```

When prompted:
- Select "Create a new project"
- Enter project name (e.g., my-wedding-invitation)

### 4. Add PostgreSQL

```bash
# Add PostgreSQL plugin
railway add -d postgres
```

### 5. Set Environment Variables

```bash
# Set environment variables (one at a time)
railway variables set OPENAI_API_KEY="your_api_key"
railway variables set ADMIN_USERNAME="admin"
railway variables set ADMIN_PASSWORD_HASH="your_hash"
railway variables set SECRET_KEY="your_secret_key"
railway variables set KAKAO_APP_KEY="your_kakao_key"

# (Optional) LangSmith
railway variables set LANGCHAIN_API_KEY="your_langsmith_key"
railway variables set LANGCHAIN_TRACING_V2="true"
railway variables set LANGSMITH_PROJECT="wedding-chatbot"
```

### 6. Deploy

```bash
# First deployment
railway up

# Check URL after deployment
railway open
```

Browser opens automatically!

### 7. Check Logs

```bash
# View real-time logs
railway logs

# View errors only
railway logs -f
```

## Deploy with GitHub

Auto-deploy with Git push.

### 1. Create GitHub Repository

```bash
# Initialize Git (if not done)
git init

# After creating repository on GitHub
git remote add origin https://github.com/yourusername/wedding-invitation.git
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 2. Create Railway Project

1. Access [Railway dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Select repository

### 3. Add PostgreSQL

1. Click "New" on project page
2. Select "Database" → "Add PostgreSQL"
3. `DATABASE_URL` environment variable auto-configured

### 4. Set Environment Variables

1. Click service on project page
2. Select "Variables" tab
3. Click "New Variable" to add:

```
OPENAI_API_KEY=your_api_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_hash
SECRET_KEY=your_secret_key
KAKAO_APP_KEY=your_kakao_key
```

### 5. Configure Deployment

1. Select "Settings" tab
2. Verify settings:

```
Build Command: (leave empty - auto-detect)
Start Command: python main.py
```

### 6. Trigger Deployment

```bash
# Auto-deploys on push to main branch
git add .
git commit -m "Update wedding info"
git push origin main
```

Railway automatically:
1. Pulls code
2. Installs dependencies
3. Builds application
4. Deploys

## PostgreSQL Setup

### Auto Setup (Recommended)

Railway automatically:
- Creates PostgreSQL instance
- Sets `DATABASE_URL` environment variable
- Auto-connects to application

No additional work needed!

### Manual Connection (Advanced)

To use specific PostgreSQL server:

```bash
# Set manually with environment variable
railway variables set DATABASE_URL="postgresql://user:password@host:port/database"
```

### Database Access

**Access with Railway CLI:**
```bash
# Open PostgreSQL console
railway connect postgres
```

**Access with external client:**
1. Select PostgreSQL service in Railway dashboard
2. Check connection info in "Connect" tab
3. Connect with pgAdmin, DBeaver, etc.

### Backup

**Auto backup:**
Railway doesn't auto-backup.

**Manual backup (Important!):**
```bash
# Backup locally
railway run pg_dump $DATABASE_URL > backup.sql

# Restore
railway run psql $DATABASE_URL < backup.sql
```

**Regular backup:**
Recommended to backup regularly before and after wedding.

## Environment Variables

### Set in Dashboard

1. Project → Select service
2. "Variables" tab
3. Click "New Variable"

### Set with CLI

```bash
# Set single variable
railway variables set KEY="value"

# Set multiple variables at once
railway variables set \
  KEY1="value1" \
  KEY2="value2" \
  KEY3="value3"

# View variables
railway variables

# Delete variable
railway variables delete KEY
```

### Import from .env File

```bash
# Upload all variables from .env file to Railway
while IFS= read -r line; do
  if [[ ! "$line" =~ ^#.*$ ]] && [[ -n "$line" ]]; then
    railway variables set "${line%%=*}=${line#*=}"
  fi
done < .env
```

### Environment-specific Variables

**Development:**
```bash
# .env.development
DEBUG=true
LOG_LEVEL=debug
```

**Production (Railway):**
```bash
# Set as Railway variables
DEBUG=false
LOG_LEVEL=info
```

### Protect Sensitive Information

⚠️ **Never commit to Git:**
- API keys
- Passwords
- Database URLs
- SECRET_KEY

✅ **Correct method:**
1. Commit only `.env.example` file
2. Set actual values as Railway environment variables
3. Add `.env` to `.gitignore`

## Custom Domain

Use your own domain instead of Railway's default (e.g., `your-app.railway.app`).

### 1. Purchase Domain

Buy domain from registrar:
- [Namecheap](https://www.namecheap.com/)
- [GoDaddy](https://www.godaddy.com/)
- [Google Domains](https://domains.google/)

Recommended examples:
- `john-jane-wedding.com`
- `wedding-2026.com`
- `ourwedding.com`

### 2. Add Domain to Railway

1. Select service in Railway project
2. "Settings" tab
3. "Domains" section
4. Enter "Custom Domain" (e.g., `www.your-domain.com`)

### 3. Configure DNS

In domain registrar's DNS management:

**Add CNAME record:**
```
Type: CNAME
Name: www (or @)
Value: your-app.railway.app
TTL: Auto (or 3600)
```

### 4. SSL Certificate

Railway automatically issues Let's Encrypt SSL certificate.
- Auto HTTPS
- Auto certificate renewal
- No additional setup needed

### 5. Setup Redirect (Optional)

Redirect `example.com` → `www.example.com`:

Add to domain DNS:
```
Type: A
Name: @
Value: 76.76.21.21 (Railway's IP)
```

Or use URL Redirect record (varies by registrar)

### Verification

1. Check DNS propagation (may take up to 48 hours):
```bash
nslookup www.your-domain.com
```

2. Access in browser:
```
https://www.your-domain.com
```

3. Verify SSL certificate:
Click padlock icon in address bar

## Troubleshooting

### Deployment Failed

**Symptom:** "Build failed" or "Deployment failed" error

**Solution 1: Check logs**
```bash
railway logs
```

**Solution 2: Dependencies issue**
```bash
# Verify requirements.txt
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push
```

**Solution 3: Specify Python version**
```bash
# Create runtime.txt file
echo "python-3.11" > runtime.txt
```

### Database Connection Error

**Symptom:** "Database connection failed"

**Solution 1: Verify DATABASE_URL**
```bash
railway variables | grep DATABASE_URL
```

**Solution 2: Restart PostgreSQL**
1. Railway dashboard
2. Select PostgreSQL service
3. "Settings" → "Restart"

**Solution 3: Check connection string**
```python
# Check in main.py
import os
print("DATABASE_URL:", os.getenv("DATABASE_URL"))
```

### Application Won't Start

**Symptom:** "Application failed to start"

**Solution 1: Check port configuration**
```python
# main.py
port = int(os.getenv("PORT", 8000))
uvicorn.run("main:app", host="0.0.0.0", port=port)
```

**Solution 2: Verify environment variables**
```bash
railway variables
```

Ensure all required variables are set

**Solution 3: Health check**
Railway checks if application is ready:
```python
@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

### Chatbot Not Working

**Symptom:** Chatbot not responding or errors

**Solution 1: Verify OpenAI API key**
```bash
railway variables | grep OPENAI_API_KEY
```

**Solution 2: Check knowledge base files**
```bash
# Verify config files deployed
railway run ls -la config/
```

**Solution 3: Check logs**
```bash
railway logs | grep chatbot
railway logs | grep ERROR
```

### Site is Slow

**Symptom:** Slow page loading

**Solution 1: Check free plan**
Railway free plan has 512MB RAM limit.

**Solution 2: Optimize images**
```bash
# Run WebP conversion script
python scripts/resize_image.py
```

**Solution 3: Consider upgrade**
If high traffic, consider Hobby Plan ($5/month)

### Domain Not Connected

**Symptom:** Cannot access custom domain

**Solution 1: Check DNS propagation**
```bash
nslookup www.your-domain.com
```

**Solution 2: Wait for propagation**
DNS propagation can take up to 48 hours.

**Solution 3: Verify DNS records**
- Check correct CNAME value entered
- Verify domain status in Railway dashboard

### Cost Exceeded

**Symptom:** Exceeded monthly $5 credit

**Solution 1: Check usage**
1. Railway dashboard
2. "Usage" tab
3. Check usage per service

**Solution 2: Stop unused services**
```bash
# Delete unused services
railway service delete SERVICE_NAME
```

**Solution 3: Change model**
```bash
# Use cheaper GPT model
railway variables set CHAT_MODEL="gpt-3.5-turbo"
```

## Deployment Checklist

### Before Deployment
- [ ] OpenAI API key ready
- [ ] Admin password hash generated
- [ ] SECRET_KEY generated
- [ ] config.json completed
- [ ] couple_knowledge.json completed
- [ ] Images optimized (WebP)
- [ ] requirements.txt updated

### Railway Setup
- [ ] Railway account created
- [ ] PostgreSQL added
- [ ] All environment variables set
- [ ] GitHub repository connected (if using auto-deploy)

### After Deployment
- [ ] Site accessible
- [ ] Chatbot tested
- [ ] Guestbook tested
- [ ] RSVP tested
- [ ] Admin page login tested
- [ ] Mobile responsive checked
- [ ] KakaoTalk sharing tested (optional)
- [ ] Database backup created

### Wedding Day
- [ ] Server status monitored
- [ ] Logs checked
- [ ] Database backup created

### After Wedding
- [ ] Download guestbook CSV
- [ ] Download RSVP data CSV
- [ ] Final database backup
- [ ] Pause project (save costs)

## Additional Resources

### Railway Official Documentation
- [Railway Docs](https://docs.railway.app/)
- [CLI Docs](https://docs.railway.app/develop/cli)
- [Environment Variables Guide](https://docs.railway.app/develop/variables)

### Community
- [Railway Discord](https://discord.gg/railway)
- [Railway Blog](https://blog.railway.app/)

### Related Guides
- [Installation Guide](./INSTALLATION.md)
- [Configuration Guide](./CONFIGURATION.md)
- [AI Chatbot Guide](./CHATBOT.md)

## Need Help?

- 📧 [Email](mailto:your.email@example.com)
- 💬 [Discord Community](https://discord.gg/your-server)
- 🐛 [GitHub Issues](https://github.com/yourusername/wedding-invitation/issues)

---

**Congratulations! 🎉** 

If successfully deployed, you can now share your invitation with guests and let them chat with the AI chatbot!