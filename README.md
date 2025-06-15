# Heroes III + HotA Strategic AI Assistant 🏰⚔️

A local, offline-capable strategic advisor for Heroes of Might and Magic III – Horn of the Abyss (HotA) running under Kegwerks/Wineskin on macOS.

## Overview

This AI assistant watches your Heroes III save files and provides real-time strategic advice through Claude. It analyzes your game state (only player-visible information) and offers turn-by-turn guidance and tactical combat tips.

## Features

- 🔍 **Automatic Save Detection**: Monitors save files and detects changes within 2 seconds
- 🤖 **Claude Integration**: Uses Anthropic's Model Context Protocol (MCP) for AI advice
- 🎨 **Beautiful Terminal UI**: Color-coded advice with clear visual hierarchy
- 📊 **Game Data Support**: Full VCMI data with HotA 1.7.3+ patches
- 🔒 **Privacy First**: Runs entirely locally, only sends visible game data to Claude
- ⚡ **Fast Response**: Strategic advice within 3 seconds of save

## Architecture

```
Heroes III (Wine) → Save File → Watcher → Parser → MCP Server → Claude
                                                        ↓
                                            Terminal ← Advice
```

## Quick Start

### Prerequisites

- macOS 15.5+ with Apple Silicon (tested on MacBook Air M2)
- Python 3.12+
- Heroes III HotA 1.7.2+ with HD Mod
- Claude Desktop with MCP enabled

### Installation

```bash
# Clone the repository
git clone https://github.com/emilRegla/h3-hota-ai-assistant.git
cd h3-hota-ai-assistant

# Install dependencies
pip install -r requirements.txt

# Download VCMI game data
git clone https://github.com/vcmi/vcmi vcmi-data
```

### Configuration

1. Enable autosave in HD Mod:
   - Edit `HD.ini` and set `AutosaveEveryDay=1`
   - Or press F5 manually each turn

2. Add to Claude Desktop:
   - Open Claude Desktop settings
   - Add MCP source: `http://localhost:5111/manifest`

### Usage

```bash
# Run the AI assistant
python h3_ai_advisor.py "/path/to/HotA/Saves"

# Example for typical installation:
python h3_ai_advisor.py "/Users/[username]/Applications/Kegworks/Heroes 3 Hota.app/Contents/SharedSupport/prefix/drive_c/GOG Games/HoMM 3 Complete/Games/HotA/Saves"
```

## Project Status

🚧 **Work in Progress** (40% Complete)

### Completed Components
- ✅ Save file monitoring and parsing (90%)
- ✅ MCP server implementation (80%)
- ✅ Main integration script (50%)
- ✅ Project structure and deployment scripts

### In Development
- 🔄 Terminal UI display logic (10%)
- 🔄 Data loader for VCMI/HotA (0%)
- 🔄 Test suite (0%)
- 🔄 Documentation (20%)

## Development

This project uses the Claude Code Swarm framework for parallel development with specialized AI agents.

### Running the Development Swarm

```bash
# Deploy all development agents
./deploy-agents.sh

# Monitor agent progress
./monitor-h3-agents.sh
```

### Project Structure

```
h3-hota-ai-assistant/
├── src/
│   ├── save_watcher/    # Save file monitoring
│   ├── mcp_server/      # MCP HTTP server
│   ├── terminal_ui/     # Terminal display
│   ├── data_loader/     # VCMI/HotA data
│   └── mcp_connector/   # Claude integration
├── tests/               # Test suites
├── docs/                # Documentation
└── coordination/        # Agent communication
```

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_ENDPOINT` | `http://localhost:5111/mcp` | MCP server endpoint |
| `MCP_PORT` | `5111` | Port for MCP server |
| `VCMI_DIR` | `vcmi-data/config` | VCMI data directory |
| `LOG_PATH` | `~/.h3ai/history.log` | Advice history log |
| `MAX_LOG_MB` | `1` | Log rotation size |

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- VCMI team for game data structures
- HotA team for the amazing expansion
- Anthropic for Claude and MCP
- h3sed library for save file parsing

---

**Note**: This tool is not affiliated with Ubisoft, 3DO, or the HotA team. Heroes of Might and Magic III is a trademark of Ubisoft Entertainment.