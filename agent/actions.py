# agent/actions.py - Action definitions and mappings
import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class Action:
    """Represents a browser action"""
    name: str
    parameters: Dict[str, Any]
    description: str = ""
    priority: int = 1

class ActionMapper:
    """Maps natural language intents to browser actions"""
    
    ACTION_PATTERNS = {
        "search for": ("search", ["query"]),
        "search": ("search", ["query"]),
        "find information about": ("search", ["query"]),
        "look up": ("search", ["query"]),
        "go to": ("navigate", ["url"]),
        "navigate to": ("navigate", ["url"]),
        "open": ("navigate", ["url"]),
        "visit": ("navigate", ["url"]),
        "click on": ("click", ["selector", "text"]),
        "click": ("click", ["selector", "text"]),
        "press": ("click", ["selector", "text"]),
        "fill out": ("fill_form", ["fields"]),
        "fill in": ("fill_form", ["fields"]),
        "enter": ("fill_form", ["fields"]),
        "type": ("fill_form", ["fields"]),
        "download": ("download", ["url", "filename"]),
        "save": ("download", ["url", "filename"]),
        "take screenshot": ("screenshot", ["url"]),
        "screenshot": ("screenshot", ["url"]),
        "capture": ("screenshot", ["url"]),
        "scrape": ("scrape", ["url", "options"]),
        "extract": ("extract", ["url", "selectors"]),
        "get data from": ("extract", ["url", "selectors"]),
        "compare": ("compare", ["urls", "criteria"]),
        "monitor": ("monitor", ["url", "interval"]),
        "watch": ("monitor", ["url", "interval"])
    }
    
    URL_PATTERN = re.compile(
        r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.(com|org|net|edu|gov|io|co|uk)[^\s]*)'
    )
    
    def __init__(self):
        self.action_history = []
    
    def map_intent_to_action(self, intent: str) -> Dict[str, Any]:
        """Map natural language intent to browser action"""
        intent_lower = intent.lower().strip()
        
        # Try pattern matching first
        for pattern, (action_name, params) in self.ACTION_PATTERNS.items():
            if pattern in intent_lower:
                parameters = self._extract_parameters(intent, action_name, params)
                
                action = {
                    "action": action_name,
                    "parameters": parameters,
                    "original_intent": intent
                }
                
                self.action_history.append(action)
                return action
        
        # Default to navigation if URL is present
        urls = self.URL_PATTERN.findall(intent)
        if urls:
            return {
                "action": "navigate",
                "parameters": {"url": urls[0]},
                "original_intent": intent
            }
        
        # Default to search if no pattern matches
        return {
            "action": "search",
            "parameters": {"query": intent},
            "original_intent": intent
        }
    
    def _extract_parameters(self, intent: str, action: str, param_names: List[str]) -> Dict[str, Any]:
        """Extract parameters from intent based on action type"""
        parameters = {}
        
        if action == "search":
            # Extract search query
            query = self._extract_search_query(intent)
            parameters["query"] = query
            parameters["engine"] = "google"  # default
            
        elif action == "navigate":
            # Extract URL
            urls = self.URL_PATTERN.findall(intent)
            if urls:
                parameters["url"] = self._normalize_url(urls[0])
            else:
                # Try to extract domain from intent
                domain = self._extract_domain(intent)
                if domain:
                    parameters["url"] = f"https://{domain}"
                    
        elif action == "click":
            # Extract text or selector
            text = self._extract_quoted_text(intent)
            if text:
                parameters["text"] = text
            else:
                parameters["selector"] = self._guess_selector(intent)
                
        elif action == "fill_form":
            # Extract form fields
            fields = self._extract_form_fields(intent)
            parameters["fields"] = fields
            
        elif action == "screenshot":
            # Extract URL if present
            urls = self.URL_PATTERN.findall(intent)
            if urls:
                parameters["url"] = self._normalize_url(urls[0])
            parameters["full_page"] = "full" in intent.lower()
            
        elif action == "scrape" or action == "extract":
            # Extract URL and options
            urls = self.URL_PATTERN.findall(intent)
            if urls:
                parameters["url"] = self._normalize_url(urls[0])
            
            # Determine scraping mode
            if "entire" in intent or "whole" in intent:
                parameters["mode"] = "full_site"
            elif "documentation" in intent or "docs" in intent:
                parameters["mode"] = "docs"
            else:
                parameters["mode"] = "single"
        
        return parameters
    
    def _extract_search_query(self, intent: str) -> str:
        """Extract search query from intent"""
        # Remove common search phrases
        query = intent.lower()
        for phrase in ["search for", "find information about", "look up", "search"]:
            query = query.replace(phrase, "").strip()
        
        # Remove quotes if present
        if query.startswith('"') and query.endswith('"'):
            query = query[1:-1]
        
        return query
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to ensure proper format"""
        if not url.startswith(('http://', 'https://')):
            if url.startswith('www.'):
                return f'https://{url}'
            else:
                return f'https://www.{url}'
        return url
    
    def _extract_domain(self, intent: str) -> Optional[str]:
        """Try to extract a domain name from intent"""
        # Look for common domain patterns
        words = intent.split()
        for word in words:
            if '.' in word and not word.startswith('.') and not word.endswith('.'):
                return word
        
        # Look for company names that might be domains
        companies = ["amazon", "google", "facebook", "twitter", "github", "stackoverflow"]
        for company in companies:
            if company in intent.lower():
                return f"{company}.com"
        
        return None
    
    def _extract_quoted_text(self, intent: str) -> Optional[str]:
        """Extract text in quotes"""
        match = re.search(r'"([^"]+)"', intent)
        if match:
            return match.group(1)
        
        match = re.search(r"'([^']+)'", intent)
        if match:
            return match.group(1)
        
        return None
    
    def _guess_selector(self, intent: str) -> str:
        """Guess a CSS selector based on intent"""
        intent_lower = intent.lower()
        
        if "button" in intent_lower:
            return "button"
        elif "link" in intent_lower:
            return "a"
        elif "input" in intent_lower or "field" in intent_lower:
            return "input"
        elif "submit" in intent_lower:
            return "button[type='submit'], input[type='submit']"
        else:
            return "*"  # fallback
    
    def _extract_form_fields(self, intent: str) -> Dict[str, str]:
        """Extract form field values from intent"""
        fields = {}
        
        # Look for common patterns like "email: test@example.com"
        pattern = re.compile(r'(\w+):\s*([^\s,]+)')
        matches = pattern.findall(intent)
        for field_name, value in matches:
            fields[field_name.lower()] = value
        
        # Look for email addresses
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        emails = email_pattern.findall(intent)
        if emails:
            fields["email"] = emails[0]
        
        return fields
    
    def get_action_history(self) -> List[Dict[str, Any]]:
        """Get history of mapped actions"""
        return self.action_history
    
    def clear_history(self):
        """Clear action history"""
        self.action_history = []