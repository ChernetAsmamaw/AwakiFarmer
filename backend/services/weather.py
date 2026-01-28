"""
Weather Service - OpenWeather API Integration
Provides weather forecasts and irrigation recommendations
"""

import requests
import os
import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class WeatherService:
    """Weather service for farming recommendations"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            logger.warning("OPENWEATHER_API_KEY not found - weather features will be limited")
        
        self.geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    
    async def get_weather(self, location: str) -> Optional[Dict]:
        """
        Get weather forecast for a location
        
        Args:
            location: City or region name
            
        Returns:
            Weather data dictionary or None if error
        """
        try:
            if not self.api_key:
                return None
            
            logger.info(f"Getting weather for: {location}")
            
            # Geocode location
            geo_params = {
                "q": location,
                "limit": 1,
                "appid": self.api_key
            }
            
            geo_response = requests.get(self.geo_url, params=geo_params, timeout=10)
            
            if geo_response.status_code != 200 or not geo_response.json():
                logger.warning(f"Location not found: {location}")
                return None
            
            coords = geo_response.json()[0]
            lat, lon = coords['lat'], coords['lon']
            location_name = coords['name']
            
            logger.info(f"Found coordinates: {lat}, {lon} for {location_name}")
            
            # Get weather forecast
            weather_params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"  # Celsius
            }
            
            weather_response = requests.get(
                self.forecast_url,
                params=weather_params,
                timeout=10
            )
            
            if weather_response.status_code != 200:
                logger.error(f"Weather API error: {weather_response.status_code}")
                return None
            
            data = weather_response.json()
            
            return {
                "location": location_name,
                "country": coords.get('country', ''),
                "coordinates": {"lat": lat, "lon": lon},
                "current": data['list'][0],
                "forecast": data['list'][:8]  # Next 24 hours (3-hour intervals)
            }
        
        except requests.Timeout:
            logger.error("Weather API timeout")
            return None
        
        except Exception as e:
            logger.error(f"Error getting weather: {str(e)}", exc_info=True)
            return None
    
    def format_weather_report(self, weather_data: Optional[Dict]) -> str:
        """
        Format weather data into farmer-friendly message
        
        Args:
            weather_data: Weather data from get_weather()
            
        Returns:
            Formatted weather report string
        """
        if not weather_data:
            return "Sorry, I couldn't get weather data for that location. Please check the location name and try again."
        
        current = weather_data['current']
        forecast = weather_data['forecast']
        location = weather_data['location']
        
        # Current conditions
        temp = current['main']['temp']
        feels_like = current['main']['feels_like']
        humidity = current['main']['humidity']
        description = current['weather'][0]['description'].capitalize()
        
        # Check for rain in forecast
        rain_hours = []
        total_rain = 0
        for period in forecast:
            if 'rain' in period:
                rain_hours.append(period)
                total_rain += period['rain'].get('3h', 0)
        
        # Wind
        wind_speed = current['wind']['speed'] * 3.6  # Convert m/s to km/h
        
        # Format report
        report = f"🌤️ **Weather for {location}**\n\n"
        report += f"**Current Conditions:**\n"
        report += f"• Temperature: {temp:.1f}°C (feels like {feels_like:.1f}°C)\n"
        report += f"• Condition: {description}\n"
        report += f"• Humidity: {humidity}%\n"
        report += f"• Wind: {wind_speed:.1f} km/h\n"
        
        # Rain forecast
        report += f"\n**Next 24 Hours:**\n"
        if rain_hours:
            report += f"⚠️ Rain expected ({len(rain_hours)} periods, ~{total_rain:.1f}mm total)\n"
        else:
            report += f"☀️ No rain expected\n"
        
        # Farming recommendations
        report += f"\n**💧 Irrigation Advice:**\n"
        
        if rain_hours:
            if total_rain > 10:
                report += "✋ **Hold off on irrigation** - significant rain expected. Your crops will get plenty of water.\n"
            else:
                report += "⏸️ **Wait and monitor** - some rain expected but may not be enough. Check soil moisture after rain.\n"
        else:
            if humidity < 40:
                report += "💧 **Irrigate soon** - low humidity and no rain forecast. Your crops need water.\n"
            elif humidity < 60:
                report += "👀 **Check soil moisture** - moderate humidity but no rain. Irrigate if soil is dry.\n"
            else:
                report += "✅ **Soil should be okay** - good humidity levels. Monitor for next few days.\n"
        
        # Temperature warnings
        if temp > 35:
            report += "\n🌡️ **Heat Warning:** Very high temperatures. Crops may experience heat stress. Consider additional watering in evening.\n"
        elif temp < 10:
            report += "\n❄️ **Cold Warning:** Low temperatures may slow growth or damage sensitive crops. Protect if possible.\n"
        
        # Wind warnings
        if wind_speed > 30:
            report += f"\n💨 **Wind Warning:** Strong winds may damage plants. Consider providing support if needed.\n"
        
        return report
    
    def get_planting_recommendation(
        self,
        crop: str,
        location: str,
        current_month: int
    ) -> str:
        """
        Get planting recommendations based on season
        
        Args:
            crop: 'maize' or 'coffee'
            location: Farmer's location
            current_month: Current month (1-12)
            
        Returns:
            Planting recommendation
        """
        # East Africa has two rainy seasons:
        # Long rains: March-May
        # Short rains: October-December
        
        if crop.lower() == 'maize':
            if current_month in [2, 3]:
                return "🌱 **Perfect timing!** Plant maize now before the long rains (March-May). Soil should be ready."
            elif current_month in [9, 10]:
                return "🌱 **Good time to plant!** Short rains (October-December) are coming. Prepare your land now."
            elif current_month in [4, 5, 11, 12]:
                return "⏰ **Late but possible** - You can still plant but expect lower yields. Ensure good weed control."
            elif current_month in [6, 7, 8]:
                return "⏸️ **Wait for short rains** - Too dry now. Prepare land and get seeds ready for October planting."
            else:
                return "⏸️ **Wait for long rains** - Too dry now. Prepare land and get seeds ready for March planting."
        
        elif crop.lower() == 'coffee':
            if current_month in [2, 3, 4]:
                return "🌱 **Good time for coffee planting** - Plant before long rains. Ensure you have shade trees ready."
            elif current_month in [10, 11]:
                return "🌱 **Acceptable planting time** - Can plant during short rains, but long rains are better."
            else:
                return "⏸️ **Not ideal for planting** - Coffee is best planted before rainy season. Wait for March-April."
        
        return "Please specify your crop (maize or coffee) for planting recommendations."
