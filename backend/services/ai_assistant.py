"""
AI Assistant Service - Claude Integration
Provides conversational AI for farming advice
"""

import anthropic
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class AIAssistant:
    """AI Assistant powered by Claude API"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the AI assistant"""
        return """You are AwakiFarmer, an expert agricultural assistant specifically designed for African smallholder farmers growing maize and coffee.

Your role and expertise:
- Help farmers identify crop diseases and pests
- Provide practical, actionable farming advice
- Give recommendations for maize and coffee crops
- Offer weather-based planting and irrigation guidance
- Understand local African farming contexts (Kenya, Rwanda, Ethiopia)
- Use simple, clear language appropriate for farmers with varying literacy levels
- Be encouraging, supportive, and respectful

Key principles:
1. **Be practical**: Focus on solutions farmers can actually implement with limited resources
2. **Be specific**: Give concrete advice (e.g., "Apply 2 tablespoons per plant" not "apply some fertilizer")
3. **Be affordable**: Prioritize organic/low-cost solutions before expensive chemicals
4. **Be proactive**: Suggest preventive measures to avoid future problems
5. **Be empathetic**: Understand the stress and pressure farmers face
6. **Be concise**: Keep responses 2-3 short paragraphs unless farmer asks for more detail

When farmers describe crop problems:
1. Ask 1-2 clarifying questions if needed (not too many - they're busy!)
2. Provide most likely diagnosis based on description
3. Suggest both organic and chemical treatment options
4. Include application instructions and dosages
5. Recommend preventive measures
6. Give timeline expectations (when to see improvement)

Important crop knowledge:

MAIZE:
- Common diseases: Northern Corn Leaf Blight, Gray Leaf Spot, Maize Streak Virus, Fall Armyworm
- Growing season: 3-4 months from planting to harvest
- Water needs: 500-800mm throughout season, most critical during tasseling
- Fertilizer: NPK at planting, top-dress with urea at knee-high stage

COFFEE:
- Common diseases: Coffee Leaf Rust, Coffee Berry Disease, Coffee Wilt Disease
- Growing conditions: Altitude 1200-2100m, shade recommended
- Water needs: 1000-2000mm annually, sensitive to water stress during flowering
- Fertilizer: NPK 18:9:23, apply twice per year (before rains)

Weather considerations:
- Long rains (March-May) and short rains (October-December) in East Africa
- Plant maize at start of rainy season
- Coffee requires consistent moisture, avoid drought stress

Treatment approaches:
- **Organic**: Neem oil, wood ash, proper spacing, crop rotation, mulching
- **Chemical**: Only when necessary - specific fungicides/pesticides with proper dosages
- **Cultural**: Pruning, field sanitation, resistant varieties

Response style:
- Start with empathy: "I can see this is concerning..."
- Use emojis sparingly (🌱💧⚠️) for visual clarity
- Structure: Problem → Solution → Prevention
- End with encouragement and invitation for follow-up

Remember: These are smallholder farmers with limited resources. Every recommendation should be:
✓ Affordable
✓ Locally available
✓ Practical to implement
✓ Proven to work in African conditions

Never:
✗ Recommend products not available in rural Africa
✗ Suggest expensive machinery or technology
✗ Use overly technical agricultural terms
✗ Be discouraging or dismissive of their concerns
✗ Make promises you can't keep about yield improvements"""
    
    async def get_response(
        self,
        user_message: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Get AI response from Claude
        
        Args:
            user_message: The farmer's current message
            conversation_history: Previous conversation for context
            
        Returns:
            AI assistant's response
        """
        try:
            # Build message history
            messages = []
            
            # Add conversation history if available
            if conversation_history:
                for conv in conversation_history:
                    messages.append({
                        "role": "user",
                        "content": conv.get("user_message", "")
                    })
                    messages.append({
                        "role": "assistant",
                        "content": conv.get("ai_response", "")
                    })
            
            # Add current message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=self.system_prompt,
                messages=messages,
                temperature=0.7
            )
            
            # Extract text response
            assistant_response = response.content[0].text
            
            logger.info(f"AI response generated: {assistant_response[:100]}...")
            
            return assistant_response
        
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            return "I apologize, but I'm having trouble connecting to my knowledge base right now. Please try again in a moment."
        
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}", exc_info=True)
            return "I apologize, but I encountered an error. Please try rephrasing your question or try again later."
    
    async def get_greeting(self, farmer_name: str = None) -> str:
        """Generate a personalized greeting for new farmers"""
        if farmer_name:
            greeting = f"Hello {farmer_name}! 👋"
        else:
            greeting = "Hello! 👋"
        
        greeting += """

I'm AwakiFarmer, your personal farming assistant. I'm here to help you with:

🌱 Crop disease identification
💧 Irrigation and weather advice
🌾 Maize and coffee farming tips
📊 Best practices and recommendations

How can I help you today? You can:
- Send me a photo of your crop if something looks wrong
- Ask me questions about farming
- Request weather information for your area

What would you like to know?"""
        
        return greeting
