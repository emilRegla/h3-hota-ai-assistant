"""Save file parser for Heroes III using h3sed library"""

import gzip
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from h3sed import Savegame
except ImportError:
    # Fallback for development without h3sed
    Savegame = None

from .models import GameState, Hero, Town, Tile


logger = logging.getLogger(__name__)


class SaveParser:
    """Parses Heroes III save files and extracts game state"""
    
    def __init__(self):
        """Initialize the parser"""
        if Savegame is None:
            logger.warning("h3sed library not available. Save parsing will be limited.")
        
        self.current_player = 0
        
    def parse_save_file(self, save_path: Path) -> Optional[GameState]:
        """
        Parse a Heroes III save file and extract game state.
        
        Args:
            save_path: Path to the save file (.gm1, .gm2, etc.)
            
        Returns:
            GameState object or None if parsing fails
        """
        try:
            # Read and decompress the save file
            with gzip.open(save_path, 'rb') as f:
                save_data = f.read()
            
            if Savegame is None:
                # Fallback: return mock data for testing
                logger.warning("Using mock data due to missing h3sed library")
                return self._create_mock_game_state()
            
            # Parse with h3sed
            save = Savegame(save_data)
            
            # Extract game state
            return self._extract_game_state(save)
            
        except Exception as e:
            logger.error(f"Failed to parse save file {save_path}: {e}")
            return None
    
    def _extract_game_state(self, save: Any) -> GameState:
        """
        Extract game state from parsed save file.
        
        Args:
            save: Parsed h3sed Savegame object
            
        Returns:
            GameState object
        """
        # Get current turn and player
        turn = getattr(save, 'day', 1)
        current_player = getattr(save, 'current_player', 0)
        
        # Extract visible tiles (only where fog of war is false)
        visible_tiles = self._extract_visible_tiles(save)
        
        # Extract heroes for current player
        heroes = self._extract_player_heroes(save, current_player)
        
        # Extract towns for current player
        towns = self._extract_player_towns(save, current_player)
        
        return GameState(
            turn=turn,
            current_player=current_player,
            visible_tiles=visible_tiles,
            heroes=heroes,
            towns=towns
        )
    
    def _extract_visible_tiles(self, save: Any) -> List[Tile]:
        """
        Extract tiles visible to the current player.
        
        Args:
            save: Parsed save game
            
        Returns:
            List of visible Tile objects
        """
        tiles = []
        
        # TODO: Implement actual fog of war check
        # This is a placeholder implementation
        map_data = getattr(save, 'map', None)
        if not map_data:
            return tiles
        
        # For now, return some sample tiles
        # In real implementation, iterate through map and check fog
        sample_tiles = [
            Tile(x=34, y=17, obj="GoldMine", owner=None),
            Tile(x=35, y=17, obj="CrystalCavern", owner=0),
            Tile(x=36, y=18, obj="Town", owner=0)
        ]
        
        return sample_tiles
    
    def _extract_player_heroes(self, save: Any, player_id: int) -> List[Hero]:
        """
        Extract heroes belonging to a specific player.
        
        Args:
            save: Parsed save game
            player_id: Player ID to filter by
            
        Returns:
            List of Hero objects
        """
        heroes = []
        
        # TODO: Implement actual hero extraction
        # This is a placeholder implementation
        hero_list = getattr(save, 'heroes', [])
        
        # For now, return a sample hero
        sample_hero = Hero(
            name="Ivor",
            location={"x": 34, "y": 17},
            army=[{"creatureId": 17, "count": 87}],
            movement_left=578,
            primary_stats={
                "attack": 9,
                "defense": 10,
                "spellPower": 4,
                "knowledge": 4
            }
        )
        heroes.append(sample_hero)
        
        return heroes
    
    def _extract_player_towns(self, save: Any, player_id: int) -> List[Town]:
        """
        Extract towns belonging to a specific player.
        
        Args:
            save: Parsed save game
            player_id: Player ID to filter by
            
        Returns:
            List of Town objects
        """
        towns = []
        
        # TODO: Implement actual town extraction
        # This is a placeholder implementation
        
        return towns
    
    def _create_mock_game_state(self) -> GameState:
        """
        Create a mock game state for testing without h3sed.
        
        Returns:
            Mock GameState object
        """
        return GameState(
            turn=28,
            current_player=0,
            visible_tiles=[
                Tile(x=34, y=17, obj="GoldMine", owner=None),
                Tile(x=35, y=17, obj="CrystalCavern", owner=0)
            ],
            heroes=[
                Hero(
                    name="Ivor",
                    location={"x": 34, "y": 17},
                    army=[{"creatureId": 17, "count": 87}],
                    movement_left=578,
                    primary_stats={
                        "attack": 9,
                        "defense": 10,
                        "spellPower": 4,
                        "knowledge": 4
                    }
                )
            ],
            towns=[]
        )