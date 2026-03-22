# Masii Bot API

FastAPI backend for Masii form submissions.

## Deployment

**App Name:** `masii-bot`  
**URL:** https://masii-bot.fly.dev  
**Region:** Singapore (sin)  
**Status:** ✅ Deployed

## Endpoints

### GET /health
Health check endpoint.

**Response:**
```json
{"status": "ok", "service": "masii-bot", "version": "1.0.0"}
```

### POST /api/intake
Form submission endpoint. Accepts form data from masii.co and stores in Supabase.

**Request:**
```json
{
  "phone": "+91XXXXXXXXXX",
  "name": "Full Name",
  "preferred_name": "Nick",
  "answers": {
    "field_name": {"value": "answer", "table": "users|preferences|signals"},
    ...
  },
  "meta": {"intent": "self", "email": "user@email.com"}
}
```

**Response (Success):**
```json
{
  "success": true,
  "submission_id": 1,
  "message": "Form submitted successfully. Masii will process it shortly."
}
```

**Response (Error):**
```json
{
  "detail": "Missing required field: phone"
}
```

## Database

**Supabase Project:** herqdldjaxmfusjjpwdg  
**Connection:** Pooler (IPv4)  
**Region:** Asia South 1 (Mumbai)

### Schema

The API uses a staging table approach:

**Table:** `form_submissions`
- `id` - Serial primary key
- `phone` - Phone number (indexed)
- `email` - Email address (indexed)
- `full_name` - Full name
- `preferred_name` - Preferred name
- `submission_data` - JSONB (full payload)
- `intent` - "self" or "proxy"
- `processed` - Boolean flag
- `created_at` - Timestamp
- `updated_at` - Timestamp

Submissions are stored in this staging table and processed by the Masii orchestrator into the final schema (users, preferences, signals tables).

## Verification

```bash
# Health check
curl https://masii-bot.fly.dev/health

# Test submission
curl -X POST https://masii-bot.fly.dev/api/intake \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+919876543210",
    "name": "Test User",
    "preferred_name": "Testy",
    "answers": {
      "gender": {"value": "Male", "table": "users"}
    },
    "meta": {"intent": "self", "email": "test@example.com"}
  }'
```

## Deployment Commands

```bash
# Deploy
cd /Users/nikunjvora/clawd/ventures/masii/backend-api
flyctl deploy

# View logs
flyctl logs

# SSH into container
flyctl ssh console

# Check status
flyctl status

# Scale
flyctl scale count 2
```

## Environment Variables

The app uses the hardcoded Supabase connection string. To change it:

```bash
flyctl secrets set DATABASE_URL="postgresql://..."
```

## Architecture

- **Runtime:** Python 3.12 (slim)
- **Framework:** FastAPI + Uvicorn
- **Database:** PostgreSQL (Supabase)
- **Auto-scaling:** 0-2 machines (stops when idle)
- **Memory:** 256 MB per machine
- **CPU:** 1 shared CPU

## Files

- `main.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container definition
- `fly.toml` - Fly.io configuration

## Next Steps

1. Build Masii orchestrator to process `form_submissions` table
2. Migrate data from staging to `users`, `preferences`, `signals` tables
3. Add authentication/API keys if needed
4. Set up monitoring and alerts
5. Configure CORS for production domains

---

**Deployed:** 2026-03-22  
**By:** Blitz (subagent)
