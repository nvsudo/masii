# Masii Updates - Post-Login Dashboard + Orchestrator

## 🎉 Completed: March 22, 2026

Both deliverables have been shipped and are ready for production deployment.

---

## What Was Built

### 1. Post-Login Dashboard & UX
- **Dashboard page** (`/me.html`) - Shows submission status with dynamic CTAs
- **Draft saving** - Auto-saves form progress to server every 2 seconds
- **Edit mode** - Users can edit submitted forms via `/form.html?mode=edit`
- **Smart routing** - Redirects based on auth and submission status
- **Backend endpoints** - GET/PATCH `/api/draft` for draft management

### 2. Orchestrator
- **Processing script** (`orchestrator.py`) - Transforms form submissions into user profiles
- **Field mapping** - Reads `dbTable` property from form config
- **Table population** - Upserts into `users`, `user_preferences`, `user_signals`
- **Error handling** - Logs errors, skips failures, continues processing
- **Dry-run mode** - Test what would happen without making changes

---

## Files Changed

### Created
```
/ventures/masii/website/me.html              - Dashboard UI
/ventures/masii/backend-api/orchestrator.py  - Processing script
/ventures/masii/VERIFICATION.md              - Testing guide
/ventures/masii/DELIVERY_SUMMARY.md          - Implementation details
```

### Modified
```
/ventures/masii/backend-api/main.py          - Added draft endpoints
/ventures/masii/website/js/form.js           - Added draft save/load
```

### Database
```sql
ALTER TABLE form_submissions 
ADD COLUMN user_id UUID,
ADD COLUMN current_question TEXT,
ADD COLUMN status TEXT DEFAULT 'submitted';

CREATE INDEX idx_form_submissions_user_id ON form_submissions(user_id);
```

---

## Quick Start

### Run Orchestrator (One-time)
```bash
cd /Users/nikunjvora/clawd/ventures/masii/backend-api

# See what would happen
python3 orchestrator.py --dry-run

# Process pending submissions
python3 orchestrator.py
```

### Deploy Backend
```bash
cd /Users/nikunjvora/clawd/ventures/masii/backend-api
fly deploy
```

### Test Dashboard
1. Visit https://masii.co/me.html
2. Log in if not authenticated
3. See status-based dashboard:
   - **Draft** → "Continue where you left off"
   - **Submitted** → "Masii is reviewing"
   - **Processed** → "You're active!"

---

## User Flows

### New User
1. Visit `/form.html` → prompted to sign in
2. Sign in with email (OTP)
3. Start form → answers auto-save as draft
4. Close browser, return later → progress restored
5. Complete form → redirected to `/me.html`
6. Dashboard shows "Under Review"

### Existing User (Edit)
1. Visit `/me.html` → sees "Edit profile" button
2. Click → redirects to `/form.html?mode=edit`
3. Form pre-fills with existing answers
4. User edits answers → auto-saves
5. Submit → updates existing submission
6. Redirected back to `/me.html`

### Admin/Backend (Process Submissions)
1. Run `python3 orchestrator.py`
2. Script fetches unprocessed submissions
3. Groups answers by table (users, preferences, signals)
4. Upserts into database
5. Marks submissions as processed
6. Dashboard updates to "Active" status

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Flow                            │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   /form.html   │ ← Start form
                    └────────────────┘
                             │
                             │ (auto-save every 2s)
                             ▼
                    ┌────────────────┐
                    │ PATCH /api/draft│ ← Save progress
                    └────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │form_submissions│ ← Draft stored
                    │ status='draft' │
                    └────────────────┘
                             │
                             │ (user completes form)
                             ▼
                    ┌────────────────┐
                    │ POST /api/intake│ ← Submit
                    └────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │form_submissions│
                    │status='submitted'│
                    └────────────────┘
                             │
                             │ (cron/manual)
                             ▼
                    ┌────────────────┐
                    │ orchestrator.py │ ← Process
                    └────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
    ┌────────┐      ┌───────────────┐    ┌─────────────┐
    │ users  │      │user_preferences│    │user_signals │
    └────────┘      └───────────────┘    └─────────────┘
         │
         ▼
┌────────────────┐
│form_submissions│
│status='processed'│
└────────────────┘
         │
         ▼
┌────────────────┐
│   /me.html     │ ← Dashboard shows "Active"
└────────────────┘
```

---

## API Endpoints

### GET /api/draft?user_id={id}
Returns draft submission for user.

**Response:**
```json
{
  "status": "draft",
  "current_question": "education_level",
  "submission_data": {
    "answers": { ... },
    "meta": { ... }
  }
}
```

### PATCH /api/draft
Upsert draft row.

**Request:**
```json
{
  "user_id": "uuid",
  "submission_data": { ... },
  "current_question": "education_level"
}
```

### PATCH /api/intake/{submission_id}
Update existing submission (edit mode).

**Request:**
```json
{
  "phone": "+1234567890",
  "name": "John Doe",
  "preferred_name": "John",
  "answers": { ... },
  "meta": { ... }
}
```

---

## Database Schema

### form_submissions (modified)
```sql
id              SERIAL PRIMARY KEY
user_id         UUID               -- NEW: Links to Supabase auth
phone           TEXT
email           TEXT
full_name       TEXT
preferred_name  TEXT
submission_data JSONB
intent          TEXT
current_question TEXT              -- NEW: For resuming draft
status          TEXT               -- NEW: draft/submitted/processed
processed       BOOLEAN
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

### users (populated by orchestrator)
```sql
id              UUID PRIMARY KEY
email           TEXT
phone           TEXT
full_name       TEXT
preferred_name  TEXT
gender          TEXT
date_of_birth   DATE
... (81 form fields map here)
```

### user_preferences (populated by orchestrator)
```sql
id              UUID PRIMARY KEY
user_id         UUID REFERENCES users(id)
pref_age_min    INTEGER
pref_age_max    INTEGER
pref_religion   TEXT
... (preference fields)
```

### user_signals (populated by orchestrator)
```sql
id              UUID PRIMARY KEY
user_id         UUID REFERENCES users(id)
diet            TEXT
drinking        TEXT
smoking         TEXT
... (lifestyle signals)
```

---

## Deployment Checklist

- [ ] Backend deployed to Fly.io (`fly deploy`)
- [ ] Frontend deployed (commit + push `me.html`, `form.js`)
- [ ] Run orchestrator once to process pending (`python3 orchestrator.py`)
- [ ] Schedule orchestrator cron (every 5 min)
- [ ] Test dashboard flow (new user, edit mode)
- [ ] Verify processed submissions in `users` table

---

## Monitoring

### Backend Logs
```bash
fly logs -a masii-bot
```

### Database Queries
```sql
-- Submission status breakdown
SELECT status, COUNT(*) FROM form_submissions GROUP BY status;

-- Recent submissions
SELECT id, status, email, created_at 
FROM form_submissions 
ORDER BY created_at DESC 
LIMIT 10;

-- Users created today
SELECT COUNT(*) FROM users WHERE created_at::date = CURRENT_DATE;
```

### Orchestrator Logs
```bash
tail -f /path/to/orchestrator.log
```

---

## Troubleshooting

**Issue:** Dashboard redirects to login even when logged in
- **Fix:** Check Supabase auth session in browser console
- **Command:** `await window.getSession()` in console

**Issue:** Draft not saving
- **Fix:** Check browser console for "💾 Draft saved" messages
- **Fix:** Verify `user_id` is set: `currentUserId` in console

**Issue:** Orchestrator fails to process submission
- **Fix:** Run with `--dry-run` to see what would happen
- **Fix:** Check logs for field mapping errors
- **Fix:** Verify `dbTable` property in form config

---

## Next Steps (Optional)

1. **Schedule orchestrator as cron:**
   ```bash
   */5 * * * * cd /path/to/backend-api && python3 orchestrator.py >> orchestrator.log 2>&1
   ```

2. **Add serverless trigger:**
   - Fly.io cron job
   - Supabase webhook on new submission

3. **Admin dashboard:**
   - View all submissions
   - Manual orchestrator trigger
   - User profile browser

---

## Support

- **Documentation:** See `VERIFICATION.md` for detailed testing
- **Implementation:** See `DELIVERY_SUMMARY.md` for technical details
- **Backend Code:** `/backend-api/main.py`, `/backend-api/orchestrator.py`
- **Frontend Code:** `/website/me.html`, `/website/js/form.js`

---

Built by **blitz-agent** | March 22, 2026
