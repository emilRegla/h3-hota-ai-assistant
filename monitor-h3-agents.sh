#!/bin/bash
# monitor-h3-agents.sh - Monitor Heroes III HotA AI Assistant agent progress

PROJECT_DIR="/Users/emilpedersen/chatgpt-claude-integration/h3-hota-ai-assistant"
cd $PROJECT_DIR

clear
echo "🔍 Heroes III HotA AI Assistant - Agent Monitor"
echo "=============================================="
echo ""

# Function to check if process is running
check_pid() {
    if ps -p $1 > /dev/null 2>&1; then
        echo "✅ Running"
    else
        echo "❌ Stopped"
    fi
}

# Load PIDs if available
if [ -f agent_pids.txt ]; then
    source agent_pids.txt
    
    echo "Agent Status:"
    echo "-------------"
    printf "%-15s %-10s %s\n" "AGENT" "PID" "STATUS"
    printf "%-15s %-10s %s\n" "Orchestrator" "$ORCHESTRATOR" "$(check_pid $ORCHESTRATOR)"
    printf "%-15s %-10s %s\n" "Save Watcher" "$SAVE_WATCHER" "$(check_pid $SAVE_WATCHER)"
    printf "%-15s %-10s %s\n" "Data Loader" "$DATA_LOADER" "$(check_pid $DATA_LOADER)"
    printf "%-15s %-10s %s\n" "MCP Server" "$MCP_SERVER" "$(check_pid $MCP_SERVER)"
    printf "%-15s %-10s %s\n" "Terminal UI" "$TERMINAL_UI" "$(check_pid $TERMINAL_UI)"
    printf "%-15s %-10s %s\n" "Integration" "$INTEGRATION" "$(check_pid $INTEGRATION)"
    printf "%-15s %-10s %s\n" "Testing" "$TESTING" "$(check_pid $TESTING)"
    printf "%-15s %-10s %s\n" "Documentation" "$DOCUMENTATION" "$(check_pid $DOCUMENTATION)"
else
    echo "No agent PIDs found. Run deploy-h3-hota-swarm.sh first."
fi

echo ""
echo "Latest Status Updates:"
echo "---------------------"

# Show last status from each agent
for agent in orchestrator save-watcher data-loader mcp-server terminal-ui integration testing documentation; do
    if [ -f coordination/status/${agent}.status ]; then
        status=$(tail -1 coordination/status/${agent}.status)
        printf "%-15s: %s\n" "${agent}" "${status:0:60}..."
    fi
done

echo ""
echo "Recent Activity:"
echo "---------------"
# Show last 5 lines from all status files combined, sorted by timestamp
if ls coordination/status/*.status 1> /dev/null 2>&1; then
    tail -n 1 coordination/status/*.status | grep -E "^\[" | sort -r | head -5
fi

echo ""
echo "Project Structure:"
echo "-----------------"
# Count files created
src_files=$(find src -name "*.py" 2>/dev/null | wc -l)
test_files=$(find tests -name "*.py" 2>/dev/null | wc -l)
doc_files=$(find docs -name "*.md" 2>/dev/null | wc -l)

echo "Source files: $src_files"
echo "Test files: $test_files"  
echo "Doc files: $doc_files"

echo ""
echo "Commands:"
echo "---------"
echo "View logs: tail -f logs/<agent>.log"
echo "Check specific status: cat coordination/status/<agent>.status"
echo "View progress report: cat PROGRESS_REPORT.md"
echo "Stop all agents: pkill -f 'claude -p'"
echo ""
echo "Auto-refreshing every 5 seconds... (Ctrl+C to exit)"