# KAVI BRIEFING — Schema + Extraction Pipeline Execution

**Date:** 2026-02-12  
**From:** A  
**Status:** N APPROVED — EXECUTE NOW

---

## N's Final Approvals & Clarifications

✅ **DOB parsing:** Implement age validation (18-80 years). Extract from conversation.  
✅ **Buttons:** Use Telegram buttons where accuracy matters (gender, smoking, drinking, etc.)  
✅ **Income privacy:** Current wording is fine, keep as-is  
✅ **Wording:** Iterate and improve over time (not blocking)  
✅ **LLM CRUD:** Ensure conversation agent can handle all profile operations later (add/update/delete fields)  
❌ **Photo validation:** Skip photo upload/validation entirely for now

---

## Critical Action Items

1. **Add missing fields to schema**  
   - Some fields from the 100+ data point framework may not exist in current schema  
   - Cross-reference `Matchmaking_Data_Capture_Framework_v1.docx` and add all missing fields

2. **Age validation**  
   - Extract DOB from conversation  
   - Validate age range: 18-80 years  
   - Store as hard filter (indexed column)

3. **Button-based accuracy**  
   - Use Telegram inline buttons for categorical fields (gender, smoking, drinking, diet, etc.)  
   - Reduces LLM parsing errors on critical demographic fields

4. **LLM CRUD readiness**  
   - Ensure conversation agent can add/update/delete profile fields via natural language  
   - Test with sample prompts: "Update my height to 5'10", "Remove my smoking preference", etc.

---

## Reference Documents

- `/Users/nikunjvora/clawd/JODI/Matchmaking_Data_Capture_Framework_v1.docx` (100+ data points)
- `/Users/nikunjvora/clawd/JODI_PROJECT.md` (project hub)
- Previous schema work in your workspace

---

## Execution Timeline

**Ship ASAP** — N wants this moving. Prioritize schema completeness + extraction accuracy.

---

## Questions?

Ping A or N directly if blockers arise.
