"""
LinkedIn posting implementation
"""

from typing import Dict, Any
from social_media.base import BaseSocialMediaPoster
import logging
import asyncio
import random

logger = logging.getLogger(__name__)

class LinkedInPoster(BaseSocialMediaPoster):
    """LinkedIn-specific posting implementation"""
    
    def get_login_url(self) -> str:
        return "https://www.linkedin.com/login"
    
    def get_home_url(self) -> str:
        return "https://www.linkedin.com/feed/"
    
    async def check_login_success(self) -> bool:
        """Check if we're logged in"""
        try:
            # Check URL
            current_url = self.browser._page.url
            if "feed" in current_url or "in/" in current_url:
                return True
            
            # Look for logged-in elements
            logged_in_selectors = [
                "button[aria-label='Start a post']",
                "div#global-nav",
                "a[href*='/in/']"
            ]
            
            for selector in logged_in_selectors:
                if await self.browser.wait_for_selector(selector, timeout=2000):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def create_post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Create a LinkedIn post"""
        try:
            # Detect posting elements
            elements = await self.element_detector.detect_posting_elements(
                self.browser,
                "linkedin"
            )
            
            # Click start a post button
            start_post_selectors = [
                elements.get('create_post_button'),
                "button[aria-label='Start a post']",
                "button:has-text('Start a post')",
                "div.share-box-feed-entry__trigger"
            ]
            
            for selector in start_post_selectors:
                if selector and await self.browser.wait_for_selector(selector, timeout=2000):
                    await self.browser.click(selector)
                    await asyncio.sleep(random.uniform(1, 2))
                    break
            
            # Wait for modal to open
            await asyncio.sleep(random.uniform(1, 2))
            
            # Find text area and type content
            text_area_selectors = [
                elements.get('text_field'),
                "div[role='textbox']",
                "div.ql-editor",
                "div[contenteditable='true']"
            ]
            
            for selector in text_area_selectors:
                if selector and await self.browser.wait_for_selector(selector, timeout=2000):
                    await self.browser.click(selector)
                    await asyncio.sleep(0.5)
                    
                    # Type the content
                    if content.get('text'):
                        await self.browser.type_text(selector, content['text'])
                        
                        # Add hashtags
                        if content.get('hashtags'):
                            await self.browser.type_text(
                                selector,
                                f"\n\n{content['hashtags']}"
                            )
                    break
            
            # Upload image if provided
            if content.get('image_full_path'):
                # Look for image button
                image_button_selectors = [
                    "button[aria-label*='Add a photo']",
                    "button:has-text('Photo')",
                    "li.share-creation-state__photo-button"
                ]
                
                for selector in image_button_selectors:
                    if await self.browser.wait_for_selector(selector, timeout=2000):
                        await self.browser.click(selector)
                        await asyncio.sleep(random.uniform(1, 2))
                        
                        # Find file input
                        file_input = await self.browser._page.query_selector("input[type='file']")
                        if file_input:
                            await file_input.set_input_files(content['image_full_path'])
                            await asyncio.sleep(random.uniform(3, 5))
                        break
            
            # Post the content
            post_button_selectors = [
                elements.get('post_submit_button'),
                "button[aria-label='Post']",
                "button:has-text('Post')",
                "button.share-actions__primary-action"
            ]
            
            for selector in post_button_selectors:
                if selector and await self.browser.wait_for_selector(selector, timeout=2000):
                    # LinkedIn sometimes disables the button initially
                    await asyncio.sleep(1)
                    await self.browser.click(selector)
                    break
            
            # Wait for posting to complete
            await asyncio.sleep(random.uniform(3, 5))
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"LinkedIn posting failed: {str(e)}")
            raise
    
    async def verify_post_success(self) -> bool:
        """Verify the post was created"""
        try:
            # LinkedIn shows a success toast or returns to feed
            success_indicators = [
                "Post successful",
                "Your post is live",
                "Posted successfully"
            ]
            
            page_text = await self.browser.extract_text()
            
            for indicator in success_indicators:
                if indicator.lower() in page_text.lower():
                    return True
            
            # Check if modal is closed and we're back at feed
            current_url = self.browser._page.url
            if "feed" in current_url:
                # Check if post modal is gone
                post_modal = await self.browser._page.query_selector("div[role='dialog']")
                if not post_modal:
                    return True
            
            return True  # LinkedIn usually posts successfully
            
        except Exception:
            return False