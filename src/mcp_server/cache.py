"""Game state caching for MCP server"""

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)


class GameStateCache:
    """Thread-safe cache for game state data"""
    
    def __init__(self, cache_file: Optional[Path] = None):
        """
        Initialize the cache.
        
        Args:
            cache_file: Optional path to persist cache to disk
        """
        self.cache_file = cache_file
        self._state: Optional[Dict[str, Any]] = None
        self._lock = threading.Lock()
        self.last_update: Optional[datetime] = None
        
        # Load from cache file if it exists
        if cache_file and cache_file.exists():
            self._load_from_file()
    
    def update(self, game_state: Dict[str, Any]):
        """
        Update the cached game state.
        
        Args:
            game_state: New game state to cache
        """
        with self._lock:
            self._state = game_state.copy()
            self.last_update = datetime.now()
            
            # Persist to file if configured
            if self.cache_file:
                self._save_to_file()
            
            logger.debug(f"Cache updated: Turn {game_state.get('turn', '?')}")
    
    def get_latest(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest cached game state.
        
        Returns:
            Latest game state or None if no state cached
        """
        with self._lock:
            return self._state.copy() if self._state else None
    
    def clear(self):
        """
        Clear the cache.
        """
        with self._lock:
            self._state = None
            self.last_update = None
            
            # Remove cache file
            if self.cache_file and self.cache_file.exists():
                self.cache_file.unlink()
    
    def _save_to_file(self):
        """
        Save cache to file (called with lock held).
        """
        try:
            cache_data = {
                "state": self._state,
                "last_update": self.last_update.isoformat() if self.last_update else None
            }
            
            # Write atomically
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Move into place
            temp_file.replace(self.cache_file)
            
        except Exception as e:
            logger.error(f"Failed to save cache to file: {e}")
    
    def _load_from_file(self):
        """
        Load cache from file.
        """
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            self._state = cache_data.get("state")
            
            # Parse last update time
            last_update_str = cache_data.get("last_update")
            if last_update_str:
                self.last_update = datetime.fromisoformat(last_update_str)
            
            logger.info(f"Loaded cache from {self.cache_file}")
            
        except Exception as e:
            logger.error(f"Failed to load cache from file: {e}")
            self._state = None
            self.last_update = None