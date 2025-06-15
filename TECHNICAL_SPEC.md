# Heroes III + HotA Strategic AI Assistant – Technical Specification

## 1. Purpose & Scope

Design and implement a local, offline‑capable strategic advisor for Heroes of Might and Magic III – Horn of the Abyss (HotA) running under Kegwerks/Wineskin on macOS 15.5.
The assistant ingests static game data and player‑visible runtime state, sends concise JSON snapshots to Anthropic Claude via the Model Context Protocol (MCP), and prints turn‑by‑turn or combat‑specific advice in a neighbouring terminal window.

**In‑scope**
- Single‑player games, HotA 1.7.2+
- Day‑by‑day strategic guidance and tactical combat tips
- Runs entirely on user's MacBook Air M2 (12 GB RAM)

**Out‑of‑scope (v1)**
- Networked multiplayer support
- Real‑time DLL injection or frame‑by‑frame micro‑management

## 2. High‑Level Architecture

```
Game (Wine) → Autosave → Save Watcher → GameState JSON → MCP Server
                              ↓                              ↓
                        Static Data                    Claude Desktop
                              ↓                              ↓
                        Terminal UI ← Advice ← MCP Connector
```

## 3. Key Components

### 3.1 Save Watcher
- **Language**: Python 3.12
- **Libraries**: h3sed, watchdog, gzip
- **Input**: autosave_A_0000.gm1 files
- **Output**: GameState JSON (filtered for visible tiles)
- **Latency Target**: ≤ 2s from save to advice request

### 3.2 Static Data Loader  
- **Source**: VCMI config repo + HotA 1.7.3 patches
- **Format**: JSON lookup tables
- **Content**: Creatures, spells, artifacts, heroes

### 3.3 MCP Server
- **Port**: 5111 (localhost only)
- **Endpoints**:
  - GET /manifest
  - GET /schema/snapshot.json
  - POST /query/snapshot
- **Security**: Bind to 127.0.0.1 only

### 3.4 Terminal UI
- **Library**: colorama
- **Colors**: Cyan (advice), Yellow (actions), Red (warnings)
- **Logging**: ~/.h3ai/history.log (1MB rotation)

## 4. Data Schemas

### 4.1 Creature (static)
```json
{
  "id": 17,
  "name": "Grand Elf",
  "faction": "Rampart",
  "tier": 3,
  "attack": 9,
  "defense": 5,
  "minDamage": 3,
  "maxDamage": 5,
  "health": 15,
  "speed": 7,
  "growth": 10,
  "special": ["ranged", "two‑shots"]
}
```

### 4.2 GameState (runtime)
```json
{
  "turn": 28,
  "currentPlayer": 0,
  "visibleTiles": [{"x":34,"y":17,"obj":"GoldMine","owner":null}],
  "heroes": [{
    "name": "Ivor",
    "location": {"x":34,"y":17},
    "army": [{"creatureId":17,"count":87}],
    "movementLeft": 578,
    "primaryStats": {"attack":9,"defense":10,"spellPower":4,"knowledge":4}
  }],
  "towns": []
}
```

## 5. Installation

```bash
brew install git python@3.12 gzip
pip3 install --user h3sed watchdog requests colorama
git clone https://github.com/vcmi/vcmi vcmi-data
python3 h3_ai_advisor.py "/path/to/HotA/Saves"
```

## 6. Configuration

| Key | Default | Description |
|-----|---------|-------------|
| MCP_ENDPOINT | http://localhost:5111/mcp | Claude MCP local proxy |
| VCMI_DIR | vcmi-data/config | Static data root |
| SAVE_DIR | CLI arg | Folder to watch |
| LOG_PATH | ~/.h3ai/history.log | Advice history file |
| MAX_LOG_MB | 1 | Rotate after this size |

## 7. Performance Targets

- End‑of‑turn advice latency: ≤ 3s (95th percentile)
- Memory footprint (Python): ≤ 300 MB RSS
- Disk used by caches: ≤ 500 MB

## 8. MCP Integration Details

### 8.1 Manifest Format
```json
{
  "schema_version": "v0.3",
  "name": "HeroesHotAState",
  "description": "Provides player-visible state from Heroes III HotA games",
  "icon": "https://raw.githubusercontent.com/you/h3_ai/assets/hota_icon.png",
  "context_sources": [{
    "id": "snapshot",
    "name": "Latest GameState JSON",
    "description": "Current visible map, heroes and towns for the human player",
    "schema": "/schema/snapshot.json",
    "query_endpoint": "/query/snapshot"
  }]
}
```

### 8.2 Claude Integration
- System prompt emphasizes HotA expertise
- User message contains GameState JSON
- Response timeout: 30s with 2 retries
- Advice format: Concise, actionable bullet points

## 9. Error Handling

| Condition | Behavior |
|-----------|-----------|
| Claude timeout | Print "⚠ Claude timed out", retry once |
| JSON schema mismatch | Log to stderr, skip cycle |
| Save parser failure | Use previous valid state |

## 10. Testing Strategy

1. Unit tests for JSON schema conformance (pytest)
2. Golden save‑files with expected advice
3. Performance regression via 50‑turn replay

---
*Version 1.1 - MCP-ready specification*