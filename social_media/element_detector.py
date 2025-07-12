"""
Dynamic element detection using LLM
"""

import base64
from typing import Dict, Optional, List
from llm.base import Message
import logging

logger = logging.getLogger(__name__)

class ElementDetector:
    """Uses LLM to dynamically detect page elements"""
    
    ELEMENT_DETECTION_PROMPT = """Analyze this webpage and identify the CSS selectors for the requested elements.

Page URL: {url}
Platform: {platform}
Task: {task}

Required elements to find:
{elements}

Return a JSON object with the CSS selectors. Example:
{{
    "username_field": "input[name='username']",
    "password_field": "input[type='password']",
    "submit_button": "button[type='submit']"
}}

If an element cannot be found, use null as the value.
Only return the JSON object, no other text."""

    def __init__(self, llm_client):
        self.llm = llm_client
    
    async def detect_login_elements(self, browser, platform: str) -> Dict[str, str]:
        """Detect login form elements"""
        try:
            # Take screenshot
            screenshot = await browser.take_screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            # Get page URL
            current_url = browser._page.url
            
            # Build prompt
            prompt = self.ELEMENT_DETECTION_PROMPT.format(
                url=current_url,
                platform=platform,
                task="login",
                elements="""- username_field: The username/email input field
- password_field: The password input field  
- submit_button: The login/submit button
- remember_me_checkbox: (optional) Remember me checkbox
- error_message: (optional) Error message container"""
            )
            
            # Ask LLM
            messages = [
                Message(role="user", content=prompt),
                Message(role="user", content=f"Screenshot: data:image/png;base64,{screenshot_b64}")
            ]
            
            response = await self.llm.generate(messages, temperature=0.1)
            
            # Parse JSON response
            import json
            selectors = json.loads(response.content.strip())
            
            logger.info(f"Detected login elements for {platform}: {selectors}")
            return selectors
            
        except Exception as e:
            logger.error(f"Element detection failed: {str(e)}")
            # Fallback to common selectors
            return self._get_fallback_selectors(platform, "login")
    
    async def detect_posting_elements(self, browser, platform: str) -> Dict[str, str]:
        """Detect posting form elements"""
        try:
            # Similar to login detection but for posting elements
            screenshot = await browser.take_screenshot(full_page=False)
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            current_url = browser._page.url
            
            prompt = self.ELEMENT_DETECTION_PROMPT.format(
                url=current_url,
                platform=platform,
                task="create_post",
                elements="""- create_post_button: Button to start creating a new post
- text_field: Text input area for post content
- image_upload_button: Button to upload images
- post_submit_button: Button to publish the post
- privacy_selector: (optional) Privacy/audience selector"""
            )
            
            messages = [
                Message(role="user", content=prompt),
                Message(role="user", content=f"Screenshot: data:image/png;base64,{screenshot_b64}")
            ]
            
            response = await self.llm.generate(messages, temperature=0.1)
            
            import json
            selectors = json.loads(response.content.strip())
            
            logger.info(f"Detected posting elements for {platform}: {selectors}")
            return selectors
            
        except Exception as e:
            logger.error(f"Posting element detection failed: {str(e)}")
            return self._get_fallback_selectors(platform, "post")
    
    def _get_fallback_selectors(self, platform: str, task: str) -> Dict[str, str]:
        """Get fallback selectors if LLM detection fails"""
        # Common patterns that often work
        fallbacks = {
            "instagram": {
                "login": {
                    "username_field": "input[name='username']",
                    "password_field": "input[name='password']",
                    "submit_button": "button[type='submit']"
                },
                "post": {
                    "create_post_button": "svg[aria-label='New post']",
                    "text_field": "textarea[aria-label='Caption']",
                    "post_submit_button": "button:has-text('Share')"
                }
            },
            "twitter": {
                "login": {
                    "username_field": "input[autocomplete='username']",
                    "password_field": "input[name='password']",
                    "submit_button": "div[data-testid='LoginForm_Login_Button']"
                },
                "post": {
                    "create_post_button": "a[aria-label='Post']",
                    "text_field": "div[data-testid='tweetTextarea_0']",
                    "post_submit_button": "button[data-testid='tweetButtonInline']"
                }
            }
            # Add more platforms...
        }
        
        return fallbacks.get(platform, {}).get(task, {})