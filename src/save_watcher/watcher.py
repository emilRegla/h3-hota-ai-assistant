"""File system watcher for Heroes III save files"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from .parser import SaveParser
from .models import GameState


logger = logging.getLogger(__name__)


class SaveFileHandler(FileSystemEventHandler):
    """Handles file system events for save files"""
    
    def __init__(self, parser: SaveParser, callback: Optional[Callable[[GameState], None]] = None):
        self.parser = parser
        self.callback = callback
        self.last_modified: dict[str, datetime] = {}
        self.debounce_seconds = 1.0  # Avoid duplicate events
    
    def on_modified(self, event: FileModifiedEvent):
        """Called when a file is modified"""
        if event.is_directory:
            return
            
        path = Path(event.src_path)
        
        # Check if it's a save file
        if not self._is_save_file(path):
            return
        
        # Debounce check
        now = datetime.now()
        last_mod = self.last_modified.get(str(path))
        if last_mod and (now - last_mod).total_seconds() < self.debounce_seconds:
            logger.debug(f"Ignoring duplicate event for {path}")
            return
        
        self.last_modified[str(path)] = now
        
        logger.info(f"Save file modified: {path}")
        
        # Parse the save file
        game_state = self.parser.parse_save_file(path)
        
        if game_state:
            # Output to stdout as JSON
            print(json.dumps(game_state.to_dict(), indent=2))
            sys.stdout.flush()
            
            # Call callback if provided
            if self.callback:
                self.callback(game_state)
        else:
            logger.error(f"Failed to parse save file: {path}")
    
    def _is_save_file(self, path: Path) -> bool:
        """Check if the file is a Heroes III save file"""
        # Heroes III save files: .GM1, .GM2, etc.
        # HD Mod autosaves: autosave_*.gm1
        return path.suffix.lower() in ['.gm1', '.gm2', '.gm3', '.gm4', '.gm5', '.gm6']


class SaveWatcher:
    """Monitors a directory for Heroes III save file changes"""
    
    def __init__(self, save_directory: Path):
        """
        Initialize the save watcher.
        
        Args:
            save_directory: Path to the Heroes III saves directory
        """
        self.save_directory = Path(save_directory)
        if not self.save_directory.exists():
            raise ValueError(f"Save directory does not exist: {save_directory}")
        
        self.parser = SaveParser()
        self.observer = Observer()
        self.handler = SaveFileHandler(self.parser)
        
        logger.info(f"Initialized SaveWatcher for directory: {self.save_directory}")
    
    def start(self, callback: Optional[Callable[[GameState], None]] = None):
        """
        Start watching for save file changes.
        
        Args:
            callback: Optional callback function to call with parsed game state
        """
        self.handler.callback = callback
        
        # Schedule the observer
        self.observer.schedule(self.handler, str(self.save_directory), recursive=False)
        
        # Start the observer
        self.observer.start()
        logger.info("Started watching for save file changes")
        
        try:
            # Keep the watcher running
            self.observer.join()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            self.stop()
    
    def stop(self):
        """Stop watching for changes"""
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped watching for save file changes")
    
    def process_existing_saves(self):
        """Process any existing save files in the directory"""
        save_files = []
        
        # Find all save files
        for pattern in ['*.gm1', '*.GM1', 'autosave_*.gm1']:
            save_files.extend(self.save_directory.glob(pattern))
        
        if not save_files:
            logger.info("No existing save files found")
            return
        
        # Sort by modification time and process the most recent
        save_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        latest_save = save_files[0]
        
        logger.info(f"Processing most recent save: {latest_save}")
        game_state = self.parser.parse_save_file(latest_save)
        
        if game_state:
            print(json.dumps(game_state.to_dict(), indent=2))
            sys.stdout.flush()


def main():
    """Main entry point for the save watcher"""
    import argparse
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Watch Heroes III save files for changes')
    parser.add_argument(
        'save_directory',
        type=Path,
        help='Path to Heroes III saves directory'
    )
    parser.add_argument(
        '--process-existing',
        action='store_true',
        help='Process the most recent existing save file before watching'
    )
    
    args = parser.parse_args()
    
    # Create and start the watcher
    watcher = SaveWatcher(args.save_directory)
    
    if args.process_existing:
        watcher.process_existing_saves()
    
    # Start watching
    logger.info(f"Watching directory: {args.save_directory}")
    logger.info("Press Ctrl+C to stop")
    
    try:
        watcher.start()
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()