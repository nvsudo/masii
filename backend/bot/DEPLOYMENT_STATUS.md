# JODI Bot Fly.io Staging Deployment Status

**Date**: February 22, 2026
**Status**: ⚠️ Deployment steps ready — Fly CLI not available in this environment. Needs manual run on dev machine.

## ✅ Completed Steps

### 1. Infrastructure Setup
- ✅ Fly.io app created: `jodi-bot-staging`
- ✅ Region: Mumbai (bom) - close to Supabase AP South 1
- ✅ App URL: **https://jodi-bot-staging.fly.dev**
- ✅ Environment secrets configured:
  - DATABASE_URL
  - TELEGRAM_BOT_TOKEN
  - SUPABASE_URL
  - SUPABASE_ANON_KEY
  - SUPABASE_SERVICE_ROLE_KEY

### 2. Files Created
- ✅ `webhook_bot.py` - Webhook-based bot entry point (replaces polling)
- ✅ `Dockerfile` - Container configuration with all dependencies
- ✅ `fly.toml` - Fly.io configuration with health checks
- ✅ `.dockerignore` - Optimized Docker build

### 3. Code Fixes
- ✅ Fixed import errors in `onboarding_handler.py` (changed from relative to absolute imports)
- ✅ Docker image builds successfully (131 MB)

## ⚠️ Issues Encountered

### Import Error (FIXED)
The bot files used relative imports (`from .config import...`) which don't work when running as standalone scripts. Fixed by changing to absolute imports.

### Deployment Lease Conflict (ONGOING)
Multiple deployment attempts failed due to machine lease conflicts. The Fly.io machine is in a restart loop due to the import error and can't release its lease long enough for redeployment.

## 📋 Next Steps to Complete Deployment (per IMP-001..006)

Commits to deploy (in order):
- IMP-001: Change DOB to two-step date — 28ea863
- IMP-002: Soften Q7/Q8 + partner prefs — 57a0838
- IMP-003: Hierarchical NRI location — ffbef3d
- IMP-004: Pre-message before partner religion — 07018b7
- IMP-005: Sect/caste terminology update — 8256e4b
- IMP-006: Warmth + acknowledgments — 8e83fce

### Staging Deploy (Recommended)
```bash
cd ~/clawd/ventures/jodi/bot
export PATH="/Users/nikunjvora/.fly/bin:$PATH"

# Deploy latest main to staging
flyctl deploy -a jodi-bot-staging

# Set webhook to staging URL (once deploy is healthy)
APP_URL="https://jodi-bot-staging.fly.dev"
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook?url=${APP_URL}/telegram"
```

### Option 2: Destroy & Recreate
If Option 1 fails:
```bash
# Destroy the existing app
flyctl apps destroy jodi-bot-staging --yes

# Recreate and deploy
flyctl apps create jodi-bot-staging --org personal
flyctl secrets set \
  DATABASE_URL="postgresql://postgres.herqdldjaxmfusjjpwdg:syO9opxb37SlEV9Q@aws-1-ap-south-1.pooler.supabase.com:5432/postgres" \
  TELEGRAM_BOT_TOKEN="8439914788:AAGst5JPX6Dl1pDBPOPXpm_sLPw6IF3ZHCc" \
  SUPABASE_URL="https://herqdldjaxmfusjjpwdg.supabase.co" \
  SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlcnFkbGRqYXhtZnVzampwd2RnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA3MzQ3NzcsImV4cCI6MjA4NjMxMDc3N30.IJF22gilascdOyI4gRFZMyI5PJjwuHAODSlcHxsZ7g4" \
  SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhlcnFkbGRqYXhtZnVzampwd2RnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDczNDc3NywiZXhwIjoyMDg2MzEwNzc3fQ.8gTkUSVIyb7pasm__pav-FGPapAt3ILws6wSzVUTggE" \
  -a jodi-bot-staging

flyctl deploy -a jodi-bot-staging
```

## 🔧 Post-Deployment Steps

Once deployment succeeds:

### 1. Set Telegram Webhook
```bash
# Get the app URL
APP_URL="https://jodi-bot-staging.fly.dev"

# Set webhook
curl "https://api.telegram.org/bot8439914788:AAGst5JPX6Dl1pDBPOPXpm_sLPw6IF3ZHCc/setWebhook?url=${APP_URL}/telegram"
```

### 2. Verify Health Endpoint
```bash
curl https://jodi-bot-staging.fly.dev/health
# Should return: OK
```

### 3. Check Logs
```bash
flyctl logs -a jodi-bot-staging
# Should show: "Bot started with webhook: https://jodi-bot-staging.fly.dev/telegram"
```

### 4. Test Bot
Send `/start` to the bot on Telegram to verify it's working.

Prioritized manual path for validation:
- Hindu → Never married → Indian citizen (in India)
  - Confirm: Q5 (children_existing) is skipped
  - Confirm: New Q8 + Q10 partner preference appear in identity basics
  - Confirm: NRI country (Q13) is skipped; State India (Q14) shows
  - Confirm: Pre-message appears before partner religion (Q22)
  - Confirm: Updated sect/caste labels (Q23/Q24) feel natural
  - Confirm: Acknowledgments show after disability (Q11), finances (Q35-39), living-with-parents (Q44)
  - Confirm: Progress nudges at ~25%/50%/75%

## 📊 Resources

- **App**: https://fly.io/apps/jodi-bot-staging
- **Monitoring**: https://fly.io/apps/jodi-bot-staging/monitoring
- **Logs**: `flyctl logs -a jodi-bot-staging`
- **Status**: `flyctl status -a jodi-bot-staging`

## 🔑 Key Information

- **Machine ID**: 89627ea6dd7d98
- **Region**: bom (Mumbai)
- **Image Size**: 131 MB
- **Python**: 3.11-slim
- **Webhook Port**: 8080
- **Health Check**: /health (every 30s)

## 📝 Notes

- Bot uses webhook mode (not polling) for Fly.io deployment
- Health checks configured to auto-restart on failures
- Database connection to Supabase AP South 1 (same region)
- WEBHOOK_URL environment variable needed (set to app URL after deployment)

## Deployment Fix Log (2026-02-21 Evening)

### Issue: Double webhook path causing 404 errors
**Symptom:** Bot receiving webhook calls to `/telegram/telegram` instead of `/telegram`

**Root cause:** `WEBHOOK_URL` environment variable was set to `https://jodi-bot-staging.fly.dev/telegram`, but webhook_bot.py adds `/telegram` again in the setWebhook call.

**Fix:**
```bash
flyctl secrets set WEBHOOK_URL="https://jodi-bot-staging.fly.dev" -a jodi-bot-staging
```

**Corrected webhook registration:**
- Before: `https://jodi-bot-staging.fly.dev/telegram/telegram` ❌
- After: `https://jodi-bot-staging.fly.dev/telegram` ✅

**Status:** Fixed and tested (2026-02-21 19:42 GST)
