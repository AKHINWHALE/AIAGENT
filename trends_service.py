"""
trends_service.py - Finds trending topics using Tavily API
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_trending_topics(category='general', max_results=5):
    """
    Find trending topics using Tavily search API.
    Returns a list of trending topic titles.
    """
    api_key = os.getenv('TAVILY_API_KEY')
    
    if not api_key:
        return ['Business news', 'Technology updates', 'Industry trends']
    
    # Search queries based on category
    queries = {
        'general': 'trending news today',
        'technology': 'trending technology news today',
        'business': 'trending business news today',
        'entertainment': 'trending entertainment news today',
        'sports': 'trending sports news today'
    }
    
    query = queries.get(category, 'trending news today')
    
    try:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        topics = []
        for result in data.get('results', []):
            topics.append({
                'title': result.get('title', ''),
                'content': result.get('content', '')[:200]
            })
        
        return topics if topics else ['General trending topics']
    
    except Exception as e:
        print(f"❌ Trends error: {e}")
        return ['General trending topics']