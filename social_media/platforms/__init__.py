"""
Platform implementations
"""

from .instagram import InstagramPoster
from .twitter import TwitterPoster
from .facebook import FacebookPoster
from .linkedin import LinkedInPoster

PLATFORM_CLASSES = {
    'instagram': InstagramPoster,
    'twitter': TwitterPoster,
    'facebook': FacebookPoster,
    'linkedin': LinkedInPoster
}

AVAILABLE_PLATFORMS = list(PLATFORM_CLASSES.keys())

def get_poster_class(platform: str):
    """Get poster class for a platform"""
    return PLATFORM_CLASSES.get(platform.lower())

__all__ = [
    'InstagramPoster',
    'TwitterPoster', 
    'FacebookPoster',
    'LinkedInPoster',
    'get_poster_class',
    'AVAILABLE_PLATFORMS'
]