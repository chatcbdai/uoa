"""
Anti-detection bypass scripts for browser automation

These scripts help avoid detection by common bot detection systems.
"""

from pathlib import Path
from typing import List

BYPASS_DIR = Path(__file__).parent

def get_bypass_scripts() -> List[str]:
    """
    Load all bypass scripts from the bypasses directory.
    
    Returns:
        List of JavaScript code strings
    """
    scripts = []
    for script_file in BYPASS_DIR.glob('*.js'):
        with open(script_file, 'r') as f:
            scripts.append(f.read())
    return scripts

def get_bypass_script(name: str) -> str:
    """
    Load a specific bypass script by name.
    
    Args:
        name: Script name without .js extension
        
    Returns:
        JavaScript code as string
    """
    script_path = BYPASS_DIR / f"{name}.js"
    if script_path.exists():
        with open(script_path, 'r') as f:
            return f.read()
    raise FileNotFoundError(f"Bypass script '{name}' not found")

# List available bypass scripts
AVAILABLE_BYPASSES = [
    'navigator_plugins',
    'notification_permission', 
    'pdf_viewer',
    'playwright_fingerprint',
    'screen_props',
    'webdriver_fully',
    'window_chrome'
]

__all__ = ['get_bypass_scripts', 'get_bypass_script', 'AVAILABLE_BYPASSES']