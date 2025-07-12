"""
Main orchestrator for social media posting
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import asyncio
import random

from browser import BrowserFactory
from social_media.credential_manager import CredentialManager
from social_media.content_manager import ContentManager
from social_media.element_detector import ElementDetector
from social_media.platforms import get_poster_class
from social_media.exceptions import SocialMediaError

logger = logging.getLogger(__name__)

class SocialMediaOrchestrator:
    """Orchestrates social media posting across platforms"""
    
    def __init__(self, storage_path: Path, llm_client):
        self.storage_path = storage_path
        self.credential_manager = CredentialManager(storage_path)
        self.content_manager = ContentManager(storage_path)
        self.element_detector = ElementDetector(llm_client)
        self.llm_client = llm_client
    
    async def post_to_platforms(
        self,
        platforms: List[str],
        content: Optional[Dict[str, str]] = None,
        use_csv: bool = True
    ) -> List[Dict[str, Any]]:
        """Post to multiple platforms"""
        results = []
        
        # Get content from CSV if requested
        if use_csv and not content:
            posts = self.content_manager.get_pending_posts()
            if not posts:
                raise SocialMediaError("No pending posts found in CSV")
        else:
            # Use provided content for all platforms
            posts = [{'platform': p, **content} for p in platforms]
        
        # Validate media files
        posts = self.content_manager.validate_media_files(posts)
        
        # Process each post
        for idx, post in enumerate(posts):
            platform = post['platform'].lower()
            
            if platform not in platforms:
                continue
            
            browser = None
            try:
                # Create browser instance
                browser = BrowserFactory.create(
                    engine="stealth",
                    headless=False,  # Show browser for social media
                    anti_detection=True
                )
                await browser.initialize()
                
                # Get poster class for platform
                poster_class = get_poster_class(platform)
                if not poster_class:
                    logger.error(f"No poster implementation for {platform}")
                    continue
                
                # Create poster instance
                poster = poster_class(
                    browser,
                    self.credential_manager,
                    self.element_detector
                )
                
                # Post content
                result = await poster.post(post)
                results.append(result)
                
                # Mark as posted if successful
                if result['success'] and use_csv:
                    self.content_manager.mark_as_posted('scheduled_posts.csv', idx)
                
                # Add delay between platforms
                await asyncio.sleep(random.uniform(5, 10))
                
            except Exception as e:
                logger.error(f"Failed to post to {platform}: {str(e)}")
                results.append({
                    'success': False,
                    'platform': platform,
                    'error': str(e)
                })
            finally:
                # Always close browser, even if an exception occurred
                if browser:
                    try:
                        await browser.close()
                    except Exception as close_error:
                        logger.error(f"Error closing browser: {close_error}")
        
        return results
    
    def add_credentials(self, platform: str, username: str, password: str) -> bool:
        """Add credentials for a platform"""
        try:
            self.credential_manager.save_credentials(
                platform,
                {'username': username, 'password': password}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials: {str(e)}")
            return False
    
    def list_platforms(self) -> List[str]:
        """List available platforms"""
        from social_media.platforms import AVAILABLE_PLATFORMS
        return AVAILABLE_PLATFORMS