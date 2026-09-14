"""
weather_service.py - Fetches weather data
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_weather(city=None):
    """
    Get current weather for a city.
    Returns a dict with temperature, description, and icon.
    """
    if not city:
        city = os.getenv('DEFAULT_CITY', 'London')
    
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key or api_key == 'your_weather_api_key_here':
        return {
            'temp': 20,
            'description': 'beautiful',
            'city': city,
            'error': 'Weather API not configured'
        }
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('cod') != 200:
            return {
                'temp': 20,
                'description': 'beautiful',
                'city': city,
                'error': data.get('message', 'Unknown error')
            }
        
        return {
            'temp': round(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'city': data['name'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed']
        }
    except Exception as e:
        print(f"❌ Weather error: {e}")
        return {
            'temp': 20,
            'description': 'beautiful',
            'city': city,
            'error': str(e)
        }