"""
Storage adapters for the undetectable toolkit
"""

from .sqlite import SQLiteStorage, StorageError

__all__ = ['SQLiteStorage', 'StorageError']