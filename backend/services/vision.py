"""
Vision Service - Crop Disease Detection
Uses Hugging Face models for image analysis
"""

import requests
from PIL import Image
import io
import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class VisionService:
    """Computer vision service for crop disease detection"""
    
    def __init__(self):
        self.hf_token = os.getenv("HUGGING_FACE_TOKEN")
        if not self.hf_token:
            logger.warning("HUGGING_FACE_TOKEN not found - image analysis may be limited")
        
        # Primary model - general plant disease detection
        self.primary_model = "Diginsa/Plant-Disease-Detection-Project"
        self.primary_api_url = f"https://api-inference.huggingface.co/models/{self.primary_model}"
        
        # Fallback model - maize specific
        self.maize_model = "Lematrixai/corn_maize-disease-detection"
        self.maize_api_url = f"https://api-inference.huggingface.co/models/{self.maize_model}"
    
    async def analyze_image(self, image_url: str, crop_type: str = None) -> List[Dict]:
        """
        Analyze crop image for diseases
        
        Args:
            image_url: URL of the image to analyze
            crop_type: Optional crop type hint ('maize' or 'coffee')
            
        Returns:
            List of predictions with labels and confidence scores
        """
        try:
            logger.info(f"Analyzing image: {image_url}")
            
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Open and validate image
            image = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large (to reduce API costs)
            max_size = 1024
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr = img_byte_arr.getvalue()
            
            # Choose model based on crop type
            if crop_type == "maize":
                api_url = self.maize_api_url
                logger.info("Using maize-specific model")
            else:
                api_url = self.primary_api_url
                logger.info("Using general plant disease model")
            
            # Call Hugging Face API
            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            response = requests.post(
                api_url,
                headers=headers,
                data=img_byte_arr,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                logger.info(f"Analysis successful: {len(results)} predictions")
                return results[:5]  # Return top 5 predictions
            
            elif response.status_code == 503:
                # Model is loading
                logger.warning("Model is loading, please retry")
                return [{
                    "label": "Model Loading",
                    "score": 0.0,
                    "note": "The disease detection model is starting up. Please try again in 20 seconds."
                }]
            
            else:
                logger.error(f"API error: {response.status_code} - {response.text}")
                return None
        
        except requests.Timeout:
            logger.error("Image download timeout")
            return None
        
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}", exc_info=True)
            return None
    
    def format_disease_result(self, predictions: Optional[List[Dict]]) -> str:
        """
        Format predictions into human-readable text
        
        Args:
            predictions: List of prediction dictionaries
            
        Returns:
            Formatted string with results
        """
        if not predictions:
            return """Sorry, I couldn't analyze this image. This could be because:

1. The image is unclear or too dark
2. The crop is not visible enough
3. The disease detection service is temporarily unavailable

Please try:
- Taking a clearer photo in good lighting
- Getting closer to the affected part of the plant
- Sending the photo again

You can also describe what you see and I'll do my best to help!"""
        
        # Check if model is loading
        if predictions[0].get("note"):
            return predictions[0]["note"]
        
        # Get top prediction
        top_result = predictions[0]
        confidence = top_result['score'] * 100
        disease = top_result['label']
        
        # Clean up disease name (remove underscores, capitalize)
        disease_clean = disease.replace('_', ' ').title()
        
        # Determine confidence level
        if confidence >= 80:
            confidence_text = "very confident"
            emoji = "✅"
        elif confidence >= 60:
            confidence_text = "fairly confident"
            emoji = "⚠️"
        else:
            confidence_text = "uncertain - this is my best guess"
            emoji = "❓"
        
        result = f"🔍 **Disease Detection Results**\n\n"
        result += f"{emoji} **Most Likely: {disease_clean}**\n"
        result += f"Confidence: {confidence:.1f}% ({confidence_text})\n"
        
        # Add alternative possibilities if confidence is not very high
        if confidence < 80 and len(predictions) > 1:
            result += f"\n**Other possibilities:**\n"
            for pred in predictions[1:3]:  # Show 2 alternatives
                alt_disease = pred['label'].replace('_', ' ').title()
                alt_confidence = pred['score'] * 100
                result += f"• {alt_disease} ({alt_confidence:.1f}%)\n"
        
        # Add caveat if confidence is low
        if confidence < 60:
            result += f"\n💡 **Note:** The confidence is low. Please provide more details or a clearer image for a better diagnosis."
        
        return result
    
    def extract_disease_info(self, predictions: Optional[List[Dict]]) -> Dict:
        """
        Extract structured disease information
        
        Returns:
            Dictionary with disease name, confidence, and metadata
        """
        if not predictions or not predictions[0].get('label'):
            return {
                "disease": "Unknown",
                "confidence": 0.0,
                "status": "error"
            }
        
        top = predictions[0]
        
        return {
            "disease": top['label'].replace('_', ' ').title(),
            "confidence": top['score'],
            "alternatives": [
                {
                    "disease": p['label'].replace('_', ' ').title(),
                    "confidence": p['score']
                }
                for p in predictions[1:3]
            ] if len(predictions) > 1 else [],
            "status": "success"
        }
