"""
Undetectable Toolkit - Unified web browsing and scraping with anti-detection

A comprehensive toolkit that combines undetectable web browsing capabilities
with powerful scraping features.
"""

__version__ = "0.1.0"

# Import main API functions
from .api import (
    scrape,
    browse,
    download,
    search,
    screenshot,
    post_to_social,
    UndetectableConfig
)

# Import browser classes for advanced usage
from .browser import UndetectableBrowser

# Import scraper for direct usage
from .scrapers import UnifiedScraper

__all__ = [
    "scrape",
    "browse", 
    "download",
    "search",
    "screenshot",
    "post_to_social",
    "UndetectableConfig",
    "UndetectableBrowser",
    "UnifiedScraper"
]