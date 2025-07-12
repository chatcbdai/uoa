# agent/capabilities.py - Agent capability definitions
from typing import Dict, Any, List

CAPABILITIES = {
    "search": {
        "description": "Search the web for information",
        "parameters": {
            "query": {
                "type": "string",
                "description": "The search query",
                "required": True
            },
            "engine": {
                "type": "string",
                "description": "Search engine to use (google, bing, duckduckgo)",
                "required": False,
                "default": "google"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "required": False,
                "default": 10
            }
        },
        "action": "browser.search",
        "examples": [
            "Search for Python web scraping libraries",
            "Find information about climate change",
            "Look up the latest news on AI"
        ]
    },
    "navigate": {
        "description": "Go to a specific website",
        "parameters": {
            "url": {
                "type": "string",
                "description": "The URL to navigate to",
                "required": True
            },
            "wait_for": {
                "type": "string",
                "description": "Element to wait for before proceeding",
                "required": False
            }
        },
        "action": "browser.navigate",
        "examples": [
            "Go to https://example.com",
            "Navigate to amazon.com",
            "Open the GitHub homepage"
        ]
    },
    "scrape": {
        "description": "Extract content from websites",
        "parameters": {
            "url": {
                "type": "string",
                "description": "The URL to scrape",
                "required": True
            },
            "mode": {
                "type": "string",
                "description": "Scraping mode (single, wildcard, full_site, docs)",
                "required": False,
                "default": "single"
            },
            "format": {
                "type": "string",
                "description": "Output format (markdown, json, html)",
                "required": False,
                "default": "markdown"
            },
            "selectors": {
                "type": "array",
                "description": "CSS selectors for specific elements",
                "required": False
            }
        },
        "action": "scraper.scrape",
        "examples": [
            "Scrape the entire Python documentation",
            "Extract product information from this page",
            "Get all articles from the blog"
        ]
    },
    "fill_form": {
        "description": "Fill out web forms",
        "parameters": {
            "fields": {
                "type": "object",
                "description": "Field names and values to fill",
                "required": True
            },
            "submit": {
                "type": "boolean",
                "description": "Whether to submit the form after filling",
                "required": False,
                "default": True
            }
        },
        "action": "browser.fill_form",
        "examples": [
            "Fill out the contact form with my information",
            "Enter username and password in the login form",
            "Complete the registration form"
        ]
    },
    "click": {
        "description": "Click elements on a page",
        "parameters": {
            "selector": {
                "type": "string",
                "description": "CSS selector for the element",
                "required": False
            },
            "text": {
                "type": "string",
                "description": "Text content of the element to click",
                "required": False
            },
            "wait_after": {
                "type": "integer",
                "description": "Milliseconds to wait after clicking",
                "required": False,
                "default": 1000
            }
        },
        "action": "browser.click",
        "examples": [
            "Click on the 'Submit' button",
            "Click the link that says 'Learn More'",
            "Press the download button"
        ]
    },
    "screenshot": {
        "description": "Take screenshots of pages",
        "parameters": {
            "url": {
                "type": "string",
                "description": "URL to screenshot (optional if already on page)",
                "required": False
            },
            "full_page": {
                "type": "boolean",
                "description": "Capture the entire page",
                "required": False,
                "default": False
            },
            "selector": {
                "type": "string",
                "description": "CSS selector for specific element",
                "required": False
            },
            "filename": {
                "type": "string",
                "description": "Custom filename for the screenshot",
                "required": False
            }
        },
        "action": "browser.screenshot",
        "examples": [
            "Take a screenshot of the homepage",
            "Capture the entire article page",
            "Screenshot just the pricing table"
        ]
    },
    "extract_data": {
        "description": "Extract structured data from pages",
        "parameters": {
            "url": {
                "type": "string",
                "description": "URL to extract from",
                "required": True
            },
            "selectors": {
                "type": "object",
                "description": "Named CSS selectors for data extraction",
                "required": True
            },
            "multiple": {
                "type": "boolean",
                "description": "Extract multiple instances (for lists)",
                "required": False,
                "default": False
            }
        },
        "action": "browser.extract",
        "examples": [
            "Extract all product prices and names",
            "Get the author and publication date",
            "Extract table data into structured format"
        ]
    },
    "compare": {
        "description": "Compare information across multiple sites",
        "parameters": {
            "urls": {
                "type": "array",
                "description": "List of URLs to compare",
                "required": True
            },
            "criteria": {
                "type": "array",
                "description": "What to compare (price, features, etc.)",
                "required": True
            },
            "output_format": {
                "type": "string",
                "description": "How to present comparison (table, list)",
                "required": False,
                "default": "table"
            }
        },
        "action": "browser.compare",
        "examples": [
            "Compare laptop prices across Amazon, BestBuy, and Newegg",
            "Compare features of different software tools",
            "Compare news coverage across multiple sites"
        ]
    },
    "monitor": {
        "description": "Monitor websites for changes",
        "parameters": {
            "url": {
                "type": "string",
                "description": "URL to monitor",
                "required": True
            },
            "selector": {
                "type": "string",
                "description": "Specific element to monitor",
                "required": False
            },
            "interval": {
                "type": "integer",
                "description": "Check interval in seconds",
                "required": False,
                "default": 300
            },
            "duration": {
                "type": "integer",
                "description": "Total monitoring duration in seconds",
                "required": False,
                "default": 3600
            }
        },
        "action": "browser.monitor",
        "examples": [
            "Monitor the price of this product",
            "Watch for new articles on the blog",
            "Alert me when the page content changes"
        ]
    },
    "download": {
        "description": "Download files from the web",
        "parameters": {
            "url": {
                "type": "string",
                "description": "URL of the file to download",
                "required": True
            },
            "filename": {
                "type": "string",
                "description": "Custom filename for saving",
                "required": False
            },
            "directory": {
                "type": "string",
                "description": "Directory to save the file",
                "required": False
            }
        },
        "action": "browser.download",
        "examples": [
            "Download the PDF report",
            "Save all images from the gallery",
            "Download the dataset file"
        ]
    }
}

def get_capability_names() -> List[str]:
    """Get list of all capability names"""
    return list(CAPABILITIES.keys())

def get_capability_description(name: str) -> str:
    """Get description for a specific capability"""
    return CAPABILITIES.get(name, {}).get("description", "")

def get_capability_parameters(name: str) -> Dict[str, Any]:
    """Get parameters for a specific capability"""
    return CAPABILITIES.get(name, {}).get("parameters", {})

def get_capability_examples(name: str) -> List[str]:
    """Get examples for a specific capability"""
    return CAPABILITIES.get(name, {}).get("examples", [])

def validate_parameters(capability: str, parameters: Dict[str, Any]) -> bool:
    """Validate parameters for a capability"""
    if capability not in CAPABILITIES:
        return False
    
    cap_params = CAPABILITIES[capability]["parameters"]
    
    # Check required parameters
    for param_name, param_info in cap_params.items():
        if param_info.get("required", False) and param_name not in parameters:
            return False
    
    return True

def get_capabilities_summary() -> str:
    """Get a human-readable summary of all capabilities"""
    summary = "Available capabilities:\n\n"
    
    for name, info in CAPABILITIES.items():
        summary += f"**{name}**: {info['description']}\n"
        examples = info.get('examples', [])
        if examples:
            summary += f"   Examples: {examples[0]}\n"
        summary += "\n"
    
    return summary