"""Data models for Heroes III game state"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any


@dataclass
class Tile:
    """Represents a visible map tile"""
    x: int
    y: int
    obj: str  # Object type (e.g., "GoldMine", "Town", "Hero")
    owner: Optional[int] = None  # Player ID or None if neutral
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Hero:
    """Represents a hero on the map"""
    name: str
    location: Dict[str, int]  # {"x": 34, "y": 17}
    army: List[Dict[str, int]]  # [{"creatureId": 17, "count": 87}, ...]
    movement_left: int
    primary_stats: Dict[str, int]  # attack, defense, spellPower, knowledge
    mana: Optional[int] = None
    experience: Optional[int] = None
    level: Optional[int] = None
    skills: Optional[List[Dict[str, Any]]] = None
    spells: Optional[List[int]] = None
    artifacts: Optional[List[int]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Remove None values for cleaner JSON
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class Town:
    """Represents a town"""
    name: str
    location: Dict[str, int]  # {"x": 45, "y": 23}
    owner: int
    type: str  # Castle, Rampart, Tower, etc.
    buildings: List[int]  # Building IDs
    garrison: List[Dict[str, int]]  # Army in garrison
    available_creatures: Optional[List[Dict[str, int]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class GameState:
    """Complete game state visible to the current player"""
    turn: int
    current_player: int
    visible_tiles: List[Tile]
    heroes: List[Hero]
    towns: List[Town]
    resources: Optional[Dict[str, int]] = None  # gold, wood, ore, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert game state to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the game state
        """
        data = {
            "turn": self.turn,
            "currentPlayer": self.current_player,
            "visibleTiles": [tile.to_dict() for tile in self.visible_tiles],
            "heroes": [hero.to_dict() for hero in self.heroes],
            "towns": [town.to_dict() for town in self.towns]
        }
        
        if self.resources:
            data["resources"] = self.resources
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """
        Create GameState from dictionary.
        
        Args:
            data: Dictionary representation of game state
            
        Returns:
            GameState object
        """
        return cls(
            turn=data.get("turn", 1),
            current_player=data.get("currentPlayer", 0),
            visible_tiles=[
                Tile(**tile) for tile in data.get("visibleTiles", [])
            ],
            heroes=[
                Hero(**hero) for hero in data.get("heroes", [])
            ],
            towns=[
                Town(**town) for town in data.get("towns", [])
            ],
            resources=data.get("resources")
        )