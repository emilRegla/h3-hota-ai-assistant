#!/usr/bin/env python3
"""
Heroes III + HotA AI Assistant - Main Entry Point

This script integrates all components:
- Watches save files for changes
- Parses game state
- Serves data via MCP to Claude Desktop
- Displays advice in terminal
"""

import argparse
import json
import logging
import sys
import threading
from pathlib import Path
from typing import Optional

# Import our components
from src.save_watcher import SaveWatcher
from src.mcp_server import MCPServer
from src.terminal_ui.display import TerminalDisplay
from src.mcp_connector.connector import MCPConnector


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class H3AIAdvisor:
    """Main application class that coordinates all components"""
    
    def __init__(self, save_dir: Path, config: dict):
        """
        Initialize the AI advisor.
        
        Args:
            save_dir: Path to Heroes III saves directory
            config: Configuration dictionary
        """
        self.save_dir = save_dir
        self.config = config
        
        # Initialize components
        self.save_watcher = SaveWatcher(save_dir)
        self.mcp_server = MCPServer(
            port=config.get('mcp_port', 5111),
            cache_file=Path(config.get('cache_file', '.h3ai_cache.json'))
        )
        self.terminal = TerminalDisplay()
        self.mcp_connector = MCPConnector(
            endpoint=config.get('mcp_endpoint', 'http://localhost:5005/mcp')
        )
        
        logger.info("H3 AI Advisor initialized")
    
    def start(self):
        """Start all components"""
        try:
            # Start MCP server in background
            logger.info("Starting MCP server...")
            self.mcp_server.start(blocking=False)
            
            # Set up game state callback
            def on_game_state_update(game_state):
                """Called when save file changes"""
                logger.info(f"Game state updated: Turn {game_state.turn}")
                
                # Update MCP server cache
                self.mcp_server.update_game_state(game_state.to_dict())
                
                # Get AI advice from Claude
                advice = self.mcp_connector.get_advice(game_state)
                
                # Display in terminal
                if advice:
                    self.terminal.display_advice(game_state, advice)
                else:
                    self.terminal.display_status(
                        "Waiting for Claude connection...",
                        "warning"
                    )
            
            # Process any existing saves first
            logger.info("Checking for existing save files...")
            self.save_watcher.process_existing_saves()
            
            # Start watching for changes
            logger.info(f"Watching save directory: {self.save_dir}")
            self.terminal.display_status(
                f"Heroes III AI Assistant Started\nWatching: {self.save_dir}",
                "success"
            )
            
            # This blocks until interrupted
            self.save_watcher.start(callback=on_game_state_update)
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
        finally:
            self.stop()
    
    def stop(self):
        """Stop all components"""
        logger.info("Stopping components...")
        
        try:
            self.save_watcher.stop()
        except:
            pass
            
        try:
            self.mcp_server.stop()
        except:
            pass
        
        self.terminal.display_status("AI Assistant stopped", "info")


def load_config(config_path: Optional[Path] = None) -> dict:
    """Load configuration from file or use defaults"""
    default_config = {
        'mcp_endpoint': 'http://localhost:5005/mcp',
        'mcp_port': 5111,
        'vcmi_dir': 'vcmi-data/config',
        'log_path': '~/.h3ai/history.log',
        'cache_file': '.h3ai_cache.json',
        'max_log_mb': 1
    }
    
    if config_path and config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            default_config.update(user_config)
            logger.info(f"Loaded config from {config_path}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
    
    return default_config


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Heroes III + HotA AI Assistant - Strategic advisor for your games'
    )
    
    parser.add_argument(
        'save_directory',
        type=Path,
        help='Path to Heroes III saves directory (e.g., ".../HotA/Saves")'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration file (JSON)'
    )
    
    parser.add_argument(
        '--mcp-port',
        type=int,
        default=5111,
        help='Port for MCP server (default: 5111)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate save directory
    if not args.save_directory.exists():
        print(f"Error: Save directory does not exist: {args.save_directory}")
        sys.exit(1)
    
    # Load configuration
    config = load_config(args.config)
    if args.mcp_port != 5111:
        config['mcp_port'] = args.mcp_port
    
    # Print startup banner
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║      Heroes III + HotA Strategic AI Assistant         ║
    ║                                                       ║
    ║  Your AI companion for Heroes of Might and Magic III  ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    print(f"Save Directory: {args.save_directory}")
    print(f"MCP Server: http://localhost:{config['mcp_port']}")
    print(f"Claude Desktop: Add http://localhost:{config['mcp_port']}/manifest")
    print("\nPress Ctrl+C to stop\n")
    
    # Create and start the advisor
    advisor = H3AIAdvisor(args.save_directory, config)
    
    try:
        advisor.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()