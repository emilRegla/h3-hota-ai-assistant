"""MCP HTTP server implementation"""

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional, Dict, Any

from .handlers import ManifestHandler, SchemaHandler, QueryHandler
from .cache import GameStateCache


logger = logging.getLogger(__name__)


class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for MCP endpoints"""
    
    def __init__(self, *args, cache: GameStateCache = None, **kwargs):
        self.cache = cache
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/manifest':
            self.handle_manifest()
        elif self.path == '/schema/snapshot.json':
            self.handle_schema()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/query/snapshot':
            self.handle_query()
        else:
            self.send_error(404, "Not Found")
    
    def handle_manifest(self):
        """Handle manifest request"""
        handler = ManifestHandler()
        manifest = handler.get_manifest()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(manifest, indent=2).encode())
    
    def handle_schema(self):
        """Handle schema request"""
        handler = SchemaHandler()
        schema = handler.get_schema()
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(schema, indent=2).encode())
    
    def handle_query(self):
        """Handle query request"""
        # Get request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        
        try:
            request_data = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON")
            return
        
        # Get cached game state
        handler = QueryHandler(self.server.cache)
        response = handler.handle_query(request_data)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        """Override to use logger instead of stderr"""
        logger.info(f"{self.address_string()} - {format % args}")


class MCPServer:
    """MCP HTTP Server for Claude integration"""
    
    def __init__(self, port: int = 5111, cache_file: Optional[Path] = None):
        """
        Initialize the MCP server.
        
        Args:
            port: Port to listen on (default: 5111)
            cache_file: Optional path to cache file for persistence
        """
        self.port = port
        self.cache = GameStateCache(cache_file)
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        
        logger.info(f"Initialized MCP server on port {port}")
    
    def start(self, blocking: bool = True):
        """
        Start the HTTP server.
        
        Args:
            blocking: If True, blocks until server stops. If False, runs in background.
        """
        # Create request handler with cache
        def handler(*args, **kwargs):
            MCPRequestHandler(*args, cache=self.cache, **kwargs)
        
        # Create HTTP server
        self.server = HTTPServer(('127.0.0.1', self.port), MCPRequestHandler)
        self.server.cache = self.cache  # Make cache accessible to handler
        
        logger.info(f"Starting MCP server on http://127.0.0.1:{self.port}")
        
        if blocking:
            self.server.serve_forever()
        else:
            # Run in background thread
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            logger.info("MCP server running in background")
    
    def stop(self):
        """Stop the HTTP server"""
        if self.server:
            logger.info("Stopping MCP server...")
            self.server.shutdown()
            self.server.server_close()
            
            if self.thread:
                self.thread.join(timeout=5)
            
            logger.info("MCP server stopped")
    
    def update_game_state(self, game_state: Dict[str, Any]):
        """
        Update the cached game state.
        
        Args:
            game_state: New game state dictionary
        """
        self.cache.update(game_state)
        logger.debug(f"Updated game state for turn {game_state.get('turn', '?')}")


def main():
    """Run standalone MCP server"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Heroes III MCP Server')
    parser.add_argument(
        '--port',
        type=int,
        default=5111,
        help='Port to listen on (default: 5111)'
    )
    parser.add_argument(
        '--cache-file',
        type=Path,
        help='Path to cache file for persistence'
    )
    
    args = parser.parse_args()
    
    server = MCPServer(port=args.port, cache_file=args.cache_file)
    
    print(f"MCP Server starting on http://localhost:{args.port}")
    print(f"Manifest: http://localhost:{args.port}/manifest")
    print("Press Ctrl+C to stop")
    
    try:
        server.start(blocking=True)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()


if __name__ == '__main__':
    main()