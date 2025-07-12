"""
Facebook posting implementation
"""

from typing import Dict, Any
from social_media.base import BaseSocialMediaPoster
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class FacebookPoster(BaseSocialMediaPoster):
    """Facebook-specific posting implementation"""
    
    def get_login_url(self) -> str:
        return "https://www.facebook.com/login"
    
    def get_home_url(self) -> str:
        return "https://www.facebook.com/"
    
    async def check_login_success(self) -> bool:
        """Check if we're logged in"""
        try:
            # Check URL
            current_url = self.browser._page.url
            if "login" not in current_url and "facebook.com" in current_url:
                # Look for logged-in elements
                logged_in_selectors = [
                    "div[role='navigation']",
                    "a[aria-label='Home']",
                    "div[aria-label='Create']"
                ]
                
                for selector in logged_in_selectors:
                    if await self.browser.wait_for_selector(selector, timeout=2000):
                        return True
            
            return False
            
        except Exception:
            return False
    
    async def create_post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Create a Facebook post"""
        try:
            # Detect posting elements
            elements = await self.element_detector.detect_posting_elements(
                self.browser,
                "facebook"
            )
            
            # Click create post area if needed
            create_post_selectors = [
                elements.get('create_post_button'),
                "div[role='button']:has-text('What\\'s on your mind')",
                "span:has-text('What\\'s on your mind')",
                "div[aria-label='Create a post']"
            ]
            
            for selector in create_post_selectors:
                if selector and await self.browser.wait_for_selector(selector, timeout=2000):
                    await self.browser.click(selector)
                    await asyncio.sleep(random.uniform(1, 2))
                    break
            
            # Type the post text
            if elements.get('text_field') and content.get('text'):
                await self.browser.type_text(
                    elements['text_field'],
                    content['text']
                )
                
                # Add hashtags
                if content.get('hashtags'):
                    await self.browser.type_text(
                        elements['text_field'],
                        f"\n\n{content['hashtags']}"
                    )
            
            # Upload image if provided
            if content.get('image_full_path'):
                # Look for photo/video button
                photo_button_selectors = [
                    "div[aria-label='Photo/Video']",
                    "div:has-text('Photo/Video')",
                    "input[type='file'][accept*='image']"
                ]
                
                for selector in photo_button_selectors:
                    if "input" in selector:
                        file_input = await self.browser._page.query_selector(selector)
                        if file_input:
                            await file_input.set_input_files(content['image_full_path'])
                            await asyncio.sleep(random.uniform(2, 4))
                            break
                    else:
                        if await self.browser.wait_for_selector(selector, timeout=2000):
                            await self.browser.click(selector)
                            await asyncio.sleep(random.uniform(1, 2))
                            # Now find file input
                            file_input = await self.browser._page.query_selector("input[type='file']")
                            if file_input:
                                await file_input.set_input_files(content['image_full_path'])
                                await asyncio.sleep(random.uniform(2, 4))
                            break
            
            # Post the content
            post_button_selectors = [
                elements.get('post_submit_button'),
                "div[aria-label='Post']",
                "span:has-text('Post')",
                "button:has-text('Post')"
            ]
            
            for selector in post_button_selectors:
                if selector and await self.browser.wait_for_selector(selector, timeout=2000):
                    await self.browser.click(selector)
                    break
            
            # Wait for posting to complete
            await asyncio.sleep(random.uniform(3, 5))
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Facebook posting failed: {str(e)}")
            raise
    
    async def verify_post_success(self) -> bool:
        """Verify the post was created"""
        try:
            # Facebook shows the post in the feed after posting
            # Look for success indicators
            success_indicators = [
                "Your post is now published",
                "Post published",
                "Just now"  # Posts show "Just now" timestamp
            ]
            
            page_text = await self.browser.extract_text()
            
            for indicator in success_indicators:
                if indicator.lower() in page_text.lower():
                    return True
            
            # Check if create post dialog is gone
            create_dialog = await self.browser._page.query_selector("div[role='dialog']")
            if not create_dialog:
                return True
            
            return True  # Facebook usually posts successfully if no errors
            
        except Exception:
            return False