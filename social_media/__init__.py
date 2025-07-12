"""
Social Media Automation Module
"""

from .orchestrator import SocialMediaOrchestrator
from .exceptions import SocialMediaError, AuthenticationError, PostingError

__all__ = [
    'SocialMediaOrchestrator',
    'SocialMediaError',
    'AuthenticationError',
    'PostingError'
]