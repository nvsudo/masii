#!/bin/bash

# restore-agents.sh
# Restore agent registry from backup if agents are missing
# Usage: ./restore-agents.sh [--check] [--restore]

BACKUP_FILE="/Users/nikunjvora/clawd/.agent-registry-backup.json"
CONFIG_FILE="$HOME/.moltbot/moltbot.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check current agent count
current_count=$(jq '.agents.list | length' "$CONFIG_FILE" 2>/dev/null || echo "0")

echo "📋 Agent Registry Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Current agents in config: $current_count"
echo "Backup file: $BACKUP_FILE"
echo ""

# If count is less than expected, show warning
if [ "$current_count" -lt 8 ]; then
  echo -e "${RED}⚠️  MISSING AGENTS DETECTED${NC}"
  echo "Expected 8 agents, found $current_count"
  echo ""
  
  if [ "$1" == "--restore" ]; then
    echo "🔄 Restoring from backup..."
    
    # Extract agent list from backup
    agents=$(jq '.agents' "$BACKUP_FILE")
    
    # Apply patch to config
    moltbot gateway --action config.patch --raw "{\"agents\": $agents}"
    
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✅ Agents restored!${NC}"
    else
      echo -e "${RED}❌ Restore failed. Check moltbot logs.${NC}"
    fi
  else
    echo "Run with --restore to fix: $0 --restore"
  fi
else
  echo -e "${GREEN}✅ All agents present${NC}"
  jq '.agents.list[] | "\(.id) → \(.workspace)"' "$CONFIG_FILE" | column -t
fi
