# Masii Post-Login Dashboard + Orchestrator - Verification Guide

## What's Been Shipped

### 1. ✅ Database Schema Changes
- Added `user_id UUID` column to `form_submissions`
- Added `current_question TEXT` column for draft tracking
- Added `status TEXT` column (draft/submitted/processed)
- Created index on `user_id` for fast lookups
- Updated existing rows to have `status = 'submitted'`

**Verify:**
```sql
\d form_submissions
-- Should show: user_id, current_question, status columns
```

### 2. ✅ Backend API Endpoints (main.py)

**New Endpoints:**
- `GET /api/draft?user_id={id}` - Returns draft submission
- `PATCH /api/draft` - Upsert draft row (create or update)
- `PATCH /api/intake/{submission_id}` - Update existing submission

**Test:**
```bash
# Test draft endpoint (should return 404 for new user)
curl "https://masii-bot.fly.dev/api/draft?user_id=test-uuid-123"

# Test health check
curl "https://masii-bot.fly.dev/health"
```

### 3. ✅ Orchestrator Script (orchestrator.py)

**Purpose:** Process `form_submissions` → populate `users`, `user_preferences`, `user_signals` tables

**Features:**
- Groups fields by table based on `dbTable` property in form config
- Upserts into users, preferences, signals tables
- Marks submissions as processed
- Handles errors gracefully (logs, skips, continues)
- Supports dry-run mode

**Test:**
```bash
# Dry run (shows what would happen)
python3 orchestrator.py --dry-run

# Process all pending
python3 orchestrator.py

# Process specific submission
python3 orchestrator.py --id 123
```

### 4. ✅ Dashboard Page (me.html)

**Features:**
- Shows user status based on `form_submissions.status`
- Dynamic CTAs:
  - `draft` → "Continue where you left off" → /form
  - `submitted` → "Masii is reviewing" + "Edit my answers" link
  - `processed` → "You're active!" + "Edit profile" link
- Redirects to /form if no submission exists
- Requires authentication (uses Supabase auth)

**Test:**
```
1. Visit masii.co/me.html (not logged in) → redirects to /login.html
2. Log in → Visit /me.html → see dashboard with appropriate status
```

### 5. ✅ Form Draft Support (form.js patches)

**Features:**
- Loads existing draft on page load (if authenticated)
- Auto-saves draft to server every 2 seconds after answer change
- Supports edit mode via `?mode=edit` query param
- Pre-fills form with existing submission data
- Redirects to dashboard if submission exists (unless in edit mode)

**Test:**
```
1. Start form, answer 10 questions, close browser
2. Return to /form.html → progress restored from server
3. Visit /me.html → See "Continue where you left off"
4. Click → Form resumes from where you left off
```

### 6. ✅ Edit Mode

**Features:**
- Form can be edited via `/form.html?mode=edit`
- Pre-fills all existing answers
- On submit: PATCH existing submission (not INSERT)
- Returns to dashboard after save

**Test:**
```
1. Complete form and submit
2. Visit /me.html → Click "Edit my answers"
3. Form loads with all answers pre-filled
4. Change some answers, submit
5. Back to /me.html → See updated status
```

---

## Files Created/Modified

**Created:**
- `/ventures/masii/website/me.html` - Dashboard page
- `/ventures/masii/backend-api/orchestrator.py` - Orchestrator script
- `apply_schema.py` - Schema migration script (can be deleted)

**Modified:**
- `/ventures/masii/backend-api/main.py` - Added draft endpoints
- `/ventures/masii/website/js/form.js` - Added draft save/load + edit mode

---

## Deployment Checklist

### Backend (main.py)
```bash
cd /Users/nikunjvora/clawd/ventures/masii/backend-api

# Test locally
uvicorn main:app --reload

# Deploy to Fly.io
fly deploy
```

### Website (me.html, form.js)
```bash
# If using static hosting, upload:
# - /website/me.html
# - /website/js/form.js (patched version)

# If using Git deploy, commit and push:
git add website/me.html website/js/form.js
git commit -m "Add post-login dashboard + draft support"
git push origin main
```

### Orchestrator
```bash
# Run once to process pending submissions
cd /Users/nikunjvora/clawd/ventures/masii/backend-api
python3 orchestrator.py

# Or schedule as cron job (e.g., every 5 minutes)
# crontab -e
# */5 * * * * cd /path/to/backend-api && python3 orchestrator.py >> orchestrator.log 2>&1
```

---

## Manual Verification Steps

### 1. Dashboard Flow
1. Visit https://masii.co/me.html (not logged in)
   - ✅ Should redirect to /login.html

2. Log in with email (OTP flow)
   - ✅ Should redirect to /form.html (if no submission)

3. Start form, answer 5 questions, note progress
   - ✅ Draft should auto-save every 2 seconds (check console: "💾 Draft saved")

4. Close browser, return to /form.html
   - ✅ Should load with 5 answers pre-filled

5. Visit /me.html
   - ✅ Should show "Draft" badge + "Continue where you left off" button

6. Complete form and submit
   - ✅ Should redirect to /me.html
   - ✅ Should show "Under Review" badge + "Edit my answers" button

### 2. Orchestrator Flow
1. Check database for pending submissions
   ```sql
   SELECT id, status, processed FROM form_submissions WHERE status = 'submitted' AND processed = false;
   ```

2. Run orchestrator in dry-run mode
   ```bash
   python3 orchestrator.py --dry-run
   ```
   - ✅ Should show what it would process (no changes)

3. Run orchestrator for real
   ```bash
   python3 orchestrator.py
   ```
   - ✅ Should process submissions
   - ✅ Check `users`, `user_preferences`, `user_signals` tables for new rows
   - ✅ Check `form_submissions`: `status` should be 'processed', `processed` should be `true`

4. Visit /me.html after processing
   - ✅ Should show "Active" badge + "Edit profile" button

### 3. Edit Mode Flow
1. Visit /me.html (after submission is processed)
   - ✅ Click "Edit profile"

2. Should redirect to `/form.html?mode=edit`
   - ✅ Form loads with all answers pre-filled

3. Change some answers, submit
   - ✅ Should update existing submission (PATCH, not INSERT)
   - ✅ Should set `status = 'submitted'`, `processed = false`

4. Run orchestrator again
   - ✅ Should re-process the updated submission

---

## Design Validation

Dashboard should match existing Masii brand:
- ✅ Cream background (#FDF6EE)
- ✅ Terracotta accent (#C4653A)
- ✅ Playfair Display headings
- ✅ DM Sans body text
- ✅ Warm, friendly tone

---

## Known Limitations / Future Work

1. **Orchestrator field mapping:**
   - Currently uses `dbTable` property from form config
   - May need refinement for complex multi-step questions
   - Test with all 81 questions to ensure correct mapping

2. **Draft conflict resolution:**
   - If user starts form on 2 devices simultaneously, last write wins
   - Could add version tracking + conflict UI in the future

3. **Error handling:**
   - Draft save failures are logged but don't block user
   - Could add retry logic or offline queue

4. **Performance:**
   - Orchestrator processes all pending submissions sequentially
   - For scale, could add parallel processing + queue system

---

## Production Readiness

**Backend API (main.py):**
- ✅ Error handling (try/catch with rollback)
- ✅ Logging (INFO level for operations)
- ✅ CORS configured
- ✅ Database transactions (BEGIN/COMMIT/ROLLBACK)

**Orchestrator:**
- ✅ Dry-run mode for safe testing
- ✅ Error handling per submission (skip and continue)
- ✅ Transaction safety (ROLLBACK on error)
- ✅ Logging with timestamps

**Frontend (me.html, form.js):**
- ✅ Loading states
- ✅ Error handling (404, network errors)
- ✅ Redirects for auth/status
- ✅ Responsive design (mobile-friendly)

---

## Support / Debugging

**Backend logs:**
```bash
# Fly.io logs
fly logs

# Local test
uvicorn main:app --reload --log-level debug
```

**Database inspection:**
```sql
-- Check submissions by status
SELECT status, COUNT(*) FROM form_submissions GROUP BY status;

-- Check recent submissions
SELECT id, status, current_question, created_at 
FROM form_submissions 
ORDER BY created_at DESC 
LIMIT 10;

-- Check users created by orchestrator
SELECT id, full_name, preferred_name, email, created_at 
FROM users 
ORDER BY created_at DESC 
LIMIT 10;
```

**Browser console:**
- Look for "💾 Draft saved" messages
- Check Network tab for API calls
- Look for "✅ Loaded draft with X answers"

---

## Done! 🎉

Both deliverables shipped:
1. ✅ Post-Login Dashboard + Draft UX
2. ✅ Orchestrator (form_submissions → users/preferences/signals)

Ready for production deployment.
