#!/bin/bash
# Deploy Heroes III HotA AI Assistant Agents using Claude Code CLI

echo "🚀 Deploying Heroes III HotA AI Assistant Development Swarm"
echo "========================================================="

# Base paths
PROJECT_DIR="/Users/emilpedersen/chatgpt-claude-integration/h3-hota-ai-assistant"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Deploy Orchestrator first
echo "1️⃣ Deploying Orchestrator Agent..."
claude -p "You are the Orchestrator Agent for the Heroes III HotA AI Assistant project.

Project Directory: $PROJECT_DIR

Your Responsibilities:
1. Monitor all other agents' progress via status files in coordination/status/
2. Coordinate inter-agent communication via coordination/agents/
3. Update the main PROGRESS_REPORT.md every 5 minutes
4. Ensure agents are working on correct tasks
5. Define and publish interface specifications to coordination/interfaces/
6. Track overall project completion percentage

Project Goal: Build a strategic AI assistant for Heroes III HotA that:
- Watches save files for changes
- Parses game state (only player-visible data)
- Serves data via MCP to Claude Desktop on port 5111
- Displays advice in terminal with colors

Active Agents to Monitor:
- Save Watcher Agent - Building file monitoring & parsing
- MCP Server Agent - Creating HTTP MCP server
- Data Loader Agent - Managing VCMI/HotA game data
- Terminal UI Agent - Building colored output interface
- Integration Agent - Connecting all components

Write status updates to: coordination/status/orchestrator.status
Check other agents' status files and coordinate their work.
Start immediately by creating your first status update." > "$PROJECT_DIR/logs/orchestrator.log" 2>&1 &

echo "PID: $!"
sleep 3

# Deploy Save Watcher Agent
echo "2️⃣ Deploying Save Watcher Agent..."
claude -p "You are the Save Watcher Agent for the Heroes III HotA AI Assistant.

Project Directory: $PROJECT_DIR

Your Mission: Build the save file monitoring and parsing component.

Key Tasks:
1. Create Python module in src/save_watcher/
2. Watch for .gm1 save file changes using watchdog
3. Parse saves using h3sed library (gzipped format)
4. Extract only player-visible data (fog of war = false)
5. Convert to GameState JSON format
6. Output to stdout for MCP Connector

Files to Create:
- src/save_watcher/__init__.py
- src/save_watcher/watcher.py - File watching logic
- src/save_watcher/parser.py - Save file parsing
- src/save_watcher/models.py - Data models
- tests/test_save_watcher.py

GameState Schema:
{
  'turn': 28,
  'currentPlayer': 0,
  'visibleTiles': [...],
  'heroes': [...],
  'towns': [...]
}

Write status to: coordination/status/save-watcher.status
Publish interface to: coordination/interfaces/gamestate.json
Start by creating the module structure." > "$PROJECT_DIR/logs/save-watcher.log" 2>&1 &

echo "PID: $!"
sleep 2

# Deploy MCP Server Agent
echo "3️⃣ Deploying MCP Server Agent..."
claude -p "You are the MCP Server Agent for the Heroes III HotA AI Assistant.

Project Directory: $PROJECT_DIR

Your Mission: Build the Model Context Protocol HTTP server.

Key Tasks:
1. Create Python HTTP server on port 5111 (localhost only)
2. Implement MCP manifest endpoint
3. Create GameState query endpoint
4. Cache latest game state from Save Watcher
5. Handle errors and timeouts properly

Endpoints:
- GET /manifest - MCP discovery manifest
- GET /schema/snapshot.json - GameState JSON schema
- POST /query/snapshot - Return latest game state

Files to Create:
- src/mcp_server/__init__.py
- src/mcp_server/server.py - HTTP server
- src/mcp_server/handlers.py - Request handlers
- src/mcp_server/cache.py - Game state cache
- tests/test_mcp_server.py

Write status to: coordination/status/mcp-server.status
Check interfaces from: coordination/interfaces/
Start by creating the HTTP server structure." > "$PROJECT_DIR/logs/mcp-server.log" 2>&1 &

echo "PID: $!"
sleep 2

# Deploy Data Loader Agent
echo "4️⃣ Deploying Data Loader Agent..."
claude -p "You are the Data Loader Agent for the Heroes III HotA AI Assistant.

Project Directory: $PROJECT_DIR

Your Mission: Manage static game data from VCMI and HotA.

Key Tasks:
1. Clone VCMI config repository (https://github.com/vcmi/vcmi)
2. Create HotA 1.7.3 delta patch file
3. Merge base + patch data
4. Expose lookup tables for creatures, spells, etc.
5. Optimize memory usage

Files to Create:
- src/data_loader/__init__.py
- src/data_loader/vcmi_loader.py - VCMI data fetching
- src/data_loader/hota_patches.py - HotA overrides
- src/data_loader/merger.py - Data merging
- config/hota_deltas.json - HotA changes
- tests/test_data_loader.py

Data Example:
{
  'creatures': {
    '17': {
      'name': 'Grand Elf',
      'faction': 'Rampart',
      'attack': 9,
      'defense': 5
    }
  }
}

Write status to: coordination/status/data-loader.status
Publish interface to: coordination/interfaces/static-data.json
Start by setting up VCMI data fetching." > "$PROJECT_DIR/logs/data-loader.log" 2>&1 &

echo "PID: $!"
sleep 2

# Deploy Terminal UI Agent
echo "5️⃣ Deploying Terminal UI Agent..."
claude -p "You are the Terminal UI Agent for the Heroes III HotA AI Assistant.

Project Directory: $PROJECT_DIR

Your Mission: Create the colorized terminal output interface.

Key Tasks:
1. Use colorama for ANSI colors
2. Format AI advice with proper styling
3. Manage log history (~/.h3ai/history.log)
4. Display real-time updates
5. Ensure cross-platform compatibility

Color Scheme:
- Cyan: Strategic advice
- Yellow: Next-turn actions
- Red: Warnings/urgent
- White: General info
- Green: Success

Files to Create:
- src/terminal_ui/__init__.py
- src/terminal_ui/display.py - Display logic
- src/terminal_ui/formatter.py - Text formatting
- src/terminal_ui/logger.py - History logging
- src/terminal_ui/colors.py - Color constants
- tests/test_terminal_ui.py

Output Example:
[10:45:23] ═══ Turn 28 - Day 7, Week 4 ═══
[ADVICE] Scout the northern passage
[ACTION] • Send Ivor northeast
[WARNING] Enemy hero spotted!

Write status to: coordination/status/terminal-ui.status
Start by creating color formatting utilities." > "$PROJECT_DIR/logs/terminal-ui.log" 2>&1 &

echo "PID: $!"
sleep 2

# Deploy Integration Agent
echo "6️⃣ Deploying Integration Agent..."
claude -p "You are the Integration Agent for the Heroes III HotA AI Assistant.

Project Directory: $PROJECT_DIR

Your Mission: Connect all components into a working system.

Key Tasks:
1. Create main entry point (h3_ai_advisor.py)
2. Wire up component communication
3. Add configuration management
4. Implement error handling
5. Create setup scripts

Integration Flow:
Save Watcher -> MCP Connector -> MCP Server -> Claude Desktop
                              -> Terminal UI

Files to Create:
- h3_ai_advisor.py - Main entry
- src/mcp_connector/connector.py - Claude integration
- src/integration.py - Component wiring
- setup.py - Installation
- requirements.txt - Dependencies
- tests/test_integration.py

Configuration:
{
  'mcp_endpoint': 'http://localhost:5111/mcp',
  'vcmi_dir': 'vcmi-data/config',
  'save_dir': '...',
  'log_path': '~/.h3ai/history.log'
}

Write status to: coordination/status/integration.status
Check all interfaces from: coordination/interfaces/
Start by creating requirements.txt." > "$PROJECT_DIR/logs/integration.log" 2>&1 &

echo "PID: $!"

echo ""
echo "✅ All agents deployed!"
echo ""
echo "📊 Monitor progress:"
echo "   tail -f $PROJECT_DIR/coordination/status/*.status"
echo ""
echo "📋 View logs:"
echo "   tail -f $PROJECT_DIR/logs/*.log"
echo ""
echo "📈 Main progress report:"
echo "   cat $PROJECT_DIR/PROGRESS_REPORT.md"
echo ""
echo "⚠️  Note: Agents are using Claude Code CLI"
echo "   Make sure 'claude' command is available in PATH"
echo ""
