"""Request handlers for MCP endpoints"""

import json
from typing import Dict, Any, Optional

from .cache import GameStateCache


class ManifestHandler:
    """Handles MCP manifest requests"""
    
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the MCP manifest for Claude Desktop.
        
        Returns:
            Manifest dictionary
        """
        return {
            "schema_version": "v0.3",
            "name": "HeroesHotAState",
            "description": "Provides player-visible state from Heroes III HotA games",
            "icon": "https://raw.githubusercontent.com/emilRegla/h3-hota-ai-assistant/main/assets/hota_icon.png",
            "context_sources": [
                {
                    "id": "snapshot",
                    "name": "Latest GameState JSON",
                    "description": "Current visible map, heroes and towns for the human player",
                    "schema": "/schema/snapshot.json",
                    "query_endpoint": "/query/snapshot"
                }
            ]
        }


class SchemaHandler:
    """Handles schema requests"""
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the JSON schema for GameState.
        
        Returns:
            JSON Schema dictionary
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "GameState",
            "description": "Heroes III game state visible to the current player",
            "type": "object",
            "required": ["turn", "currentPlayer", "visibleTiles", "heroes", "towns"],
            "properties": {
                "turn": {
                    "type": "integer",
                    "description": "Current game turn (day)",
                    "minimum": 1
                },
                "currentPlayer": {
                    "type": "integer",
                    "description": "Current player ID (0-7)",
                    "minimum": 0,
                    "maximum": 7
                },
                "visibleTiles": {
                    "type": "array",
                    "description": "Map tiles visible to the player",
                    "items": {
                        "type": "object",
                        "required": ["x", "y", "obj"],
                        "properties": {
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "obj": {"type": "string"},
                            "owner": {
                                "type": ["integer", "null"],
                                "minimum": 0,
                                "maximum": 7
                            }
                        }
                    }
                },
                "heroes": {
                    "type": "array",
                    "description": "Player's heroes",
                    "items": {
                        "type": "object",
                        "required": ["name", "location", "army", "movementLeft", "primaryStats"],
                        "properties": {
                            "name": {"type": "string"},
                            "location": {
                                "type": "object",
                                "required": ["x", "y"],
                                "properties": {
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"}
                                }
                            },
                            "army": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["creatureId", "count"],
                                    "properties": {
                                        "creatureId": {"type": "integer"},
                                        "count": {"type": "integer", "minimum": 1}
                                    }
                                }
                            },
                            "movementLeft": {"type": "integer", "minimum": 0},
                            "primaryStats": {
                                "type": "object",
                                "required": ["attack", "defense", "spellPower", "knowledge"],
                                "properties": {
                                    "attack": {"type": "integer", "minimum": 0},
                                    "defense": {"type": "integer", "minimum": 0},
                                    "spellPower": {"type": "integer", "minimum": 0},
                                    "knowledge": {"type": "integer", "minimum": 0}
                                }
                            }
                        }
                    }
                },
                "towns": {
                    "type": "array",
                    "description": "Player's towns",
                    "items": {
                        "type": "object",
                        "required": ["name", "location", "owner", "type", "buildings", "garrison"],
                        "properties": {
                            "name": {"type": "string"},
                            "location": {
                                "type": "object",
                                "required": ["x", "y"],
                                "properties": {
                                    "x": {"type": "integer"},
                                    "y": {"type": "integer"}
                                }
                            },
                            "owner": {"type": "integer"},
                            "type": {"type": "string"},
                            "buildings": {
                                "type": "array",
                                "items": {"type": "integer"}
                            },
                            "garrison": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["creatureId", "count"],
                                    "properties": {
                                        "creatureId": {"type": "integer"},
                                        "count": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                },
                "resources": {
                    "type": "object",
                    "description": "Player's resources",
                    "properties": {
                        "gold": {"type": "integer", "minimum": 0},
                        "wood": {"type": "integer", "minimum": 0},
                        "ore": {"type": "integer", "minimum": 0},
                        "mercury": {"type": "integer", "minimum": 0},
                        "sulfur": {"type": "integer", "minimum": 0},
                        "crystal": {"type": "integer", "minimum": 0},
                        "gems": {"type": "integer", "minimum": 0}
                    }
                }
            }
        }


class QueryHandler:
    """Handles query requests"""
    
    def __init__(self, cache: GameStateCache):
        """
        Initialize the query handler.
        
        Args:
            cache: GameStateCache instance
        """
        self.cache = cache
    
    def handle_query(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a query request from Claude.
        
        Args:
            request_data: Request body from Claude
            
        Returns:
            Response dictionary
        """
        # Get the latest game state from cache
        game_state = self.cache.get_latest()
        
        if game_state is None:
            # No game state available yet
            return {
                "error": "No game state available",
                "message": "Waiting for Heroes III save file to be detected"
            }
        
        # Check if requesting specific turn
        requested_turn = request_data.get("turn")
        if requested_turn is not None:
            # For now, we only support latest state
            if requested_turn != game_state.get("turn"):
                return {
                    "error": "Turn not available",
                    "message": f"Requested turn {requested_turn}, but only turn {game_state.get('turn')} is available"
                }
        
        # Return the game state
        return {
            "success": True,
            "data": game_state,
            "metadata": {
                "cached_at": self.cache.last_update.isoformat() if self.cache.last_update else None,
                "version": "1.0.0"
            }
        }