"""
Base class for social media platforms
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
import logging
import asyncio
import random
from datetime import datetime

from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)

class BaseSocialMediaPoster(ABC):
    """Abstract base class for social media posting"""
    
    def __init__(self, browser, credential_manager, element_detector):
        self.browser = browser
        self.credential_manager = credential_manager
        self.element_detector = element_detector
        self.platform_name = self.__class__.__name__.replace('Poster', '').lower()
        self.is_logged_in = False
    
    async def post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Main posting workflow"""
        try:
            # Step 1: Login if needed
            if not self.is_logged_in:
                await self.login()
            
            # Step 2: Navigate to posting area
            await self.navigate_to_post_creation()
            
            # Step 3: Create the post
            result = await self.create_post(content)
            
            # Step 4: Verify posting
            success = await self.verify_post_success()
            
            return {
                'success': success,
                'platform': self.platform_name,
                'post_url': result.get('url'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Posting failed on {self.platform_name}: {str(e)}")
            return {
                'success': False,
                'platform': self.platform_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def login(self) -> bool:
        """Login to the platform"""
        try:
            # Get credentials
            creds = self.credential_manager.get_credentials(self.platform_name)
            if not creds:
                raise AuthenticationError(f"No credentials found for {self.platform_name}")
            
            # Navigate to login page
            await self.browser.navigate(self.get_login_url())
            
            # Wait for page to load
            await asyncio.sleep(random.uniform(2, 4))
            
            # Detect login elements
            elements = await self.element_detector.detect_login_elements(
                self.browser, 
                self.platform_name
            )
            
            # Fill login form
            if elements.get('username_field'):
                await self.browser.type_text(
                    elements['username_field'], 
                    creds['username']
                )
            
            if elements.get('password_field'):
                await self.browser.type_text(
                    elements['password_field'],
                    creds['password']
                )
            
            # Click submit
            if elements.get('submit_button'):
                await self.browser.click(elements['submit_button'])
            
            # Wait for login to complete
            await asyncio.sleep(random.uniform(3, 5))
            
            # Check if login successful
            self.is_logged_in = await self.check_login_success()
            
            if not self.is_logged_in:
                raise AuthenticationError(f"Login failed for {self.platform_name}")
            
            logger.info(f"Successfully logged in to {self.platform_name}")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise
    
    async def navigate_to_post_creation(self):
        """Navigate to post creation area"""
        # Add human-like delay
        await asyncio.sleep(random.uniform(1, 3))
        
        # Navigate to home/feed first
        await self.browser.navigate(self.get_home_url())
        await asyncio.sleep(random.uniform(2, 4))
        
        # Find and click create post button
        elements = await self.element_detector.detect_posting_elements(
            self.browser,
            self.platform_name
        )
        
        if elements.get('create_post_button'):
            await self.browser.click(elements['create_post_button'])
            await asyncio.sleep(random.uniform(1, 2))
    
    @abstractmethod
    def get_login_url(self) -> str:
        """Get platform login URL"""
        pass
    
    @abstractmethod
    def get_home_url(self) -> str:
        """Get platform home URL"""
        pass
    
    @abstractmethod
    async def check_login_success(self) -> bool:
        """Check if login was successful"""
        pass
    
    @abstractmethod
    async def create_post(self, content: Dict[str, str]) -> Dict[str, Any]:
        """Create a post with given content"""
        pass
    
    @abstractmethod
    async def verify_post_success(self) -> bool:
        """Verify the post was created successfully"""
        pass