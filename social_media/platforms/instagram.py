"""
Instagram posting implementation
"""

from typing import Dict, Any
from social_media.base import BaseSocialMediaPoster
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class InstagramPoster(BaseSocialMediaPoster):
    """Instagram-specific posting implementation"""
    
    def get_login_url(self) -> str:
        return "https://www.instagram.com/accounts/login/"
    
    def get_home_url(self) -> str:
        return "https://www.instagram.com/"
    
    async def check_login_success(self) -> bool:
        """Check if we're logged in by looking for profile icon"""
        try:
            # Check URL first
            current_url = self.browser._page.url
            if "login" in current_url or "accounts" in current_url:
                return False
            
            # Look for profile elements
            profile_selectors = [
                "img[alt*='profile']",
                "div[role='menuitem']",
                "svg[aria-label='Profile']"
            ]
            
            for selector in profile_selectors:
                if await self.browser.wait_for_selector(selector, timeout=2000):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def create_post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Create an Instagram post"""
        try:
            # Detect posting elements
            elements = await self.element_detector.detect_posting_elements(
                self.browser,
                "instagram"
            )
            
            # Upload image if provided
            if content.get('image_full_path'):
                # Click file input or drag-drop area
                file_input = await self.browser._page.query_selector("input[type='file']")
                if file_input:
                    await file_input.set_input_files(content['image_full_path'])
                    await asyncio.sleep(random.uniform(2, 4))
                
                # Click Next buttons through the flow
                next_buttons = await self.browser._page.query_selector_all("button:has-text('Next')")
                for button in next_buttons:
                    await button.click()
                    await asyncio.sleep(random.uniform(1, 2))
            
            # Add caption
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
            
            # Share the post
            share_selectors = [
                "button:has-text('Share')",
                "button:has-text('Post')",
                elements.get('post_submit_button')
            ]
            
            for selector in share_selectors:
                if selector and await self.browser.wait_for_selector(selector, timeout=2000):
                    await self.browser.click(selector)
                    break
            
            # Wait for posting to complete
            await asyncio.sleep(random.uniform(3, 5))
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Instagram posting failed: {str(e)}")
            raise
    
    async def verify_post_success(self) -> bool:
        """Verify the post was created"""
        try:
            # Look for success indicators
            success_indicators = [
                "Your post has been shared",
                "Post shared",
                "View post"
            ]
            
            page_text = await self.browser.extract_text()
            
            for indicator in success_indicators:
                if indicator.lower() in page_text.lower():
                    return True
            
            # Check if we're back at the home feed
            current_url = self.browser._page.url
            if current_url == self.get_home_url():
                return True
            
            return False
            
        except Exception:
            return False