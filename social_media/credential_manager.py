"""
Secure credential management using keyring + Fernet
"""

import json
import keyring
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Dict, Optional
import logging

from .exceptions import CredentialError

logger = logging.getLogger(__name__)

class CredentialManager:
    """Manages encrypted credentials for social media platforms"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path / "credentials"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.service_name = "undetectable_toolkit_social"
        self._fernet = None
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key from keyring"""
        # Try to get existing key from keyring
        key = keyring.get_password(self.service_name, "master_key")
        
        if not key:
            # Generate new key
            key = Fernet.generate_key().decode()
            keyring.set_password(self.service_name, "master_key", key)
            logger.info("Created new master encryption key")
        
        return key.encode()
    
    @property
    def fernet(self) -> Fernet:
        """Get Fernet instance with lazy loading"""
        if not self._fernet:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def save_credentials(self, platform: str, credentials: Dict[str, str]) -> None:
        """Save encrypted credentials for a platform"""
        try:
            # Encrypt the credentials
            encrypted = self.fernet.encrypt(json.dumps(credentials).encode())
            
            # Save to file
            cred_file = self.storage_path / f"{platform}.enc"
            cred_file.write_bytes(encrypted)
            
            logger.info(f"Saved credentials for {platform}")
        except Exception as e:
            raise CredentialError(f"Failed to save credentials: {str(e)}")
    
    def get_credentials(self, platform: str) -> Optional[Dict[str, str]]:
        """Get decrypted credentials for a platform"""
        try:
            cred_file = self.storage_path / f"{platform}.enc"
            
            if not cred_file.exists():
                return None
            
            # Read and decrypt
            encrypted = cred_file.read_bytes()
            decrypted = self.fernet.decrypt(encrypted)
            
            return json.loads(decrypted.decode())
        except Exception as e:
            logger.error(f"Failed to get credentials for {platform}: {str(e)}")
            return None
    
    def delete_credentials(self, platform: str) -> bool:
        """Delete credentials for a platform"""
        try:
            cred_file = self.storage_path / f"{platform}.enc"
            if cred_file.exists():
                cred_file.unlink()
                logger.info(f"Deleted credentials for {platform}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete credentials: {str(e)}")
            return False