# 🚀 AwakiFarmer Deployment Guide

This guide covers deploying AwakiFarmer to production. Choose the platform that best fits your needs.

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] All API keys ready (Twilio, Claude, Hugging Face, OpenWeather)
- [ ] Code tested locally
- [ ] Database schema created
- [ ] Environment variables documented
- [ ] Twilio WhatsApp number ready for production
- [ ] Domain name (optional but recommended)

---

## 🎯 Recommended: Railway

**Why Railway?**
- Easiest deployment
- Automatic HTTPS
- Built-in database support
- Generous free tier ($5/month credit)
- Perfect for MVPs

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 2: Login

```bash
railway login
```

### Step 3: Initialize Project

```bash
cd awakifarmer-mvp
railway init
```

Select "Create new project" and give it a name.

### Step 4: Add Environment Variables

```bash
railway variables
```

Or add via Railway dashboard:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`
- `ANTHROPIC_API_KEY`
- `HUGGING_FACE_TOKEN`
- `OPENWEATHER_API_KEY`
- `DATABASE_URL` (Railway will provide this if you add PostgreSQL)

### Step 5: Add PostgreSQL (Optional)

```bash
railway add postgresql
```

Railway will automatically set `DATABASE_URL`.

### Step 6: Deploy

```bash
railway up
```

### Step 7: Get Your URL

```bash
railway domain
```

Copy the URL (e.g., `https://awakifarmer-production.up.railway.app`)

### Step 8: Update Twilio Webhook

1. Go to Twilio Console → Messaging → WhatsApp Sandbox (or your approved number)
2. Set webhook URL: `https://your-railway-url.up.railway.app/whatsapp/webhook`
3. Save

### Step 9: Test

Send a WhatsApp message to your number and verify it works!

---

## 🌐 Alternative: Render

**Why Render?**
- Free tier available
- Easy GitHub integration
- Good performance
- Managed databases

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/awakifarmer-mvp.git
git push -u origin main
```

### Step 2: Create Render Account

Go to https://render.com and sign up with GitHub.

### Step 3: Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** awakifarmer-mvp
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`

### Step 4: Add Environment Variables

In Render dashboard, add:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`
- `ANTHROPIC_API_KEY`
- `HUGGING_FACE_TOKEN`
- `OPENWEATHER_API_KEY`
- `DATABASE_URL` (if using Render PostgreSQL)

### Step 5: Deploy

Click "Create Web Service" and wait for deployment.

### Step 6: Add Database (Optional)

1. Click "New +" → "PostgreSQL"
2. Copy the "Internal Database URL"
3. Add as `DATABASE_URL` environment variable in your web service

### Step 7: Update Twilio Webhook

Use your Render URL: `https://awakifarmer-mvp.onrender.com/whatsapp/webhook`

---

## 🐳 Alternative: Docker + Any Host

**Why Docker?**
- Consistent environment
- Works on any cloud provider
- Easy to scale

### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - TWILIO_WHATSAPP_NUMBER=${TWILIO_WHATSAPP_NUMBER}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - HUGGING_FACE_TOKEN=${HUGGING_FACE_TOKEN}
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - DATABASE_URL=postgresql://postgres:password@db:5432/awakifarmer
    depends_on:
      - db
    restart: always

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=awakifarmer
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

volumes:
  postgres_data:
```

### Step 3: Build and Run

```bash
# Create .env file with your API keys
cp backend/.env.example .env

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Step 4: Deploy to Cloud

#### DigitalOcean App Platform
1. Push to GitHub
2. Connect to DigitalOcean App Platform
3. Select Dockerfile deployment
4. Add environment variables
5. Deploy

#### AWS ECS/Fargate
1. Push image to ECR
2. Create ECS task definition
3. Configure load balancer
4. Deploy service

---

## 🔐 Production Security

### 1. Use HTTPS Only
All platforms above provide free HTTPS. Never use HTTP in production.

### 2. Secure Environment Variables
- Never commit .env files
- Use platform secret managers
- Rotate keys regularly

### 3. Database Security
- Use strong passwords
- Enable SSL connections
- Regular backups
- Restrict access by IP

### 4. API Rate Limiting
Add rate limiting to prevent abuse:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/whatsapp/webhook")
@limiter.limit("60/minute")
async def whatsapp_webhook(...):
    ...
```

### 5. Monitoring

#### Railway
Built-in logs and metrics in dashboard.

#### Render
- View logs: `render logs awakifarmer-mvp`
- Metrics in dashboard

#### Add Sentry for Error Tracking
```bash
pip install sentry-sdk[fastapi]
```

```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production"
)
```

---

## 📊 Production Checklist

After deployment, verify:

- [ ] Health endpoint returns 200: `curl https://your-url.com/health`
- [ ] WhatsApp messages work
- [ ] Image uploads work
- [ ] Weather API works
- [ ] Database is saving conversations
- [ ] Logs are accessible
- [ ] Error notifications set up
- [ ] Backup strategy in place
- [ ] Monitoring enabled

---

## 🔄 Continuous Deployment

### GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install Railway
        run: npm install -g @railway/cli
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

Get Railway token: `railway login --browserless`

---

## 🆘 Troubleshooting

### Deployment fails
- Check logs: `railway logs` or Render dashboard
- Verify all environment variables are set
- Check Python version compatibility

### WhatsApp not working
- Verify webhook URL is correct (HTTPS required)
- Check Twilio webhook logs in dashboard
- Test health endpoint: `curl https://your-url.com/health`

### Database connection errors
- Verify DATABASE_URL is correct
- Check if database is running
- Test connection separately

### Slow responses
- Check API rate limits
- Monitor cloud provider metrics
- Consider adding Redis cache
- Upgrade to paid tier if on free plan

---

## 💰 Cost Estimates

### Railway (Recommended for MVP)
- **Free Tier:** $5/month credit (enough for testing)
- **Hobby:** $5/month (good for 100-500 farmers)
- **Pro:** $20/month (good for 1000+ farmers)

### Render
- **Free:** $0 (limited, good for testing)
- **Starter:** $7/month (good for production)

### DigitalOcean
- **Basic Droplet:** $6/month
- **App Platform:** $5-12/month

---

## 📈 Scaling Considerations

### Up to 1,000 farmers
- Basic tier on any platform
- Single server instance
- SQLite or small PostgreSQL

### 1,000 - 10,000 farmers
- Upgrade to paid tier
- Add Redis for caching
- PostgreSQL with more storage
- Consider load balancer

### 10,000+ farmers
- Multiple server instances
- Dedicated database
- CDN for media
- Queue system (Celery + Redis)
- Professional monitoring

---

## 🎯 Next Steps After Deployment

1. **Set up monitoring** (Sentry, LogRocket, or similar)
2. **Configure backups** (database, logs)
3. **Set up alerts** (downtime, errors, API limits)
4. **Document runbook** (how to debug, restart, etc.)
5. **Test disaster recovery** (can you restore from backup?)

---

**You're deployed! 🎉 Now start onboarding farmers!**
