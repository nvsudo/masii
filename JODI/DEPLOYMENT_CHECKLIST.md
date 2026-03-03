# ✅ JODI Extraction Pipeline — Deployment Checklist

**Ready to ship:** 2026-02-11  
**Owner:** Kavi → Blitz (integration) → N (approval)

---

## PRE-DEPLOYMENT ✅

### Schema (Production Supabase)
- [x] All 5 tables created
- [x] 31 indexes operational
- [x] 4 SQL helper functions working
- [x] Test data inserted/verified
- [x] Age auto-calculation trigger working
- [x] MVP activation logic tested

**Status:** ✅ **COMPLETE** — All migrations deployed and tested

---

### Code Files
- [x] `extraction_enhancements.py` — DOB validation + buttons
- [x] `bot_tier1_buttons.py` — Button callback handler
- [x] `conversation_v2.py` — Enhanced extraction prompt
- [x] `INTEGRATION_READY_CODE.py` — Copy-paste integration code
- [x] `requirements.txt` — Added `python-dateutil>=2.8.0`

**Status:** ✅ **COMPLETE** — All code ready for integration

---

### Documentation
- [x] `EXTRACTION_PIPELINE_COMPLETE.md` — Full implementation guide
- [x] `READY_TO_SHIP_SUMMARY.md` — Executive summary
- [x] `MIGRATION_COMPLETE_REPORT.md` — Schema deployment report
- [x] `DATA_FIELD_MAPPING.md` — 100+ field mapping
- [x] `INTEGRATION_READY_CODE.py` — Integration examples

**Status:** ✅ **COMPLETE** — All docs ready

---

## BLITZ INTEGRATION (Est. 1 hour)

### Step 1: Install Dependencies
```bash
cd /Users/nikunjvora/clawd/matchmaker/jodi
pip install -r requirements.txt
# New: python-dateutil>=2.8.0
```
- [ ] Dependencies installed
- [ ] No version conflicts

**Estimated time:** 2 minutes

---

### Step 2: Add Imports to bot.py
```python
from bot_tier1_buttons import handle_tier1_button_callback, ask_next_tier1_question_if_needed
from extraction_enhancements import extract_dob_from_message, parse_and_validate_dob
```
- [ ] Imports added
- [ ] No import errors

**Estimated time:** 1 minute

---

### Step 3: Add DOB Validation to handle_message()
Location: After `user_message = update.message.text`, before orchestrator call

```python
potential_dob = extract_dob_from_message(user_message)
if potential_dob:
    validated_dob, error_msg = parse_and_validate_dob(str(potential_dob))
    if error_msg:
        await update.message.reply_text(error_msg)
        print(f"⚠️ [DOB-VALIDATE] Rejected: {error_msg}")
        return
    print(f"✅ [DOB-VALIDATE] Valid DOB: {validated_dob}")
```
- [ ] Code added
- [ ] Indentation correct
- [ ] No syntax errors

**Estimated time:** 5 minutes

---

### Step 4: Replace Callback Handler in main()
Replace:
```python
application.add_handler(CallbackQueryHandler(handle_match_response))
```

With:
```python
async def unified_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    # Tier 1 buttons
    if any(data.startswith(f"{cat}:") for cat in ['gender', 'orientation', 'smoking', 'drinking', 'religion', 'children', 'marital', 'intent', 'timeline', 'diet', 'education']):
        await handle_tier1_button_callback(update, context, db, conv)
    # Match buttons
    elif data.startswith("match_"):
        await handle_match_response(update, context)
    else:
        await query.answer("Unknown button")

application.add_handler(CallbackQueryHandler(unified_callback_handler))
```
- [ ] Old handler removed
- [ ] New handler added
- [ ] All button categories listed

**Estimated time:** 5 minutes

---

### Step 5: (Optional) Add Proactive Button Offers
Location: End of handle_message(), after conversation storage

```python
# After: _save_conversation_history(telegram_id, conversation_history)
await ask_next_tier1_question_if_needed(update, telegram_id, db, conv)
```
- [ ] Code added (optional but recommended)

**Estimated time:** 2 minutes

---

### Step 6: Local Testing
```bash
cd /Users/nikunjvora/clawd/matchmaker/jodi
python3 bot.py
```

Test cases:
- [ ] Bot starts without errors
- [ ] DOB validation: "I was born on Jan 1, 2010" → Error
- [ ] DOB validation: "My birthday is May 15, 1995" → Accepted
- [ ] Button flow: Gender → Smoking → Drinking
- [ ] Button values stored in database
- [ ] Tier 1 completion reaches 100%

**Estimated time:** 15 minutes

---

### Step 7: Staging Deployment
```bash
cd /Users/nikunjvora/clawd/matchmaker/jodi
./EXECUTE_STAGING_DEPLOY.sh
```
- [ ] Staging deployed
- [ ] Telegram webhook updated
- [ ] Bot responds on staging

**Estimated time:** 5 minutes

---

### Step 8: Staging Testing
Same tests as local, but on staging:
- [ ] DOB validation works
- [ ] Buttons appear
- [ ] Button clicks work
- [ ] Data stored correctly
- [ ] Tier progress updates

**Estimated time:** 10 minutes

---

**BLITZ TOTAL TIME:** ~1 hour

---

## N UX REVIEW (Est. 30 minutes)

### UX Flow Testing
- [ ] Start fresh conversation
- [ ] Complete Tier 1 with buttons
- [ ] Button wording feels natural
- [ ] Error messages are clear
- [ ] Flow doesn't feel interrogative

### Button Options Review
For each button category, verify:
- [ ] Gender identity options cover most users
- [ ] Smoking/drinking options are clear
- [ ] Religion options are comprehensive
- [ ] Children intent options are empathetic
- [ ] Marital history options are sensitive

### Iteration Points
Mark any areas needing improvement:
- [ ] Button wording changes needed? (List below)
- [ ] Additional button options needed? (List below)
- [ ] Flow order changes? (List below)
- [ ] Error message improvements? (List below)

**Notes:**
```
[Space for N's feedback]
```

**N TOTAL TIME:** ~30 minutes

---

## PRODUCTION DEPLOYMENT

### Pre-Production Checklist
- [ ] All Blitz integration steps complete
- [ ] Staging fully tested
- [ ] N has approved UX
- [ ] Any iteration points addressed
- [ ] Team is ready for deployment

### Production Deploy
```bash
cd /Users/nikunjvora/clawd/matchmaker/jodi
# Deploy to production (command TBD based on your setup)
fly deploy --app jodi-prod
```
- [ ] Production deployed
- [ ] Webhook updated
- [ ] Bot responds
- [ ] No errors in logs

### Post-Deploy Verification
- [ ] Send test message to bot
- [ ] Verify DOB validation works
- [ ] Verify buttons appear
- [ ] Check database for test data
- [ ] Monitor logs for 10 minutes

**Deployment time:** 10 minutes

---

## POST-DEPLOYMENT

### Monitoring (First 24 hours)
- [ ] Check error logs every 2 hours
- [ ] Monitor button click success rate
- [ ] Track DOB validation rejections
- [ ] Watch Tier 1 completion rates

### User Feedback Collection
- [ ] First 10 users: Individual check-ins
- [ ] First 50 users: Survey button flow
- [ ] First 100 users: Analyze completion rates

### Iteration Backlog
Based on feedback, prioritize:
1. Button wording improvements
2. Additional button options
3. Flow order changes
4. New categorical fields
5. DOB error message refinements

---

## ROLLBACK PLAN (If Needed)

If critical issues arise:

### Emergency Rollback
```bash
# Revert to previous bot.py version
git checkout HEAD~1 -- bot.py conversation_v2.py

# Redeploy
fly deploy --app jodi-prod
```
- [ ] Previous version identified
- [ ] Rollback tested on staging
- [ ] Rollback docs ready

### Schema Rollback
❌ **NOT RECOMMENDED** — Schema is additive, no breaking changes

New columns/tables can stay even if code rolls back.

---

## SUCCESS METRICS

### Technical Metrics (Week 1)
- [ ] 0 critical errors
- [ ] <5% button callback failures
- [ ] 100% DOB validation accuracy
- [ ] >95% Tier 1 completion rate

### UX Metrics (Week 1)
- [ ] <3% user drop-off during Tier 1
- [ ] >90% button adoption (vs free text)
- [ ] Avg Tier 1 completion time: 5-10 min
- [ ] Positive user feedback

### Business Metrics (Week 2)
- [ ] >70% users reach MVP (T1 100% + T2 70%)
- [ ] >50% MVP users get matched
- [ ] <5% profile quality complaints

---

## DEPENDENCIES SUMMARY

### Python Packages
- `python-telegram-bot>=20.0`
- `psycopg2-binary>=2.9`
- `anthropic>=0.18`
- `python-dotenv>=1.0`
- `supabase>=2.0`
- `aiohttp>=3.8.0`
- **NEW:** `python-dateutil>=2.8.0`

### Database
- Supabase (Postgres 15+)
- 5 tables: users, user_signals, user_preferences, tier_progress, matches
- 31 indexes
- 4 SQL functions

### External Services
- Telegram Bot API
- Anthropic Claude API (Sonnet 4)

---

## CONTACTS

- **Schema/DB:** Kavi
- **Integration:** Blitz
- **UX Review:** N
- **Production Deploy:** Kavi + Blitz
- **Monitoring:** Entire team

---

## TIMELINE ESTIMATE

| Phase | Owner | Time | Status |
|-------|-------|------|--------|
| Schema deployment | Kavi | — | ✅ COMPLETE |
| Code development | Kavi | — | ✅ COMPLETE |
| Integration | Blitz | 1 hour | ⏳ PENDING |
| Local testing | Blitz | 15 min | ⏳ PENDING |
| Staging deploy | Blitz | 5 min | ⏳ PENDING |
| Staging testing | Blitz | 10 min | ⏳ PENDING |
| UX review | N | 30 min | ⏳ PENDING |
| Iteration (if needed) | Blitz | 30 min | ⏳ PENDING |
| Production deploy | Blitz | 10 min | ⏳ PENDING |
| **TOTAL** | — | **~2.5 hours** | ⏳ **IN PROGRESS** |

---

## READY TO SHIP ✅

**Schema:** ✅ Deployed  
**Code:** ✅ Ready  
**Docs:** ✅ Complete  
**Tests:** ✅ Defined  
**Rollback:** ✅ Planned

**Next:** Blitz integration (1 hour)

---

**Questions?** Ping Kavi, Blitz, or N in group chat.

**Let's ship it!** 🚀
