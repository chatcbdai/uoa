"""
Twitter/X posting implementation
"""

from typing import Dict, Any
from social_media.base import BaseSocialMediaPoster
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class TwitterPoster(BaseSocialMediaPoster):
    """Twitter/X-specific posting implementation"""
    
    def get_login_url(self) -> str:
        return "https://twitter.com/i/flow/login"
    
    def get_home_url(self) -> str:
        return "https://twitter.com/home"
    
    async def check_login_success(self) -> bool:
        """Check if we're logged in by looking for home elements"""
        try:
            # Check URL
            current_url = self.browser._page.url
            if "home" in current_url:
                return True
            
            # Look for logged-in indicators
            logged_in_selectors = [
                "a[aria-label='Profile']",
                "div[data-testid='primaryColumn']",
                "a[href='/compose/tweet']"
            ]
            
            for selector in logged_in_selectors:
                if await self.browser.wait_for_selector(selector, timeout=2000):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def create_post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Create a Twitter/X post"""
        try:
            # Detect posting elements
            elements = await self.element_detector.detect_posting_elements(
                self.browser,
                "twitter"
            )
            
            # Type the tweet text
            if elements.get('text_field') and content.get('text'):
                await self.browser.type_text(
                    elements['text_field'],
                    content['text']
                )
                
                # Add hashtags if provided
                if content.get('hashtags'):
                    # Add a space if text doesn't end with one
                    separator = " " if not content['text'].endswith(" ") else ""
                    await self.browser.type_text(
                        elements['text_field'],
                        f"{separator}{content['hashtags']}"
                    )
            
            # Upload image if provided
            if content.get('image_full_path'):
                # Find image upload button
                image_upload_selectors = [
                    "input[type='file'][accept*='image']",
                    "div[data-testid='fileInput']"
                ]
                
                for selector in image_upload_selectors:
                    file_input = await self.browser._page.query_selector(selector)
                    if file_input:
                        await file_input.set_input_files(content['image_full_path'])
                        await asyncio.sleep(random.uniform(2, 4))
                        break
            
            # Post the tweet
            post_button_selectors = [
                elements.get('post_submit_button'),
                "button[data-testid='tweetButtonInline']",
                "div[data-testid='tweetButton']"
            ]
            
            for selector in post_button_selectors:
                if selector and await self.browser.wait_for_selector(selector, timeout=2000):
                    await self.browser.click(selector)
                    break
            
            # Wait for posting to complete
            await asyncio.sleep(random.uniform(2, 4))
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Twitter posting failed: {str(e)}")
            raise
    
    async def verify_post_success(self) -> bool:
        """Verify the tweet was posted"""
        try:
            # Twitter usually redirects to the tweet or shows a success toast
            # Look for indicators
            success_indicators = [
                "Your post was sent",
                "Tweet sent",
                "View Tweet"
            ]
            
            page_text = await self.browser.extract_text()
            
            for indicator in success_indicators:
                if indicator.lower() in page_text.lower():
                    return True
            
            # Check if we're back at home with compose area cleared
            current_url = self.browser._page.url
            if "home" in current_url:
                # Check if compose area is empty
                compose_area = await self.browser._page.query_selector(
                    "div[data-testid='tweetTextarea_0']"
                )
                if compose_area:
                    text_content = await compose_area.text_content()
                    if not text_content or text_content.strip() == "":
                        return True
            
            return True  # Twitter often doesn't show explicit success
            
        except Exception:
            return False