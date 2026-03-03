# Agent Registry Guardrails

## What Happened

On **2026-02-11**, all agent entries except `devops-agent` disappeared from the main Moltbot config (`~/.moltbot/moltbot.json`). This wiped out:
- shreya ✅ (restored)
- kavi ✅ (restored)
- blitz ✅ (restored)
- michael ✅ (restored)
- scout ✅ (restored)
- productivity_journal ✅ (restored)
- greg ✅ (restored)

**Root cause:** Likely a config reset or manual edit that overwrote `agents.list` without preserving existing entries.

---

## Guardrails Now In Place

### 1. **Backup Registry** 
**File:** `.agent-registry-backup.json`  
**Location:** `/Users/nikunjvora/clawd/.agent-registry-backup.json`

Source of truth backup. Updated whenever agents are restored.  
**Action if lost:** Copy back from version control.

### 2. **Restore Script**
**File:** `restore-agents.sh`  
**Location:** `/Users/nikunjvora/clawd/restore-agents.sh`

Checks and restores agents from backup.

```bash
# Check status
./restore-agents.sh

# Restore from backup
./restore-agents.sh --restore
```

### 3. **Automated Integrity Check (Cron)**
Runs **every 6 hours** (0/6/12/18 UTC, Dubai time).  
**Job ID:** `d02b5297-f96f-4202-873c-69c4014ed95a`  
**Trigger:** Reminds you if agents are missing.

To disable:
```bash
moltbot cron remove d02b5297-f96f-4202-873c-69c4014ed95a
```

To view:
```bash
moltbot cron list
```

---

## If Agents Disappear Again

### Quick Fix
```bash
cd /Users/nikunjvora/clawd
./restore-agents.sh --restore
```

### Manual Fix
```bash
moltbot gateway --action config.get | jq .
# Compare agents.list to .agent-registry-backup.json
# If missing, restore:
moltbot gateway --action config.patch --raw '{"agents": {...}}'
```

---

## Prevention Strategy

1. **Use `config.patch` for agent updates**, never `config.apply` unless rebuilding entire config
2. **Back up config before major changes:**
   ```bash
   cp ~/.moltbot/moltbot.json ~/.moltbot/moltbot.json.backup.$(date +%s)
   ```
3. **Version control the backup:**
   ```bash
   cd /Users/nikunjvora/clawd
   git add .agent-registry-backup.json restore-agents.sh
   git commit -m "Guardrails: agent registry protection"
   ```

---

## Agent Directories (Safe as-is)

All agent workspaces are safely stored:
```
/Users/nikunjvora/clawd/agents/
├── devops/
├── shreya/
├── kavi/
├── blitz/
├── michael/
├── scout/
├── productivity_journal/
└── greg/
```

Only the config registry needs protection, not the agent files.

---

## Future Improvements

- [ ] Monitor config file hash for unauthorized changes
- [ ] Slack alert on agent removal
- [ ] Auto-sync agent registry from git on startup
- [ ] Add a "pin agents" setting to prevent accidental removal
