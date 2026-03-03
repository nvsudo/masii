# JODI Telegram Bot - Deployment Plan

## Status: In Progress 🔄

**Date**: February 21, 2026  
**Owner**: Blitz  
**Coordinator**: Kavi (schema & infra)

---

## Implementation Progress

### ✅ Completed

- [x] Project structure created
- [x] Core bot framework (bot.py)
- [x] Onboarding handler with button flow
- [x] Conditional logic router
- [x] Input validation module
- [x] Database adapter (Supabase Postgres)
- [x] Session state management
- [x] Photo upload handling
- [x] Error handling
- [x] Config system (Q1-Q17 defined)
- [x] README and documentation

### 🔄 In Progress

- [ ] **Config completion** (Q18-Q77) - Codex generating now
- [ ] **Schema coordination with Kavi** - Pending
- [ ] **Testing & validation**

### ⏳ Pending

- [ ] Deploy to staging (Fly.io)
- [ ] End-to-end testing with real users
- [ ] Bug fixes from testing
- [ ] Production deployment

---

## Schema Coordination with Kavi

### Database Tables Required

1. **users** - Main user profile table
   - Columns: telegram_id, gender_identity, date_of_birth, religion, caste_community, etc.
   - Needs: All direct-field columns from Q1-77

2. **user_preferences** - Partner preferences (JSONB)
   - Column: preferences (JSONB)
   - Contains: partner_religion_pref, partner_location_pref, pref_age_range, etc.

3. **user_signals** - Personality/lifestyle signals (JSONB)
   - Column: signals (JSONB)
   - Contains: career_ambition, social_style, fitness_frequency, etc.

4. **conversation_state** - Session persistence
   - Columns: user_id, session_data (JSONB), last_active
   - Status: ✅ Should exist from previous work

5. **user_photos** - Photo storage
   - Columns: user_id, photo_url, photo_type, uploaded_at
   - Status: ❓ Needs verification

### Schema Verification Needed

**Action**: Reach out to Kavi to verify:
1. Are all required columns in `users` table created?
2. Does `conversation_state` table exist with correct structure?
3. Does `user_photos` table exist?
4. Are JSONB columns (`preferences`, `signals`) indexed for queries?

**Reference**: `/ventures/jodi/schema/` - Check migration files

---

## Testing Plan

### Unit Tests

1. **Conditional Logic**
   ```bash
   python conditional_logic.py
   ```
   - Test 4 user paths
   - Verify skip logic works correctly
   - Validate question counts

2. **Validation**
   - Date of birth parsing
   - Height conversion (cm / feet'inches)
   - Age range validation

3. **Database Adapter**
   - Session save/load
   - Answer persistence
   - Photo storage

### Integration Tests

Test complete user flows:

1. **Path 1: Hindu, never married, India**
   - Expected: ~75 questions
   - Verify caste/manglik questions show
   - Verify Q11 (country) skipped

2. **Path 2: Muslim, never married, India**
   - Expected: ~71 questions
   - Verify caste questions skipped
   - Verify sect shows Muslim options

3. **Path 3: NRI Hindu, abroad**
   - Expected: ~75 questions
   - Verify Q11 (country) shows
   - Verify Q12 (state) skipped
   - Verify Q17 (settling country) shows

4. **Path 4: Divorced, has children**
   - Expected: ~76 questions
   - Verify Q5 (children_existing) shows
   - All other paths work

### End-to-End Testing

Manual testing with bot:

1. Start fresh user → complete full flow → verify DB
2. Exit mid-flow → restart → verify resume works
3. Upload 1 photo → add more → verify storage
4. Invalid inputs → verify error messages
5. Sticker during buttons → verify gentle reminder

---

## Deployment Steps

### Staging Deployment

1. **Prepare Environment**
   ```bash
   cd /ventures/jodi/bot
   ```

2. **Create staging config**
   - Create `fly.staging.toml`
   - Set environment variables via Fly secrets

3. **Deploy**
   ```bash
   fly deploy --config fly.staging.toml
   ```

4. **Test with 5 users**
   - Invite testers via Telegram
   - Monitor logs: `fly logs -a jodi-matchmaker-staging`
   - Track completion rates

5. **Bug fixes**
   - Iterate based on feedback
   - Redeploy as needed

### Production Deployment

**Gating Criteria** (must pass before prod):
- [ ] Zero crashes in staging
- [ ] 80%+ users complete full flow
- [ ] All 4 test paths validated
- [ ] Photo upload works reliably
- [ ] Resume from pause works correctly
- [ ] Kavi approval on schema stability

**Deploy Command**:
```bash
fly deploy --config fly.production.toml
```

---

## Rollout Timeline

| Phase | Timeline | Owner | Status |
|-------|----------|-------|--------|
| Config completion | 30 min | Blitz | 🔄 In progress |
| Schema coordination | 1 hour | Kavi + Blitz | ⏳ Pending |
| Unit testing | 2 hours | Blitz | ⏳ Pending |
| Staging deploy | 30 min | Kavi | ⏳ Pending |
| E2E testing | 4 hours | Blitz | ⏳ Pending |
| Bug fixes | 2-4 hours | Blitz | ⏳ Pending |
| Production deploy | 30 min | Kavi | ⏳ Pending |
| **Total** | **1-1.5 days** | - | - |

**Target**: Ship to production by **Feb 22, 2026 EOD**

---

## Risks & Mitigation

### Risk 1: Schema Mismatch
**Impact**: Bot crashes when saving answers  
**Mitigation**: Coordinate with Kavi ASAP, verify all columns exist  
**Status**: ⚠️ High priority

### Risk 2: Complex Conditional Logic
**Impact**: Users see wrong questions or get stuck  
**Mitigation**: Comprehensive unit tests, validate all 4 paths  
**Status**: ✅ Tests written

### Risk 3: Telegram API Rate Limits
**Impact**: Bot slows down or fails for multiple users  
**Mitigation**: Use async properly, batch operations where possible  
**Status**: ✅ Using python-telegram-bot async

### Risk 4: Photo Storage
**Impact**: Photos lost or not displaying  
**Mitigation**: Use Telegram file_id initially, migrate to S3 later  
**Status**: ✅ Handled

---

## Success Metrics

**Immediate (First Week)**:
- 90%+ users complete intro (Message 1-7)
- 70%+ users complete Section A (Q1-9)
- 50%+ users complete full onboarding (Q1-77)
- Zero crashes or data loss

**Short-term (First Month)**:
- Average completion time: <15 minutes
- Resume rate: 60%+ of paused users return
- Photo upload success: 95%+
- User satisfaction: "This was easy" feedback

---

## Next Actions

1. **Wait for Codex** to complete config.py (Q18-Q77)
2. **Coordinate with Kavi** on schema verification
3. **Run conditional logic tests** to validate branching
4. **Deploy to staging**
5. **E2E test** with 5 users
6. **Ship to production**

---

**Last Updated**: Feb 21, 2026 - Blitz  
**Next Update**: After Codex completes + Kavi coordination
