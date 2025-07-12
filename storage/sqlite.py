"""
SQLite storage adapter for the undetectable toolkit
"""

import sqlite3
import threading
import queue
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any, Set
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

class StorageError(Exception):
    """Custom exception for storage-related errors"""
    pass

class SQLiteStorage:
    """SQLite storage for scraped content"""
    
    def __init__(self, db_path: Optional[Path] = None, max_connections: int = 3):
        """
        Initialize SQLite storage.
        
        Args:
            db_path: Path to SQLite database file
            max_connections: Maximum number of concurrent connections
        """
        if db_path is None:
            db_path = Path.cwd() / "storage" / "scraping.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.max_connections = max_connections
        self._closed = False
        
        # Connection pool
        self._pool = queue.Queue(maxsize=max_connections)
        self._active_connections: Set[sqlite3.Connection] = set()
        self._pool_lock = threading.Lock()
        
        # Initialize pool and database
        self._initialize_pool()
        with self._get_connection() as conn:
            self._setup_database(conn)
    
    def _initialize_pool(self) -> None:
        """Initialize connection pool"""
        for _ in range(self.max_connections):
            self._add_connection_to_pool()
    
    def _add_connection_to_pool(self) -> None:
        """Add a new connection to the pool"""
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                isolation_level=None,  # Autocommit mode
                check_same_thread=False  # Allow connection to be used across threads
            )
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=30000")
            conn.execute("PRAGMA synchronous=NORMAL")
            self._pool.put(conn, block=False)
        except queue.Full:
            conn.close()
        except Exception as e:
            raise StorageError(f"Failed to create database connection: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Get a connection from the pool"""
        if self._closed:
            raise StorageError("Storage system is closed")
        
        connection = None
        try:
            connection = self._pool.get(timeout=30.0)
            with self._pool_lock:
                self._active_connections.add(connection)
            yield connection
        finally:
            if connection is not None:
                with self._pool_lock:
                    self._active_connections.discard(connection)
                if not self._closed:
                    try:
                        self._pool.put(connection, timeout=1.0)
                    except queue.Full:
                        connection.close()
                else:
                    connection.close()
    
    def _setup_database(self, connection: sqlite3.Connection) -> None:
        """Setup database schema"""
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS scraped_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                content_type TEXT,
                content TEXT,
                html TEXT,
                metadata TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(url)
            );
            
            CREATE INDEX IF NOT EXISTS idx_url ON scraped_content(url);
            CREATE INDEX IF NOT EXISTS idx_scraped_at ON scraped_content(scraped_at);
            
            CREATE TABLE IF NOT EXISTS scraped_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_url TEXT NOT NULL,
                target_url TEXT NOT NULL,
                link_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_url) REFERENCES scraped_content(url)
            );
            
            CREATE INDEX IF NOT EXISTS idx_source_url ON scraped_links(source_url);
            CREATE INDEX IF NOT EXISTS idx_target_url ON scraped_links(target_url);
        """)
    
    def save_content(
        self,
        url: str,
        content: str,
        html: str = None,
        title: str = None,
        content_type: str = "text",
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Save scraped content to database.
        
        Args:
            url: URL of the scraped content
            content: Processed content (e.g., markdown)
            html: Original HTML content
            title: Page title
            content_type: Type of content (text, markdown, etc.)
            metadata: Additional metadata
        """
        if self._closed:
            raise StorageError("Storage system is closed")
        
        try:
            metadata_json = json.dumps(metadata or {})
            
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO scraped_content 
                    (url, title, content_type, content, html, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (url, title, content_type, content, html, metadata_json))
                
            logger.info(f"Saved content for URL: {url}")
            
        except Exception as e:
            logger.error(f"Failed to save content: {str(e)}")
            raise StorageError(f"Failed to save content: {str(e)}")
    
    def save_links(self, source_url: str, links: list) -> None:
        """
        Save links found on a page.
        
        Args:
            source_url: URL where links were found
            links: List of link dictionaries with 'url' and optional 'text'
        """
        if self._closed:
            raise StorageError("Storage system is closed")
        
        try:
            with self._get_connection() as conn:
                # Delete existing links for this source
                conn.execute("DELETE FROM scraped_links WHERE source_url = ?", (source_url,))
                
                # Insert new links
                for link in links:
                    if isinstance(link, dict):
                        target_url = link.get('url', link.get('href'))
                        link_text = link.get('text', '')
                    else:
                        target_url = str(link)
                        link_text = ''
                    
                    if target_url:
                        conn.execute("""
                            INSERT INTO scraped_links (source_url, target_url, link_text)
                            VALUES (?, ?, ?)
                        """, (source_url, target_url, link_text))
                
            logger.debug(f"Saved {len(links)} links for URL: {source_url}")
            
        except Exception as e:
            logger.error(f"Failed to save links: {str(e)}")
            raise StorageError(f"Failed to save links: {str(e)}")
    
    def get_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve content by URL.
        
        Args:
            url: URL to retrieve
            
        Returns:
            Dictionary with content data or None if not found
        """
        if self._closed:
            raise StorageError("Storage system is closed")
        
        try:
            with self._get_connection() as conn:
                result = conn.execute("""
                    SELECT url, title, content_type, content, html, metadata, 
                           scraped_at, updated_at
                    FROM scraped_content
                    WHERE url = ?
                """, (url,)).fetchone()
                
                if result:
                    return {
                        'url': result[0],
                        'title': result[1],
                        'content_type': result[2],
                        'content': result[3],
                        'html': result[4],
                        'metadata': json.loads(result[5] or '{}'),
                        'scraped_at': result[6],
                        'updated_at': result[7]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve content: {str(e)}")
            raise StorageError(f"Failed to retrieve content: {str(e)}")
    
    def get_links(self, source_url: str) -> list:
        """
        Get all links from a source URL.
        
        Args:
            source_url: URL to get links from
            
        Returns:
            List of link dictionaries
        """
        if self._closed:
            raise StorageError("Storage system is closed")
        
        try:
            with self._get_connection() as conn:
                results = conn.execute("""
                    SELECT target_url, link_text
                    FROM scraped_links
                    WHERE source_url = ?
                """, (source_url,)).fetchall()
                
                return [
                    {'url': row[0], 'text': row[1]}
                    for row in results
                ]
                
        except Exception as e:
            logger.error(f"Failed to retrieve links: {str(e)}")
            raise StorageError(f"Failed to retrieve links: {str(e)}")
    
    def list_urls(self, limit: int = 100, offset: int = 0) -> list:
        """
        List all scraped URLs.
        
        Args:
            limit: Maximum number of URLs to return
            offset: Number of URLs to skip
            
        Returns:
            List of URL strings
        """
        if self._closed:
            raise StorageError("Storage system is closed")
        
        try:
            with self._get_connection() as conn:
                results = conn.execute("""
                    SELECT url FROM scraped_content
                    ORDER BY scraped_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset)).fetchall()
                
                return [row[0] for row in results]
                
        except Exception as e:
            logger.error(f"Failed to list URLs: {str(e)}")
            raise StorageError(f"Failed to list URLs: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        if self._closed:
            raise StorageError("Storage system is closed")
        
        try:
            with self._get_connection() as conn:
                # Get content count
                content_count = conn.execute(
                    "SELECT COUNT(*) FROM scraped_content"
                ).fetchone()[0]
                
                # Get link count
                link_count = conn.execute(
                    "SELECT COUNT(*) FROM scraped_links"
                ).fetchone()[0]
                
                # Get date range
                date_range = conn.execute("""
                    SELECT MIN(scraped_at), MAX(scraped_at)
                    FROM scraped_content
                """).fetchone()
                
                return {
                    'content_count': content_count,
                    'link_count': link_count,
                    'first_scraped': date_range[0] if date_range[0] else None,
                    'last_scraped': date_range[1] if date_range[1] else None,
                    'database_path': str(self.db_path)
                }
                
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            raise StorageError(f"Failed to get stats: {str(e)}")
    
    def close(self) -> None:
        """Close all database connections"""
        with self._pool_lock:
            if self._closed:
                return
            
            self._closed = True
            
            # Close pooled connections
            while True:
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except queue.Empty:
                    break
                except Exception:
                    pass
            
            # Close active connections
            for conn in list(self._active_connections):
                try:
                    conn.close()
                except Exception:
                    pass
            
            self._active_connections.clear()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()