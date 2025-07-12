"""
Network utilities for rate limiting and anti-detection
"""

import asyncio
import time
import random
import logging
from typing import Dict, Optional
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter to control request frequency.
    Implements token bucket algorithm with jitter.
    """
    
    def __init__(self, rate_limit: float = 1.0, burst: int = 5):
        """
        Initialize rate limiter.
        
        Args:
            rate_limit: Requests per second
            burst: Maximum burst size (tokens in bucket)
        """
        self.rate_limit = rate_limit
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self._lock = asyncio.Lock()
        
        # Track request history for adaptive rate limiting
        self.request_history = deque(maxlen=100)
    
    async def acquire(self, jitter: bool = True):
        """
        Acquire permission to make a request.
        Blocks until rate limit allows the request.
        
        Args:
            jitter: Add random jitter to make timing more human-like
        """
        async with self._lock:
            now = time.time()
            
            # Refill tokens based on time passed
            time_passed = now - self.last_update
            self.tokens = min(
                self.burst,
                self.tokens + time_passed * self.rate_limit
            )
            self.last_update = now
            
            # Wait if no tokens available
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) / self.rate_limit
                
                # Add jitter to avoid patterns
                if jitter:
                    sleep_time += random.uniform(0.1, 0.5)
                
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
                
                # Update tokens after sleep
                self.tokens = 1
                self.last_update = time.time()
            
            # Consume token
            self.tokens -= 1
            
            # Record request
            self.request_history.append(datetime.now())
            
            # Additional random delay for human-like behavior
            if jitter:
                await asyncio.sleep(random.uniform(0.1, 0.3))
    
    def get_current_rate(self) -> float:
        """Get current request rate (requests per second)"""
        if len(self.request_history) < 2:
            return 0.0
        
        # Calculate rate from recent requests
        recent = list(self.request_history)[-10:]
        if len(recent) < 2:
            return 0.0
        
        time_span = (recent[-1] - recent[0]).total_seconds()
        if time_span == 0:
            return 0.0
        
        return len(recent) / time_span
    
    def adjust_rate(self, factor: float):
        """
        Adjust rate limit dynamically.
        
        Args:
            factor: Multiplication factor (e.g., 0.5 to halve rate)
        """
        self.rate_limit = max(0.1, self.rate_limit * factor)
        logger.info(f"Adjusted rate limit to {self.rate_limit} requests/second")

class NetworkManager:
    """
    Manages network behavior for anti-detection.
    Handles headers, delays, and request patterns.
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        
        # Desktop browser headers
        self.desktop_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Mobile browser headers
        self.mobile_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def get_random_user_agent(self, device_type: str = "desktop") -> str:
        """
        Generate realistic user agent string.
        
        Args:
            device_type: "desktop" or "mobile"
        """
        if device_type == "mobile":
            agents = [
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
                'Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
            ]
        else:
            chrome_versions = ['122.0.0.0', '121.0.0.0', '120.0.0.0', '119.0.0.0']
            firefox_versions = ['122.0', '121.0', '120.0']
            
            os_strings = [
                'Macintosh; Intel Mac OS X 10_15_7',
                'Windows NT 10.0; Win64; x64',
                'X11; Linux x86_64',
                'Windows NT 10.0; WOW64',
                'X11; Ubuntu; Linux x86_64'
            ]
            
            # 70% Chrome, 20% Firefox, 10% Safari
            browser_choice = random.random()
            
            if browser_choice < 0.7:  # Chrome
                version = random.choice(chrome_versions)
                os_str = random.choice(os_strings)
                return f'Mozilla/5.0 ({os_str}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36'
            elif browser_choice < 0.9:  # Firefox
                version = random.choice(firefox_versions)
                os_str = random.choice(os_strings[:3])  # Firefox less common on some OS
                return f'Mozilla/5.0 ({os_str}; rv:{version}) Gecko/20100101 Firefox/{version}'
            else:  # Safari (Mac only)
                return 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        
        return random.choice(agents if device_type == "mobile" else [])
    
    def generate_headers(
        self,
        url: str,
        device_type: str = "desktop",
        referer: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate realistic browser headers.
        
        Args:
            url: Target URL
            device_type: "desktop" or "mobile"
            referer: Custom referer or None for auto-generation
        """
        headers = (
            self.mobile_headers.copy()
            if device_type == "mobile"
            else self.desktop_headers.copy()
        )
        
        # Set user agent
        headers['User-Agent'] = self.get_random_user_agent(device_type)
        
        # Set referer
        if referer:
            headers['Referer'] = referer
        elif random.random() < 0.7:  # 70% chance to have referer
            # Common referer sources
            referer_sources = [
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/',
                f'https://{url.split("/")[2]}/',  # Same domain
            ]
            headers['Referer'] = random.choice(referer_sources)
        
        # Randomize DNT header
        if random.random() < 0.3:  # 30% of users have DNT
            headers['DNT'] = '1'
        
        # Add sec-ch-ua headers for Chrome (if using Chrome UA)
        if 'Chrome' in headers.get('User-Agent', ''):
            version = headers['User-Agent'].split('Chrome/')[1].split(' ')[0].split('.')[0]
            headers['sec-ch-ua'] = f'"Chromium";v="{version}", "Not(A:Brand";v="24", "Google Chrome";v="{version}"'
            headers['sec-ch-ua-mobile'] = '?1' if device_type == "mobile" else '?0'
            headers['sec-ch-ua-platform'] = '"Android"' if 'Android' in headers['User-Agent'] else '"Windows"'
        
        return headers
    
    def get_request_delay(self, base_delay: float = 1.0) -> float:
        """
        Generate realistic delay between requests.
        
        Args:
            base_delay: Base delay in seconds
            
        Returns:
            Delay in seconds with human-like randomness
        """
        # Human-like delay patterns
        delay_patterns = [
            lambda: random.uniform(base_delay * 0.5, base_delay * 1.5),  # Normal browsing
            lambda: random.uniform(base_delay * 0.2, base_delay * 0.8),   # Fast browsing
            lambda: random.uniform(base_delay * 1.5, base_delay * 3.0),   # Slow/careful browsing
            lambda: base_delay + random.expovariate(1/base_delay),        # Reading pattern
        ]
        
        pattern = random.choice(delay_patterns)
        delay = pattern()
        
        # Occasionally add longer pauses (reading, distracted, etc.)
        if random.random() < 0.1:  # 10% chance
            delay += random.uniform(5, 15)
        
        return max(0.1, delay)  # Minimum 100ms delay
    
    async def wait_with_jitter(self, seconds: float):
        """
        Wait with random jitter to avoid patterns.
        
        Args:
            seconds: Base wait time
        """
        jittered_time = seconds + random.uniform(-0.2 * seconds, 0.2 * seconds)
        await asyncio.sleep(max(0.1, jittered_time))
    
    def should_abort_resource(self, resource_type: str, url: str) -> bool:
        """
        Determine if a resource should be blocked to save bandwidth.
        
        Args:
            resource_type: Type of resource (image, stylesheet, etc.)
            url: Resource URL
            
        Returns:
            True if resource should be blocked
        """
        # Always block these types
        always_block = {'media', 'font', 'websocket', 'manifest', 'eventsource'}
        if resource_type in always_block:
            return True
        
        # Conditionally block based on URL patterns
        if resource_type == 'image':
            # Block tracking pixels and ads
            block_patterns = ['doubleclick', 'googleadservices', 'googlesyndication', 
                            'google-analytics', 'googletagmanager', 'facebook.com/tr',
                            'amazon-adsystem', '.gif', '1x1', 'pixel']
            return any(pattern in url.lower() for pattern in block_patterns)
        
        if resource_type == 'script':
            # Block known tracking/ad scripts
            block_patterns = ['google-analytics', 'googletagmanager', 'doubleclick',
                            'googleadservices', 'google-ads', 'facebook.com/tr',
                            'hotjar', 'clarity.ms', 'segment.io']
            return any(pattern in url.lower() for pattern in block_patterns)
        
        return False