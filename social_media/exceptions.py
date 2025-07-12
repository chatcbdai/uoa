"""Custom exceptions for social media module"""

class SocialMediaError(Exception):
    """Base exception for social media operations"""
    pass

class AuthenticationError(SocialMediaError):
    """Raised when authentication fails"""
    pass

class PostingError(SocialMediaError):
    """Raised when posting fails"""
    pass

class CredentialError(SocialMediaError):
    """Raised when credential operations fail"""
    pass