# JODI — Complete Roadmap (As of 2026-02-22 12:20)

**Total Items:** 20  
**Done:** 10 | **Backlog:** 10

---

## 🚨 P0 — Critical (Ship This Week)

| # | ID | Type | Description | ETA | Status |
|---|----|------|-------------|-----|--------|
| 1 | **FEAT-006** | Feature | Entry Flow: Self vs Proxy + Existing User Check | 2 days | Backlog |
| 2 | **FEAT-003** | Feature | Consent Handling for Proxy Submissions (superseded by FEAT-006) | N/A | Backlog |

**P0 Summary:** 2 items remaining (entry flow with proxy/consent + state-aware resume)

---

## 🔥 P1 — High (Ship This Sprint)

| # | ID | Type | Description | ETA | Status |
|---|----|------|-------------|-----|--------|
| 1 | **IMP-006** | Improvement | Conversational Warmth & Empathy | 1-2 days | Backlog |
| 2 | **IMP-005** | Improvement | Sect/Denomination Cultural Terminology Review | 2 days | Backlog |
| 3 | **IMP-004** | Improvement | Partner Religion Needs Expectation Setting | <1 day | Backlog |
| 4 | **IMP-003** | Improvement | NRI Location Hierarchical Drill-Down | 1 day | Backlog |
| 5 | **IMP-002** | Improvement | Body Type & Complexion Softer Phrasing | 1 day | Backlog |
| 6 | **IMP-001** | Improvement | DOB: Two-Step Button Selection | <1 day | Backlog |
| 7 | **FEAT-004** | Feature | Language Selection & Localization (11 languages) | 3-5 days | Backlog |
| 8 | **FEAT-005** | Feature | Automated Conditional Logic Tests | 1 day | Backlog |

**P1 Summary:** 8 items (~10-12 days total work)

---

## 📊 P2 — Medium (This Month)

| # | ID | Type | Description | ETA | Status |
|---|----|------|-------------|-----|--------|
| 1 | **FEAT-007** | Feature | Multi-Channel Identity + State Management | 4 weeks | Backlog |

**P2 Summary:** 1 item (phased rollout: Telegram → WhatsApp → Web)

---

## 📝 P3 — Nice to Have (Backlog)

*Empty*

---

## ✅ Done (Shipped — Last 48 Hours)

| # | ID | Type | Description | Shipped | Time |
|---|----|------|-------------|---------|------|
| 1 | **IMP-007** | Improvement | Section Transitions (9 buffers) | 2026-02-22 12:10 | 25 min |
| 2 | **BUG-006** | Bug | Loop Detection (universal, any question) | 2026-02-22 12:10 | 20 min |
| 3 | **BUG-005** | Bug | Q22 Caste/Community Options Fixed | 2026-02-21 22:38 | 15 min |
| 4 | **BUG-004** | Bug | Q21 Sect/Denomination Options Fixed | 2026-02-21 22:30 | 20 min |
| 5 | **BUG-003** | Bug | Q16 Tier Boundary Error Fixed | 2026-02-21 22:08 | 30 min |
| 6 | **BUG-002** | Bug | User Preferences Save Error Fixed | 2026-02-21 20:50 | 10 min |
| 7 | **BUG-001** | Bug | Schema Mismatch (massive fix) | 2026-02-21 20:13 | 8 min |
| 8 | **FEAT-000** | Feature | 100+ Data Point Framework | 2026-02-12 | — |
| 9 | **FEAT-001** | Feature | Supabase Database Schema | 2026-02-12 | — |
| 10 | **FEAT-002** | Feature | Telegram Onboarding Sequence | 2026-02-12 | — |

---

## 📈 Velocity Metrics (Last 48h)

- **Items shipped:** 7 bugs + 1 improvement = 8 items
- **Total dev time:** ~2.5 hours
- **Average:** 18 minutes per fix
- **Blockers cleared:** 7 (all critical path bugs resolved)

---

## 🎯 Recommended Week 1 Focus

| Priority | Item | Why | ETA |
|----------|------|-----|-----|
| 1 | **FEAT-006** (Entry Flow) | Enables proxy submissions + returning users (huge UX win) | 2 days |
| 2 | **IMP-006** (Warmth) | Makes bot feel human, reduces dropoffs | 1-2 days |
| 3 | **FEAT-005** (Tests) | Prevents future loop bugs, enables confident refactoring | 1 day |

**Total:** 4-5 days (Week 1 complete)

---

## 🎯 Recommended Week 2 Focus

| Priority | Item | Why | ETA |
|----------|------|-----|-----|
| 1 | **IMP-001** (DOB Buttons) | Quick win, better UX at Q3 | <1 day |
| 2 | **IMP-004** (Religion Expectation) | Sensitive question needs framing | <1 day |
| 3 | **IMP-003** (NRI Location) | Better NRI experience (key market) | 1 day |
| 4 | **IMP-002** (Body/Complexion) | More honest answers (better matching) | 1 day |

**Total:** 3-4 days (Week 2 complete)

---

## 🎯 Recommended Month 1 Focus

**Weeks 3-4:**
- **FEAT-004** (Language Selection) — 11 Indian languages, TAM expansion (3-5 days)
- **IMP-005** (Cultural Terminology) — Competitor audit, fix sect/caste labels (2 days)
- **Buffer** — Testing, bug fixes, polish (2-3 days)

**By end of Month 1:**
- Entry flow ✅ (proxy + resume)
- Warm conversational tone ✅
- Automated tests ✅
- All P1 improvements ✅
- Language selection ✅ (11 languages)
- Ready for soft launch (friends/family)

---

## 🗺️ Long-Term Roadmap

**Month 2:**
- **FEAT-007** Phase 1-2 (Phone identity + session sync)
- Soft launch to 50-100 users (Telegram only)
- Iterate based on feedback

**Month 3:**
- **FEAT-007** Phase 3 (WhatsApp integration)
- Matching algorithm v1
- Scale to 500 users

**Month 4:**
- **FEAT-007** Phase 4 (Web form)
- Public launch (web landing page + Telegram + WhatsApp)
- Distribution experiments

---

## 🚦 Status Summary

**Green (Ready to ship):**
- All infrastructure ✅ (Fly, Supabase, bot code)
- All critical bugs fixed ✅ (7 bugs resolved in 48h)
- Loop detection ✅ (prevents infinite loops)
- Section transitions ✅ (reduces perceived infinite loop)

**Yellow (In progress):**
- Entry flow design (FEAT-006) — needs implementation
- Conversational warmth (IMP-006) — needs copy + integration
- Multi-channel architecture (FEAT-007) — design done, needs implementation

**Red (Blockers):**
- None currently

---

## 📝 Notes

1. **FEAT-003 superseded by FEAT-006** — Consent handling is part of larger entry flow redesign
2. **BUG-006 detection shipped, root cause pending** — Loop detection catches issue, but underlying Q26 skip logic bug still needs diagnosis (waiting for N's test path)
3. **Multi-channel (FEAT-007) is P2** — Not urgent, but critical for distribution (WhatsApp + web form). 4-week phased rollout.
4. **Testing infrastructure (FEAT-005) recommended before big refactors** — Prevents regressions, enables confident iteration

---

**Last Updated:** 2026-02-22 12:20 GST  
**Next Review:** After FEAT-006 ships (entry flow)
