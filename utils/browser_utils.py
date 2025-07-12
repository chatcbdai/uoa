"""
Browser utility functions for anti-detection features
"""

import random
from typing import Dict

def get_random_user_agent() -> str:
    """Get a random realistic user agent string"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]
    return random.choice(user_agents)

def get_realistic_viewport() -> Dict[str, int]:
    """Generate realistic viewport dimensions"""
    common_viewports = [
        {'width': 1920, 'height': 1080},  # Full HD
        {'width': 1366, 'height': 768},   # Common laptop
        {'width': 1536, 'height': 864},   # Common laptop
        {'width': 1440, 'height': 900},   # Common Mac
        {'width': 1280, 'height': 720},   # HD
        {'width': 1600, 'height': 900},   # Common widescreen
        {'width': 1680, 'height': 1050},  # Common Mac
    ]
    return random.choice(common_viewports)

def get_random_delay(min_ms: int = 50, max_ms: int = 150) -> float:
    """Get a random delay in milliseconds for human-like interactions"""
    return random.uniform(min_ms, max_ms)

def generate_convincing_referer(url: str) -> str:
    """Generate a convincing referer URL, typically from a search engine"""
    # Extract domain from URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    
    search_engines = [
        f'https://www.google.com/search?q={domain}',
        f'https://www.bing.com/search?q={domain}',
        f'https://duckduckgo.com/?q={domain}'
    ]
    
    return random.choice(search_engines)