"""
AwakiFarmer MVP - Main Application
WhatsApp-based AI Farming Assistant
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
import logging
from dotenv import load_dotenv
import os

from services.ai_assistant import AIAssistant
from services.vision import VisionService
from services.weather import WeatherService
from services.database import DatabaseService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AwakiFarmer MVP",
    description="WhatsApp-based AI Farming Assistant for African Smallholder Farmers",
    version="1.0.0"
)

# Initialize services
ai_assistant = AIAssistant()
vision_service = VisionService()
weather_service = WeatherService()
db_service = DatabaseService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AwakiFarmer MVP",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            "database": "up",
            "ai_assistant": "up",
            "vision": "up",
            "weather": "up"
        }
    }


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(
    Body: str = Form(None),
    From: str = Form(...),
    MediaUrl0: str = Form(None),
    NumMedia: int = Form(0),
    MessageSid: str = Form(...)
):
    """
    Main webhook endpoint for WhatsApp messages
    Handles both text and image messages
    """
    
    logger.info(f"Received message from {From}: {Body[:50] if Body else 'Image'}")
    
    try:
        # Extract phone number (remove 'whatsapp:' prefix)
        farmer_phone = From.replace("whatsapp:", "")
        
        # Get or create farmer profile
        farmer = db_service.get_or_create_farmer(farmer_phone)
        
        # Get conversation history
        conversation_history = db_service.get_conversation_history(farmer_phone, limit=5)
        
        # Prepare response
        resp = MessagingResponse()
        msg = resp.message()
        
        # Handle image message (disease detection)
        if NumMedia > 0 and MediaUrl0:
            logger.info(f"Processing image from {farmer_phone}")
            
            # Analyze image for disease
            predictions = await vision_service.analyze_image(MediaUrl0)
            disease_result = vision_service.format_disease_result(predictions)
            
            # Get AI interpretation and recommendations
            prompt = f"""A farmer has sent an image of their crop with this disease detection result:

{disease_result}

The farmer asks: {Body if Body else 'What is this disease and how do I treat it?'}

Provide:
1. Explanation of what this disease is
2. Why it occurs
3. Treatment options (organic and chemical)
4. Prevention tips for the future

Keep your response practical and actionable for a smallholder farmer."""
            
            ai_response = await ai_assistant.get_response(
                prompt,
                conversation_history=conversation_history
            )
            
            # Save to database
            db_service.save_conversation(
                farmer_phone=farmer_phone,
                message_type="image",
                user_message=Body or "Image uploaded",
                ai_response=ai_response,
                metadata={"predictions": predictions, "image_url": MediaUrl0}
            )
            
            # Send response
            full_response = f"{disease_result}\n\n{ai_response}"
            msg.body(full_response)
            
        # Handle text message
        else:
            # Check if farmer is asking about weather
            if any(word in Body.lower() for word in ['weather', 'rain', 'forecast', 'temperature']):
                # Try to get weather if we have farmer's location
                if farmer.get('location'):
                    weather_data = await weather_service.get_weather(farmer['location'])
                    weather_report = weather_service.format_weather_report(weather_data)
                    
                    # Include weather in AI context
                    prompt = f"""The farmer asks: {Body}

Here's the current weather for their location ({farmer['location']}):
{weather_report}

Provide farming advice based on this weather information."""
                    
                    ai_response = await ai_assistant.get_response(
                        prompt,
                        conversation_history=conversation_history
                    )
                    
                    msg.body(f"{weather_report}\n\n{ai_response}")
                else:
                    # Ask for location
                    msg.body("To provide weather information, I need to know your location. Please tell me which town or region you're in. For example: 'I'm in Nairobi' or 'I'm near Kigali'")
                    
            # Regular conversation
            else:
                ai_response = await ai_assistant.get_response(
                    Body,
                    conversation_history=conversation_history
                )
                
                msg.body(ai_response)
            
            # Save to database
            db_service.save_conversation(
                farmer_phone=farmer_phone,
                message_type="text",
                user_message=Body,
                ai_response=ai_response if 'ai_response' in locals() else msg.body
            )
        
        return Response(content=str(resp), media_type="application/xml")
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        
        # Send error message to farmer
        resp = MessagingResponse()
        msg = resp.message()
        msg.body("Sorry, I encountered an error processing your message. Please try again in a moment. If the problem persists, contact support.")
        
        return Response(content=str(resp), media_type="application/xml")


@app.post("/test/send-message")
async def test_send_message(
    to: str,
    message: str
):
    """
    Test endpoint to send outbound WhatsApp messages
    Useful for testing proactive alerts and reminders
    """
    try:
        from twilio.rest import Client
        
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        
        message = client.messages.create(
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            body=message,
            to=f"whatsapp:{to}"
        )
        
        return {
            "status": "sent",
            "message_sid": message.sid,
            "to": to
        }
    
    except Exception as e:
        logger.error(f"Error sending test message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get basic usage statistics"""
    try:
        stats = db_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
