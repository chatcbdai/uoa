"""
Browser module for undetectable web automation

This module provides various browser implementations with anti-detection features.
"""

from .base import BaseBrowser, BrowserError
from .factory import BrowserFactory, BrowserEngine

# Import the main browser class
try:
    from .stealth_browser import StealthBrowser as UndetectableBrowser
except ImportError:
    # Will be available after stealth_browser.py is created
    UndetectableBrowser = None

__all__ = [
    'BaseBrowser',
    'BrowserError',
    'BrowserFactory',
    'BrowserEngine',
    'UndetectableBrowser'
]