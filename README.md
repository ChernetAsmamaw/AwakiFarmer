# 🌱 AwakiFarmer MVP

**WhatsApp-Based AI Farming Assistant for African Smallholder Farmers**

A rapid-deploy AgriTech solution that delivers professional agronomic guidance through WhatsApp, powered by Claude AI and computer vision.

---

## 🚀 Quick Start (Get Running in 30 Minutes)

### Prerequisites
- Python 3.9+
- API keys (see Setup section)
- Twilio account with WhatsApp sandbox
- ngrok (for local testing)

### Installation

```bash
# Clone or download the project
cd awakifarmer-mvp/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

### Get API Keys

1. **Twilio (WhatsApp)** - https://www.twilio.com/try-twilio
   - Sign up, verify phone
   - Go to Console → Messaging → Try WhatsApp
   - Copy: Account SID, Auth Token, WhatsApp Number

2. **Anthropic Claude** - https://console.anthropic.com
   - Sign up
   - Create API key
   - Copy key (starts with sk-ant-api03-)

3. **Hugging Face** - https://huggingface.co/join
   - Sign up
   - Settings → Access Tokens → New token
   - Copy token (starts with hf_)

4. **OpenWeather** (optional) - https://openweathermap.org/api
   - Sign up for free
   - Copy API key

### Run the Server

```bash
# Start the FastAPI server
python app.py

# Server will run on http://localhost:8000
```

### Expose to Internet (for WhatsApp webhook)

```bash
# In a new terminal:
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### Configure Twilio Webhook

1. Go to Twilio Console → Messaging → Try it out → WhatsApp Sandbox
2. Set webhook URL: `https://YOUR-NGROK-URL.ngrok.io/whatsapp/webhook`
3. Save

### Test It!

1. Send "join <your-sandbox-code>" to the Twilio WhatsApp number
2. Send a message: "Hello"
3. You should get a response from AwakiFarmer!
4. Try sending a photo of a crop

---

## 📱 Features

### ✅ Implemented in MVP

- **WhatsApp Integration**: No app download, works on any phone
- **AI Conversational Assistant**: Powered by Claude for farming advice
- **Disease Detection**: Analyze crop photos for diseases (maize & coffee)
- **Weather Integration**: Location-based forecasts and irrigation advice
- **Conversation Memory**: Remembers context across messages
- **Multi-language Ready**: Framework for English, Swahili, etc.
- **Database Storage**: SQLite/PostgreSQL for farmer profiles and history

### 🔮 Future Enhancements (Post-MVP)

- Voice message support
- Proactive alerts (disease outbreaks, weather warnings)
- SMS fallback
- Admin dashboard
- Analytics and insights
- IoT sensor integration (Phase 3)

---

## 🏗️ Architecture

```
┌─────────────┐
│   Farmer    │
│  (WhatsApp) │
└──────┬──────┘
       │
       ↓
┌──────────────────────┐
│  Twilio WhatsApp API │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│   FastAPI Backend    │
├──────────────────────┤
│ • AI Assistant       │ ──→ Claude API
│ • Vision Service     │ ──→ Hugging Face
│ • Weather Service    │ ──→ OpenWeather
│ • Database Service   │ ──→ PostgreSQL/SQLite
└──────────────────────┘
```

---

## 📊 API Endpoints

### WhatsApp Webhook
```
POST /whatsapp/webhook
```
Main endpoint for receiving WhatsApp messages

### Health Check
```
GET /health
```
Check if all services are running

### Statistics
```
GET /stats
```
Get usage statistics (total farmers, messages, etc.)

### Test Send Message
```
POST /test/send-message
Body: {
  "to": "+254712345678",
  "message": "Hello from AwakiFarmer!"
}
```
Send outbound WhatsApp message (for testing)

---

## 💬 Example Conversations

### Disease Identification
```
Farmer: [Sends photo of maize with brown spots]
Farmer: What's wrong with my maize?

AwakiFarmer: 🔍 Disease Detection Results

✅ Most Likely: Northern Corn Leaf Blight
Confidence: 87.3% (very confident)

I can see Northern Corn Leaf Blight on your maize. This is a 
fungal disease common in humid conditions. Here's what you need 
to do...

[Detailed treatment advice follows]
```

### Weather Advisory
```
Farmer: Should I water my coffee today? I'm in Nyeri

AwakiFarmer: 🌤️ Weather for Nyeri

Current Conditions:
• Temperature: 21.5°C
• Humidity: 72%
• No rain expected in next 24 hours

💧 Irrigation Advice:
👀 Check soil moisture - moderate humidity but no rain. 
Irrigate if soil is dry at root level.

Coffee plants need consistent moisture, especially during 
flowering season...
```

### General Advice
```
Farmer: When is the best time to plant maize?

AwakiFarmer: 🌱 Perfect timing for maize planting depends on 
the rainy season in your area...

[Detailed seasonal guidance]
```

---

## 🗂️ Project Structure

```
awakifarmer-mvp/
├── backend/
│   ├── app.py                      # Main FastAPI application
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example               # Environment variables template
│   ├── .env                       # Your API keys (DO NOT COMMIT)
│   │
│   ├── services/
│   │   ├── ai_assistant.py        # Claude API integration
│   │   ├── vision.py              # Hugging Face disease detection
│   │   ├── weather.py             # OpenWeather integration
│   │   └── database.py            # SQLAlchemy models and queries
│   │
│   └── awakifarmer.db             # SQLite database (auto-created)
│
├── MVP_SETUP_GUIDE.md             # Detailed setup instructions
└── README.md                       # This file
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` with your values:

```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# Hugging Face
HUGGING_FACE_TOKEN=hf_xxxxxxxxxx

# OpenWeather (optional)
OPENWEATHER_API_KEY=your_key

# Database (defaults to SQLite if not set)
DATABASE_URL=sqlite:///./awakifarmer.db

# App Settings
DEBUG=True
LOG_LEVEL=INFO
```

---

## 🚀 Deployment

### Option 1: Railway (Recommended - Easiest)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Set environment variables in Railway dashboard
railway variables

# Deploy
railway up

# Get your URL
railway domain
```

Then configure Twilio webhook with your Railway URL.

### Option 2: Render

1. Push code to GitHub
2. Go to https://render.com
3. New → Web Service
4. Connect your repo
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
7. Add environment variables
8. Deploy

### Option 3: DigitalOcean App Platform

1. Connect GitHub repo
2. Select Python as environment
3. Set run command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Add environment variables
5. Deploy

---

## 💰 Costs

### Development/Testing (100 farmers)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Twilio WhatsApp | ~5,000 messages | $25 |
| Claude API | ~500K tokens | $50 |
| Hugging Face | Free tier | $0 |
| OpenWeather | Free tier | $0 |
| Railway/Render | Hobby tier | $5-10 |
| **TOTAL** | | **$80-85** |

**Per farmer**: $0.80-0.85/month

### Production (1,000 farmers)

Monthly: ~$500-700 ($0.50-0.70 per farmer)

---

## 📈 Success Metrics

Track these to validate your MVP:

### Technical
- ✅ Response time <5 seconds
- ✅ Disease detection accuracy >85%
- ✅ System uptime >99%

### User Engagement
- ✅ 70%+ weekly active users
- ✅ 4+ messages per farmer per week
- ✅ 2+ images uploaded per farmer per week

### Product Validation
- ✅ 4.5/5 satisfaction score
- ✅ 60%+ willingness to pay $5-10/month
- ✅ Measurable yield improvement testimonials

---

## 🧪 Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test stats endpoint
curl http://localhost:8000/stats

# Simulate WhatsApp message
curl -X POST http://localhost:8000/whatsapp/webhook \
  -d "Body=Hello" \
  -d "From=whatsapp:+254712345678" \
  -d "MessageSid=test123"
```

### Test with Real WhatsApp

1. Join Twilio sandbox (send "join <code>" to sandbox number)
2. Send test messages:
   - "Hello" (should get greeting)
   - "What's wrong with my maize?" (should get farming advice)
   - Send a crop photo (should get disease detection)
   - "What's the weather in Nairobi?" (should get weather)

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### WhatsApp messages not reaching webhook
- Check ngrok is running
- Verify webhook URL in Twilio console is correct (HTTPS)
- Check Twilio logs in dashboard

### "Model is loading" message from vision service
- Hugging Face models cold-start takes 20-30 seconds
- Just wait and try again
- This won't happen in production after first use

### Slow responses
- Check your internet connection
- Verify API keys are correct
- Look at logs: `tail -f app.log`

### Database errors
- Check DATABASE_URL in .env
- For SQLite, ensure write permissions in directory

---

## 📚 Documentation

- **Twilio WhatsApp**: https://www.twilio.com/docs/whatsapp
- **Claude API**: https://docs.anthropic.com
- **Hugging Face**: https://huggingface.co/docs/api-inference
- **FastAPI**: https://fastapi.tiangolo.com

---

## 🎯 Next Steps

### Week 1: Build & Test
- [x] Set up all services
- [x] Integrate WhatsApp
- [x] Add AI assistant
- [x] Add disease detection
- [ ] Test with 10 farmers
- [ ] Gather initial feedback

### Week 2-3: Iterate
- [ ] Fix bugs from testing
- [ ] Improve AI prompts
- [ ] Add more disease examples
- [ ] Test with 50-100 farmers
- [ ] Document common issues

### Week 4: Validate
- [ ] Conduct surveys
- [ ] Measure accuracy
- [ ] Assess willingness to pay
- [ ] Create case studies
- [ ] Prepare for first paying customers

---

## 🤝 Contributing

This is an MVP, so there's lots to improve! Areas for contribution:

- Additional crop types
- More disease models
- Voice message support
- Translation to local languages
- Admin dashboard
- Analytics

---

## 📞 Support

For issues or questions:
- Email: info@awakifarmer.com
- Check logs: `tail -f app.log`
- Review API documentation

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🌟 Acknowledgments

- Built with Claude AI (Anthropic)
- Hugging Face for disease detection models
- Twilio for WhatsApp Business API
- OpenWeather for weather data

---

**Ready to deploy?** Follow the setup guide and you'll have a working MVP in 2-3 days! 🚀
