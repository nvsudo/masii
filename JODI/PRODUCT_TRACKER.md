# JODI — Product Tracker

**Linear-style issue tracking** — Features, Improvements, Bugs

**Last Updated:** 2026-02-21 (Initial tracker created)

---

## 🚨 P0 — Critical (Ship This Week)

### [FEAT-006] Entry Flow: Self vs Proxy + Existing User Check
- **Type:** Feature
- **Status:** Backlog
- **Priority:** P0
- **Created:** 2026-02-22 11:10 GST
- **Owner:** Unassigned
- **User Request:** "At the top of the flow: is this for yourself or someone else? Existing user or new user? If existing, enter mobile number (better word this). Start with what we don't have already (state-aware flow)."
- **Description:** Add gating questions at the very beginning (before Q1 gender) to handle proxy submissions and returning users.
- **Flow Design:**
  1. **First Screen:** "Are you filling this for yourself or someone else?"
     - Options: [Myself] [Family member / Friend]
  2. **IF Proxy selected:**
     - "Who are you filling this for?" → [Better wording needed: "candidate", "person", "individual"?]
     - "How are you connected to them?" → [Parent / Sibling / Friend / Relative / Matchmaker]
     - "Do you have their consent to create this profile?" → [Yes, they know / I'll get consent later / No consent yet]
     - IF no consent → Show disclaimer: "You can fill the form, but we won't activate matching until they consent."
  3. **Second Screen (all users):** "Have you started a profile with us before?"
     - Options: [New user] [Returning user]
  4. **IF Returning user:**
     - "Please enter your mobile number" → Validate against `users.phone`
     - IF found → Load existing `answers` from session/DB, resume from last unanswered question
     - IF not found → "We couldn't find a profile with that number. Let's start fresh." → Proceed as new user
  5. **THEN:** Proceed to Q1 (Gender)
- **State-Aware Flow Logic:**
  - Load `session.answers` from DB (by telegram_id or phone lookup)
  - Skip questions where `answers[field]` already exists
  - Display progress: "You're 45% complete. Let's pick up where you left off."
  - Allow users to update previous answers: "Want to change any previous answers first?" → Show summary with edit buttons
- **Database Changes:**
  - Add `is_proxy` BOOLEAN to `users` table
  - Add `proxy_relationship` VARCHAR(50) (self/parent/sibling/friend/relative/matchmaker)
  - Add `consent_obtained` BOOLEAN (default FALSE)
  - Add `phone` VARCHAR(20) UNIQUE (for returning user lookup)
  - Add `onboarding_resumed` BOOLEAN (track if they're resuming vs fresh start)
- **UX Considerations:**
  - Proxy users see "You're filling this for [Name]" reminder throughout
  - Returning users see "Last updated: Feb 21, 2026" on resume
  - State-aware: "We already have your age and location. Moving to family questions..."
- **Edge Cases:**
  - Proxy with consent later → Send consent request message to candidate's phone
  - Returning user changes answers → Update DB, recalculate tier completion
  - Multiple devices (Telegram + web) → Sync state across platforms
- **Deliverables:**
  1. Entry flow UI (2 new screens before Q1)
  2. Proxy relationship capture + consent tracking
  3. Phone-based user lookup (returning users)
  4. State-aware question skipping (skip already-answered)
  5. Resume flow UX (progress indicator, edit previous answers)
  6. DB schema updates (4 new columns)
- **Impact:** Reduces dropoff (returning users don't start over), enables proxy submissions (parents/siblings), improves UX (transparent progress)

### [IMP-006] Conversational Warmth & Empathy
- **Type:** Improvement
- **Status:** Backlog
- **Priority:** P1
- **Created:** 2026-02-22 11:10 GST
- **Owner:** Unassigned
- **User Feedback:** "Conversationally, needs to get warmer. The tree route sometimes goes in a loop as well."
- **Description:** Bot feels transactional, not warm or human. Reads like a form, not a conversation. Lacks personality, empathy, reassurance.
- **Current Issues:**
  - No acknowledgment of answers ("Got it", "Thanks", "That helps")
  - No empathy for sensitive questions (disability, divorce, financial status)
  - No personality or humor
  - No encouragement or progress celebration
- **Proposed Changes:**
  1. **Acknowledgment responses** after sensitive/personal questions:
     - After Q5 (children from previous): "Thanks for sharing that with me."
     - After Q9 (disability): "I appreciate you being open about this."
     - After Q33-Q37 (financial): "Thanks. This stays private — only shared with serious matches after your approval."
     - After Q72 (dealbreakers): "Good to know what matters most to you."
  2. **Progress encouragement** at milestones:
     - 25% complete: "You're doing great! 25% done."
     - 50% complete: "Halfway there! This is going well."
     - 75% complete: "Almost done! Just a few more questions."
  3. **Empathy for difficult questions:**
     - Before financial section: "Next few questions are about finances. I know this can feel intrusive, but it helps us find matches who are in a similar life stage. You can skip any question."
     - Before dealbreakers: "Everyone has non-negotiables. Let's talk about yours — no judgment."
  4. **Humor/lightness where appropriate:**
     - After Q53 (weekends): "Everyone needs downtime 😊"
     - After Q54 (pets): "🐶 or 🐱? Or both?"
  5. **Personality in section transitions:**
     - Not: "Section 4 of 9"
     - Instead: "Great! Let's talk about family next. Don't worry, we're not asking for dowry 😄"
- **Implementation:**
  - Add `response_template` field to questions in `config.py`
  - Modify `_handle_question_answer()` to send acknowledgment after saving answer
  - Add progress milestone messages (25%, 50%, 75%)
  - Update section transitions with warmer tone
- **Tone Guide:**
  - Warm, friendly, slightly playful
  - Empathetic for sensitive topics
  - Encouraging, not pushy
  - Indian cultural context (diaspora-aware, family-oriented)
- **Impact:** Builds trust, reduces perceived interrogation, improves completion rate

### [FEAT-003] Consent Handling for Proxy Submissions
- **Type:** Feature
- **Status:** Backlog
- **Priority:** P0
- **Created:** 2026-02-21
- **Owner:** Unassigned
- **Description:** First question flow needs consent gate for family/friend submissions. Allows profile creation but blocks matching until consent obtained.
- **Flow:**
  1. "Are you here for yourself or family member?"
  2. IF family/friend → "How are you connected to this person?"
  3. "Do you have consent from them?"
  4. IF no consent → Allow form fill BUT matching activates only post-consent
  5. THEN gender question (male/female)
- **Use Case:** Parent filling for child, sibling helping sibling, friend recommending friend
- **Impact:** Trust, compliance, prevents unauthorized profiles
- **Deliverables:**
  - Consent flag in database (has_consent boolean)
  - Proxy relationship field (self/parent/sibling/friend/other)
  - Matching gate (skip if has_consent=false)
  - Consent collection flow (post-profile for proxy submissions)
- **Note:** Superseded by FEAT-006 (more comprehensive entry flow design)

---

## 🔥 P1 — High (Ship This Sprint)

### [IMP-005] Sect/Denomination (Q21) - Cultural Terminology Review
- **Type:** Improvement
- **Status:** Backlog
- **Priority:** P1
- **Created:** 2026-02-21 22:31 GST
- **Owner:** Unassigned
- **User Feedback:** "Vaishnavite — English names for Indian culture. We need to do better at this drill down."
- **Description:** Q21 sect/denomination options use English transliterations that feel academic/foreign for an Indian matchmaking platform. Need culturally authentic terminology that resonates with the target audience.
- **Current Options (Hindu):**
  - Shaivite, Vaishnavite, Arya Samaj, Smartha, None, Prefer not to say
- **Issues:**
  - "Vaishnavite" instead of "Vaishnava" or native script
  - Too academic/formal for conversational matchmaking context
  - Doesn't reflect how users actually describe their sect
- **Proposed Approach:**
  1. Research how users self-identify in Indian matchmaking (Shaadi.com, Jeevansathi terminology)
  2. Test bilingual options: "Vaishnava (वैष्णव)" or native script with English fallback
  3. Consider regional variations (North vs South India terminology)
  4. Add brief explanations for less common sects (e.g., "Smartha (follows Adi Shankaracharya tradition)")
- **Applies to all religions:** Muslim (Sunni/Shia), Sikh (Amritdhari), Christian (Catholic), Jain (Digambar/Shwetambar)
- **Ties to:** FEAT-004 (Language Selection) — interim fix before full localization
- **Impact:** Cultural authenticity, user trust, better self-identification accuracy
- **Deliverables:**
  - Competitor terminology audit (top 3 Indian matchmaking platforms)
  - Revised sect options for all 5 religions (Hindu, Muslim, Christian, Sikh, Jain)
  - A/B test: English vs bilingual vs native script (if language selection implemented)

### [IMP-004] Partner Religion (Q20) - Needs Expectation Setting
- **Type:** Improvement
- **Status:** Backlog
- **Priority:** P1
- **Created:** 2026-02-21 22:10 GST
- **Owner:** Unassigned
- **Description:** Q20 (partner religion preference) is sensitive territory — needs conversational buffer/expectation setting before asking
- **Current Issue:** Bot jumps straight into "What religion does your partner need to be?" after Q19 (your religious practice)
- **Why Sensitive:**
  - Partner religion preference is politically/socially charged
  - Can feel judgmental without context
  - Needs framing about why we ask (better matches, not discrimination)
- **Proposed Solution:**
  - Add transition message between Q19 and Q20
  - Example: "Quick heads up — the next few questions are about what you're looking for in a partner. Some might feel personal, but they help us understand compatibility. You can always skip or say 'flexible' if you prefer."
  - OR: Build into intro messages (Section C transition: "Religion & Culture Compatibility")
- **Alternative:** Skip Q20 entirely, infer from user's own religion + signals
- **Impact:** User trust, reduces friction at sensitive questions

### [IMP-003] Location Questions: Hierarchical NRI Drill-Down + Partner Location Logic
- **Type:** Improvement
- **Status:** Backlog
- **Priority:** P1
- **Created:** 2026-02-21
- **Owner:** Unassigned
- **Description:** Fix location questions (Q11-17) for better NRI experience and clearer partner location preferences.

**Issue 1: NRI Location Needs Hierarchical Drill-Down**
- **Current:** Single-level country dropdown (messy for NRIs)
- **Proposed Flow:**
  1. "Where are you based?" → [USA, UK, EU, AU, Singapore, UAE, Others]
  2. **IF EU selected** → Show top 7 EU countries + Others
     - Germany, France, Netherlands, Spain, Italy, Switzerland, Belgium, Others
  3. **IF Others selected** → Show top 7 global + text input
     - Canada, New Zealand, Middle East (non-UAE), South Africa, etc. + "Type your country"
  4. **Critical:** India should NOT be an option (they're NRI by definition)
- **Why:** Cleaner UX, faster selection for common NRI destinations

**Issue 2: Partner Location Preference Logic Wrong**
- **Current Q16:** "Open to relocating?" (doesn't fit the question flow)
- **Proposed:** "Does your partner need to be in your city as of now?"
  - Options: [Same city, Same state, Same country, Open (to anywhere)]
- **Why:** 
  - "Open to relocating" is about YOU moving, not partner location preference
  - "Same city/state/country/open" is clearer preference hierarchy
  - Matches how people actually think about location compatibility

**Implementation:**
- Q11: Hierarchical country selection (2-3 step drill-down)
- Q16: Replace with clearer partner location preference options
- Both questions need conditional logic based on first selection

- **Impact:** Better NRI onboarding experience, clearer location matching logic

### [IMP-002] Body Type & Complexion: Softer Questions + Paired Preferences
- **Type:** Improvement
- **Status:** Backlog
- **Priority:** P1
- **Created:** 2026-02-21
- **Owner:** Unassigned
- **Description:** Rephrase body type (Q7) and complexion (Q8) questions to be less direct. Current wording ("Body type: Slim/Average/Athletic/Heavy") won't get honest answers — no one will select "heavy."
- **Current Issues:**
  - Q7 (Body Type): Too direct, judgmental options ("Heavy")
  - Q8 (Complexion): Too direct, sensitive topic (skin tone in Indian culture)
  - Missing immediate partner preference pairing
  - Missing red flag capture
- **Proposed Approach:**
  - **Option 1:** Softer question framing
    - Body type: "How would you describe your build?" or "Your fitness routine?"
    - Complexion: Emoji-based or indirect ("Skin tone closest to..." with neutral options)
  - **Option 2:** Supplement with lifestyle question
    - "How often do you work out?" (Never/Occasionally/Regularly/Athlete)
    - Infer body type from lifestyle + other signals
  - **Option 3:** Visual/emoji approach
    - Show emoji figures or neutral silhouettes instead of text labels
- **Critical Addition: Paired Preference + Red Flags**
  - **Immediately after** user answers their own body type/complexion
  - Ask: "What do you prefer in a partner?" (same categories)
  - Ask: "Any dealbreakers?" (e.g., "I prefer athletic but heavy is a red flag")
  - This creates mini-sections: YOUR trait → YOUR preference → YOUR dealbreakers
- **Example Flow (Body Type):**
  1. "How would you describe your fitness level?" → [Not active / Occasionally active / Regularly active / Very athletic]
  2. "What fitness level would you prefer in a partner?" → [Same options + "No preference"]
  3. "Any fitness dealbreakers?" → [Optional: select dealbreakers or "No dealbreakers"]
- **Impact:** 
  - More honest self-reporting (less judgmental framing)
  - Captures preferences + dealbreakers at point of context (user just thought about it)
  - Better matching data (paired preferences are clearer)
- **Applies to both:**
  - Q7 (Body Type) + partner preference + dealbreakers
  - Q8 (Complexion) + partner preference + dealbreakers

### [IMP-001] Date of Birth: Two-Step Button Selection
- **Type:** Improvement
- **Status:** Backlog
- **Priority:** P1
- **Created:** 2026-02-21
- **Owner:** Unassigned
- **Description:** Simplify DOB collection to two-step button selection instead of text input (DD/MM/YYYY).
- **Current Issue:** Q3 asks for full DOB as text input. Error-prone (typos, wrong format), requires validation.
- **Proposed Flow:**
  - **Step 1:** "What year were you born?" → Button grid (1980-2006, ~27 options)
  - **Step 2:** "Which month?" → Button grid (Jan-Dec, 12 options)
  - **Day:** Skip for now (can collect later or users exchange directly)
- **Rationale:**
  - Year + Month gives accurate age for matching
  - Day not critical for compatibility (optional field for later)
  - Button taps > text input (faster, zero errors, better UX)
- **Impact:** Reduce friction at Q3, improve completion rate
- **Implementation:**
  - Update Q3 config from `text_input` to two separate `single_select` questions
  - Calculate age from year + month (assume day = 15 for age calculation)
  - Store: `birth_year` INT, `birth_month` INT, `date_of_birth` DATE (constructed as YYYY-MM-15)

### [FEAT-004] Language Selection & Localization
- **Type:** Feature
- **Status:** Backlog
- **Priority:** P1
- **Created:** 2026-02-21
- **Owner:** Unassigned
- **Description:** Upfront language selection for non-English users. Tamil-only users (and other regional languages) need the bot to speak their language from the start.
- **Current Issue:** Bot assumes English. No language selection at beginning. Emojis may not be culturally appropriate across all languages.
- **Proposed Flow:**
  - Very first question (before gender): "Which language would you prefer? / எந்த மொழியை விரும்புகிறீர்கள்?"
  - Options: English, हिन्दी, தமிழ், తెలుగు, ಕನ್ನಡ, മലയാളം, ગુજરાતી, मराठी, বাংলা, ਪੰਜਾਬੀ, اردو
  - All subsequent questions/messages in selected language
  - Store in users table: `preferred_language` VARCHAR(10)
- **Scope:**
  - Phase 1: Language selection + translate all 77 questions + intro messages (11 languages)
  - Phase 2: Translate bot responses, error messages, confirmations
  - Phase 3: Emoji localization (some cultures don't use emojis as liberally)
- **Impact:** TAM expansion (India has 200M+ non-English speakers in matchmaking market)
- **Deliverables:**
  - Language selection screen (Q0)
  - Translation files for all 77 questions + intro messages (11 languages)
  - Update config.py to support multi-language question text
  - Update bot response generator to use selected language
  - Database field: `preferred_language`
- **Translation Strategy:**
  - Use Google Translate API for initial translations
  - Human review/refinement for cultural nuance (especially intro messages)
  - A/B test emoji usage by language (some languages may need less emoji-heavy copy)

### [FEAT-005] Automated Conditional Logic Tests
- **Type:** Feature
- **Status:** Backlog
- **Priority:** P1
- **Created:** 2026-02-22 11:10 GST
- **Owner:** Unassigned
- **User Request:** "We need tests to simulate the conditional trees. For example — languages you speak has come a few times now in my testing in a loop."
- **Description:** No automated tests to catch conditional logic bugs (loops, skip logic errors, duplicate questions). Current `validate_conditional_logic()` function exists in `conditional_logic.py` but never runs automatically.
- **Problem:**
  - BUG-006 (Q26 loop) discovered manually during testing
  - No way to catch regressions when modifying skip logic
  - Conditional branches untested (Hindu vs Muslim vs NRI paths)
  - Deploy blindly, hope nothing breaks
- **Proposed Solution:**
  1. **Test Suite with 8-10 User Personas:**
     - Hindu, never married, India (baseline)
     - Muslim, never married, India
     - NRI Hindu, never married, USA
     - Divorced Hindu with kids, India
     - Jain, OCI, UK
     - Sikh, never married, Canada
     - Buddhist, India
     - Christian, never married, India
  2. **Simulate Full Flow for Each Persona:**
     - Start at Q1, follow conditional logic through Q77
     - Track: asked questions, skipped questions, section jumps
     - Assert: no duplicate questions, correct question count, right sections skipped
  3. **Assertions:**
     - `no_duplicate_questions(asked_questions)` — fail if any question asked twice
     - `correct_question_count(persona)` — Hindu India = 73 questions, Muslim India = 69, etc.
     - `correct_skip_logic(persona)` — Q22-Q24 skipped for Muslims, Q34 skipped for Indians, etc.
     - `section_jumps_correct(persona)` — Q21→Q25 jump for Muslims, Q24→Q28 for non-Hindus
  4. **Run on Every Deploy:**
     - Pre-deploy script: `python -m pytest tests/test_conditional_logic.py`
     - CI/CD integration (GitHub Actions)
     - Fail deployment if tests fail
- **Existing Foundation:**
  - `conditional_logic.py` already has `validate_conditional_logic()` function
  - `TEST_PATHS` already defined (4 personas)
  - Just need to: expand personas, convert to pytest, integrate with deploy
- **Files to Create:**
  - `/ventures/jodi/tests/test_conditional_logic.py`
  - `/ventures/jodi/tests/test_personas.json` (8-10 user paths)
  - `/ventures/jodi/.github/workflows/test.yml` (CI/CD)
  - `/ventures/jodi/scripts/run_tests.sh` (pre-deploy script)
- **Deliverables:**
  1. Pytest test suite with 8-10 persona paths
  2. Assertions: no duplicates, correct counts, right skips
  3. Pre-deploy script integration
  4. CI/CD GitHub Actions workflow
  5. Documentation: how to add new test personas
- **Impact:**
  - Catch loops (BUG-006) before users see them
  - Prevent regressions when modifying skip logic
  - Confidence to refactor conditional logic
  - Faster iteration (no manual testing)
- **ETA:** 1 day (build test suite + CI/CD integration)

---

## 📊 P2 — Medium (This Month)

### [FEAT-007] Multi-Channel Identity + State Management
- **Type:** Feature
- **Status:** Backlog
- **Priority:** P2
- **Created:** 2026-02-22 12:15 GST
- **Owner:** Unassigned
- **User Request:** "As we build this across WhatsApp, web forms, and Telegram — we need a way to link it to a user and be state/progress aware."
- **Description:** Enable unified user state across Telegram, WhatsApp, and web form. Phone-based identity allows seamless resume from any channel.
- **Core Architecture:**
  1. **Identity Layer:** `user_channels` table maps channel IDs → user_id
     - telegram_id: 7207658858 → user_id: abc123
     - whatsapp_phone: +971585408825 → user_id: abc123
     - session_token: xyz789 → user_id: abc123
  2. **State Layer:** Two tables
     - `sessions` (ephemeral, per-channel) — Fast writes, loop tracking, temp state
     - `users` (canonical, permanent) — Source of truth, profile, progress
  3. **Audit Layer:** `conversation_logs` tracks all interactions with channel metadata
- **User Flow Example:**
  - Day 1: User starts on Telegram, phone=+971585408825, completes 45%
  - Day 2: User switches to WhatsApp (same phone), system finds user_id=abc123
  - Bot: "Welcome back! You're 45% complete. Let's continue from Q27..."
  - Day 3: User opens web form, same resume experience
- **Database Changes:**
  - New tables: `user_channels`, `sessions`
  - Updated tables: `users` (add phone, email, preferred_channel)
  - Helper functions: `get_or_create_user_by_phone()`, `link_channel_to_user()`, `get_user_id_from_channel()`
- **Implementation Phases:**
  1. **Phase 1 (Week 1):** Phone-based identity — collect phone at start, OTP verification, create user_channels
  2. **Phase 2 (Week 2):** Session state sync — bot handlers use user_id, write to sessions + users, resume logic
  3. **Phase 3 (Week 3):** WhatsApp integration — webhook receiver, phone-based lookup, same bot logic
  4. **Phase 4 (Week 4):** Web form — Next.js form with 77 questions, magic link auth, save to same users table
- **Key Benefits:**
  - No duplicate profiles (phone ensures uniqueness)
  - Seamless resume across devices/channels
  - Better conversion (users don't restart)
  - Audit trail (see which channel users prefer)
  - Future-proof (easy to add SMS, voice, etc.)
- **Files:**
  - `schema/12_multi_channel_identity.sql` — DB schema + helper functions
  - `MULTI_CHANNEL_ARCHITECTURE.md` — Full design doc with examples
- **Impact:** Critical for multi-channel distribution (WhatsApp + web landing pages), reduces dropoffs (resume from any channel), enables future channels
- **ETA:** 4 weeks (phased rollout)
- **Dependencies:** FEAT-006 (entry flow) should ship first (phone collection overlaps)

---

## 📝 P3 — Nice to Have (Backlog)

*No P3 items currently*

---

## ✅ Done (Shipped)

### [IMP-007] Section Transition Messages (9 Transitions)
- **Type:** Improvement
- **Status:** Done ✅
- **Shipped:** 2026-02-22 12:10 GST
- **Owner:** A
- **Description:** Added buffer messages between question sections to reduce perceived infinite loop and improve transparency.
- **User Feedback:** "As we transition from one category to others, there is no transparency felt — like 'now I will move on to ask you some questions about your family...' Without conversations and categories, it feels like an infinite loop and we will have drop offs."
- **Solution:**
  - Created `_send_section_transition()` method that auto-detects section changes
  - Uses existing `SECTION_TRANSITIONS` dict from config.py (already had the right tone)
  - Sends warm transition message before first question of each new section
  - Added progress % indicator at family and lifestyle transitions (📊 X% complete)
  - 9 transitions implemented: after_identity, after_location, after_religion, after_education, after_financial, after_family, after_lifestyle, after_partner_prefs, after_values
- **Tone matched:** Short, reassuring, encouraging (matches intro messages)
- **Files Changed:** `bot/onboarding_handler.py` (+41 lines: new method + integration)
- **Deployment:** Commit 1eecb15, deployed to Fly staging (deployment-01KJ268WC036CXVPMW5X10GBW3)
- **Time to fix:** 25 minutes
- **Impact:** Users now see clear section breaks, understand flow structure, feel progress

### [BUG-006] Question Loop Detection — Universal Loop Prevention
- **Type:** Bug
- **Status:** Done ✅
- **Shipped:** 2026-02-22 12:10 GST
- **Owner:** A
- **Description:** Q26 (languages you speak) appearing multiple times in same user flow. Implemented universal loop detection to catch any duplicate question.
- **User Report:** "Languages you speak has come a few times now in my testing in a loop"
- **Solution:**
  - Added `asked_questions: []` array to session state (tracks all asked questions)
  - Before asking any question: check if `question_num in asked_questions`
  - If duplicate detected:
    - Log full error context (user path, answers, current question)
    - Skip to next question automatically
    - Alert via logger (can wire to Telegram later)
  - If infinite loop detected (Q→Q): bail out with user message "Something went wrong..."
  - After asking question: append to `asked_questions` array
- **Testing Strategy:**
  - Loop detection logs full user path when triggered (enables root cause diagnosis)
  - Catches ANY loop, not just Q26
  - N can now test and we'll see exactly which path triggers the loop in logs
- **Files Changed:** `bot/onboarding_handler.py` (+31 lines: loop detection logic)
- **Deployment:** Commit 1eecb15 (same commit as IMP-007), deployed to Fly staging
- **Time to fix:** 20 minutes
- **Impact:** No more infinite loops, users never get stuck, full diagnostic logging for root cause analysis
- **Next:** Need N's test path to find root cause of Q26 loop (detection catches it, but haven't fixed the underlying skip logic bug yet)

### [BUG-005] Caste/Community (Q22) - No Options Shown
- **Type:** Bug
- **Status:** Done ✅
- **Shipped:** 2026-02-21 22:38 GST
- **Owner:** A
- **Description:** Q22 (caste/community) showed no button options, displayed "tap on option above", user stuck
- **Root Cause:** Same as BUG-004 — `get_conditional_options()` missing Q22 handler. Q22 has `options: "castes_by_religion"` (dynamic), but function only handled Q21.
- **Solution:**
  - Added Q22 handler to `get_conditional_options()` in `conditional_logic.py`
  - Returns caste/community options based on religion:
    - **Hindu:** Brahmin, Kshatriya/Rajput, Vaishya/Baniya, Kayastha, Maratha, Reddy, Nair, Ezhava, SC, ST, OBC, Other, Prefer not to say (13 options)
    - **Jain:** Digambar, Shwetambar, Agarwal, Oswal, Porwal, Other, Prefer not to say (7 options)
    - **Sikh:** Jat, Khatri, Arora, Ramgarhia, Saini, SC, Other, Prefer not to say (8 options)
    - **Buddhist:** SC, ST, OBC, Other, Prefer not to say (5 options)
    - **Others** (Muslim, Christian, etc.): return None (caste doesn't apply, question skipped)
- **Recursive Check:** Confirmed only 2 questions use conditional options in entire flow:
  - Q21 (sects_by_religion) — fixed in BUG-004
  - Q22 (castes_by_religion) — fixed in BUG-005
  - All other dynamic options ("countries", "states_india") already handled by `self.dynamic_options` dict
- **Files Changed:** `bot/conditional_logic.py` (56 lines added)
- **Deployment:** Commit 7a5144b, deploying to Fly staging
- **Time to fix:** 15 minutes (diagnosis + recursive check + code + deploy)
- **Impact:** Unblocks all users at Q21→Q22 transition
- **Note:** Caste options will also need cultural terminology review (same as IMP-005 for sects)

### [BUG-004] Sect/Denomination (Q21) - No Options Shown
- **Type:** Bug
- **Status:** Done ✅
- **Shipped:** 2026-02-21 22:30 GST
- **Owner:** A
- **Description:** Q21 (sect/denomination) showed no button options, displayed "tap on option above", user stuck
- **Root Cause:** `onboarding_handler.py` never called `get_conditional_options()` from `conditional_logic.py`. Q21 has `options: "sects_by_religion"` (dynamic), but handler only checked `self.dynamic_options` dict (which only had "countries" and "states_india"). The conditional logic function existed and worked correctly, but was never invoked.
- **Solution:**
  - Imported `get_conditional_options` in `onboarding_handler.py`
  - Modified `_ask_single_select()` to check conditional options first before falling back to config/dynamic options
  - Q21 now correctly shows religion-based sect/denomination options (Hindu→Shaivite/Vaishnavite/etc, Muslim→Sunni/Shia/etc)
- **Files Changed:** `bot/onboarding_handler.py` (12 lines: +6 new, -6 old)
- **Deployment:** Commit 882aa8e, pushed to GitHub, deploying to Fly staging
- **Time to fix:** 20 minutes (diagnosis + code fix + deploy)
- **Impact:** Unblocks all users at Q20→Q21 transition

### [BUG-003] Error 0 at Q16 (Tier Boundary Bug)
- **Type:** Bug
- **Status:** Done ✅
- **Shipped:** 2026-02-21 22:08 GST
- **Owner:** A
- **Description:** Bot crashed at Q16 (partner location preference) with cryptic "error 0" at tier boundary
- **Root Cause:** Dictionary indexing error when transitioning from `users` table to `preferences` table
  - Q1-15 save to `users` table ✅
  - **Q16 is FIRST question saving to `preferences` table** ❌
  - Code used `result[0]['id']` treating fetchone() result as a list
  - Actual: `result` is a RealDictRow (dict-like): `{'id': 123, 'telegram_id': 456}`
  - Error: `KeyError: 0` logged as "error 0"
- **Solution:**
  - Fixed `_save_to_preferences_table()`: Changed `result[0]['id']` → `result['id']`
  - **Proactively fixed `_save_to_jsonb_table()`:** Same bug + also used `telegram_id` instead of `user_id` for FK lookups
  - Both methods now properly convert telegram_id → user_id before INSERT/UPDATE
- **Files Changed:** `/ventures/jodi/bot/db_adapter.py`
- **Why this question:** Q16 is tier boundary — first transition from `users` to `preferences` table
- **Additional fix:** Enhanced error logging with full tracebacks in `bot.py`
- **Impact:** All table transitions now work correctly (users → preferences, users → signals)

### [BUG-002] User Preferences Save Error
- **Type:** Bug
- **Status:** Done ✅
- **Shipped:** 2026-02-21 20:50 GST
- **Owner:** A
- **Description:** Bot crashed when saving to `user_preferences` table (Q16+). Error: "column 'preferences' of relation 'user_preferences' does not exist"
- **Root Cause:** Bot code assumed `user_preferences` has JSONB column `preferences`, but actual schema has individual columns (`partner_location_pref`, `pref_age_range`, etc.)
- **Affected Questions:** Q16, Q20, Q24, Q46, Q48, Q50, Q56-64, Q73-77 (20+ preference/dealbreaker questions)
- **Solution:** Added `_save_to_preferences_table()` method in `db_adapter.py` that:
  - Gets user_id from telegram_id
  - Ensures row exists in user_preferences
  - Saves to actual column names (not JSONB)
  - Handles all 20 preference field mappings
- **Files Changed:** `/ventures/jodi/bot/db_adapter.py`
- **Deployment:** New Docker image deployed to Fly.io (deployment-01KJ0J5GYE41PRKBBGPEZV4W3J)
- **Actual time:** ~10 minutes (identify issue → code fix → deploy)

### [BUG-001] Schema Mismatch: Bot vs Database
- **Type:** Bug
- **Status:** Done ✅
- **Shipped:** 2026-02-21 20:13 GST
- **Owner:** A
- **Description:** **MASSIVE schema mismatch** between bot code (77-field MVP) and database schema. Bot expects 53 fields in `users` table, schema only had 11 matching + 7 name mismatches + **35 missing**. Preferences table: 0 exact matches, 6 name mismatches, 14 missing.
- **Root cause:** Trigger function used `NEW.user_id` but column doesn't exist (correct: `NEW.id`).
- **Error:**
  ```
  Database query failed: record "new" has no field "user_id"
  CONTEXT: SQL statement "SELECT calculate_weighted_completeness(NEW.user_id)"
  PL/pgSQL function trigger_recalculate_completeness() line 3 at PERFORM
  ```
- **Impact:** Bot crashed after Q1 (gender). **Blocked all onboarding.**
- **Solution:**
  - Created migration `/schema/08_fix_schema_to_match_bot.sql` (14KB)
  - Fixed trigger: `NEW.user_id` → `NEW.id`
  - Added 35 missing columns to `users` table
  - Added 14 missing columns to `user_preferences` table
  - Renamed 7 columns in `users` (marital_history→marital_status, country→country_current, etc.)
  - Renamed 2 columns in `user_preferences` (education_minimum→pref_education_min, etc.)
  - Updated indexes, triggers, helper functions
  - Applied to JODI Supabase (herqdldjaxmfusjjpwdg)
  - Restarted bot on Fly.io
- **Analysis:** See `/JODI/SCHEMA_VERIFICATION_REPORT.md` for full field-by-field comparison
- **Actual execution time:** 8 minutes (not 2 hours!)
- **Lesson:** Schema must stay in sync with bot code. Bot is source of truth.

### [FEAT-000] 100+ Data Point Framework
- **Type:** Feature
- **Status:** Done ✅
- **Shipped:** 2026-02-12
- **Owner:** A + Kavi
- **Description:** Comprehensive matchmaking data capture framework (100+ data points). Explicit vs Inferred (40/60 split), Hard filters (indexed columns) vs Signals (JSONB), 4-tier model (Basics → Ready → Deep Profile → Calibrated).
- **Deliverables:**
  - Data architecture spec (Matchmaking_Data_Capture_Framework_v1.docx)
  - Full schema design (11 tables: profiles, matches, user_preferences, user_signals, conversation_logs, photos, interactions, match_feedback, tier_progress, profile_readiness, users)
  - MVP activation rules (100% T1 + 70% T2 + 45% total + 2+ sessions)
- **Impact:** Competitive moat (60% AI-inferred data), quality-first matching (Keeper lesson: don't rush incomplete profiles)

### [FEAT-001] Supabase Database Schema
- **Type:** Feature
- **Status:** Done ✅
- **Shipped:** 2026-02-12
- **Owner:** Kavi
- **Description:** Full production schema deployed to Supabase (Project: herqdldjaxmfusjjpwdg, Region: AP South 1 Mumbai).
- **Deliverables:**
  - 11 tables deployed
  - Migrations 01-07 executed successfully
  - Missing fields added (first_name, last_name, full_name, alias)
  - Google Sheet for schema review: https://docs.google.com/spreadsheets/d/18nvSgfJ0yD_DDoNMhV8-0JvjP_DT0tbsPkOHDjclywA/edit
- **Impact:** Production-ready database, all 100+ data points covered

### [FEAT-002] Telegram Onboarding Sequence
- **Type:** Feature
- **Status:** Done ✅
- **Shipped:** 2026-02-12
- **Owner:** A
- **Description:** Complete 7-message intro (2-3 min) + 4-phase button-based onboarding (37 screens, 10-12 min total, 34-36 fields captured, $0 LLM cost). Soft, trust-building tone. Privacy reassurance. Photos-at-end philosophy.
- **Deliverables:**
  - Full sequence spec: /JODI/TELEGRAM_ONBOARDING_SEQUENCE.md
  - 7 intro messages (who we are, how we work, privacy, photos philosophy, emotional safety)
  - Phase 1: About You (10 screens, 11 fields)
  - Phase 2: Your Preferences (10 screens, 10 fields)
  - Phase 3: Family & Lifestyle (7 screens, 7 fields)
  - Phase 4: Photos & Final Steps (10 screens, 6-8 fields)
- **Trade-off:** Longer intro filters for serious users (deliberate choice)
- **Impact:** Zero LLM cost onboarding, complete profile capture, trust-building UX

---

## 📋 Status Legend

- **Backlog** — Not started
- **Todo** — Queued for work
- **In Progress** — Actively building
- **In Review** — Built, needs QA/approval
- **Done** — Shipped to production

---

## 🏷️ Type Legend

- **Feature** — New capability
- **Improvement** — Enhancement to existing capability
- **Bug** — Defect fix

---

## 🎯 Priority Legend

- **P0** — Critical (ship this week)
- **P1** — High (ship this sprint)
- **P2** — Medium (ship this month)
- **P3** — Nice to have (backlog)

---

## 📊 Metrics (As of 2026-02-22 12:20)

| Metric | Count |
|--------|-------|
| Total Items | 20 |
| Features | 8 |
| Improvements | 7 |
| Bugs | 6 |
| P0 (Critical) | 2 |
| P1 (High) | 7 |
| P2 (Medium) | 1 |
| P3 (Backlog) | 0 |
| Done | 10 |
| In Progress | 0 |
| Backlog | 10 |

---

## 🔄 Update Log

**2026-02-22 (12:20):** ✅ **BUG-006 + IMP-007 SHIPPED** — Both fixes deployed to staging (deployment-01KJ268WC036CXVPMW5X10GBW3). Loop detection now catches ANY duplicate question and logs full diagnostic path. Section transitions auto-send warm buffer messages between categories (9 transitions). Total time: 45 minutes. Also added **FEAT-007** (P2) — Multi-channel identity architecture (Telegram + WhatsApp + web form unified state, phone-based linking, 4-week phased rollout). Files: schema/12_multi_channel_identity.sql + MULTI_CHANNEL_ARCHITECTURE.md.

**2026-02-22 (11:15):** 🎯 **MAJOR TRACKER UPDATE** — Added 5 new high-priority items based on N's testing feedback:
- **FEAT-006** (P0): Entry flow redesign — "For yourself or someone else?" + existing user check + state-aware flow (skip already-answered questions)
- **BUG-006** (P0): Question loop detection — "Languages you speak" (Q26) appearing multiple times (need N's test path to reproduce)
- **IMP-007** (P0): Section transition messages — 9 transitions needed ("Now let's talk about your family...") to reduce perceived infinite loop and improve transparency
- **IMP-006** (P1): Conversational warmth & empathy — Bot feels transactional, needs acknowledgment responses, progress encouragement, personality
- **FEAT-005** (P1): Automated conditional logic tests — Build test suite with 8-10 personas to catch loops/regressions before deploy

Also created **CONDITIONAL_FLOW.md** — Visual Mermaid diagram of entire 77-question flow with all conditional branches, section jumps, and skip logic. N can review flow and vibe before approving changes.

**Key insights from N's feedback:**
1. **Infinite loop feeling** = Missing section transitions + actual loop bugs (Q26) + no warmth
2. **Dropoffs likely** = Users don't know where they are in the flow, feels endless
3. **State-aware flow critical** = Returning users shouldn't start over (huge UX win)
4. **Testing infrastructure missing** = Need automated tests to prevent regressions

**Next steps:** 
1. N to review CONDITIONAL_FLOW.md and confirm priorities
2. N to provide test path that triggers Q26 loop (need to reproduce)
3. Pick top 3 to fix this week (suggest: BUG-006 loop, IMP-007 transitions, FEAT-006 entry flow)

**2026-02-21 (22:38):** ✅ **BUG-005 FIXED** — Q22 caste/community conditional options now rendering. Same root cause as BUG-004 (missing handler in `get_conditional_options()`). Added Q22 handler with caste options for Hindu (13), Jain (7), Sikh (8), Buddhist (5). Recursive check confirmed only Q21+Q22 use conditional options. Deployed commit 7a5144b. 15-minute fix. **Note:** Caste options also need cultural terminology review (same as IMP-005).

**2026-02-21 (22:32):** Added IMP-005 (Sect/Denomination Cultural Terminology Review) — P1. User feedback: "Vaishnavite — English names for Indian culture. We need to do better." Q21 uses academic English transliterations (Vaishnavite, Shaivite) that feel foreign for Indian matchmaking context. Need culturally authentic terminology — research competitor platforms (Shaadi.com), test bilingual options ("Vaishnava (वैष्णव)"), consider regional variations. Applies to all religions (Hindu, Muslim, Sikh, Christian, Jain). Ties to FEAT-004 (language selection).

**2026-02-21 (22:30):** ✅ **BUG-004 FIXED** — Q21 conditional options now rendering. Root cause: `get_conditional_options()` function existed but was never called in handler. Fixed `_ask_single_select()` to check conditional options first. Deployed to staging (commit 882aa8e). 20-minute fix. Unblocks all users at Q20→Q21.

**2026-02-21 (22:12):** Added BUG-004 (Sect/Denomination Q21 - No Options Shown) — P1 blocker. After Q20 (religion), Q21 shows no buttons, says "tap option above", user stuck. Likely conditional logic issue (options based on religion not populating). Also added IMP-004 (Partner Religion Q20 - Needs Expectation Setting) — P1. Q20 asks partner religion preference without context, feels abrupt/judgmental. Needs transition message or sensitivity framing. **Committed + pushed bot fixes to git.**

**2026-02-21 (22:08):** ✅ **BUG-003 FIXED** — Tier boundary bug at Q16. Root cause: `result[0]['id']` treating dict as list (KeyError: 0 → "error 0"). Q16 is first question transitioning from `users` to `preferences` table. Fixed `_save_to_preferences_table()` + proactively fixed `_save_to_jsonb_table()` (had same bug + telegram_id/user_id mismatch). Enhanced error logging with full tracebacks. All table transitions now work.

**2026-02-21 (21:36):** Added BUG-003 (Error 0 at Q16) — **P0 CRITICAL**. Bot crashes at Q16 (partner location preference) with cryptic "error 0". Logs show bot answers callback successfully then hits error. Hypothesis: division by zero in tier completion calc or next question logic. Missing full traceback in logs. Blocks all users at Q16.

**2026-02-21 (20:50):** ✅ **BUG-002 FIXED** — Bot code bug saving to user_preferences table. Was trying to save to JSONB column "preferences" but schema has individual columns. Added `_save_to_preferences_table()` method with proper column mapping. Deployed to Fly.io. Bot can now proceed past Q16 (and all 20+ preference questions).

**2026-02-21 (20:42):** Added IMP-003 (Location Questions: Hierarchical NRI Drill-Down + Partner Location Logic) — P1. Two fixes: (1) NRI location needs 2-3 step drill-down (USA/UK/EU/AU/SG/UAE/Others → if EU show top 7 + Others → if Others show top 7 + text). India NOT an option (they're NRI by definition). (2) Partner location preference wrong — current "open to relocating" doesn't fit. Replace with "Does partner need to be in your city?" → [Same city / Same state / Same country / Open].

**2026-02-21 (20:37):** Added IMP-002 (Body Type & Complexion: Softer Questions + Paired Preferences) — P1. Rephrase Q7 (body type) and Q8 (complexion) to be less direct. Current: "Heavy" option won't get honest answers. Proposed: (a) softer framing ("fitness level" not "body type"), (b) emoji/visual approach, or (c) supplement with lifestyle questions. **Critical addition:** Immediately pair with partner preference + dealbreakers (e.g., "I prefer athletic but heavy is a red flag"). Creates mini-sections: YOUR trait → YOUR preference → YOUR dealbreakers.

**2026-02-21 (20:33):** Added IMP-001 (DOB: Two-Step Button Selection) — P1. Simplify Q3 from text input (DD/MM/YYYY) to two button taps: (1) Birth year grid (1980-2006), (2) Birth month grid (Jan-Dec). Skip day (not critical, can collect later). Rationale: buttons > text (faster, zero errors, better UX).

**2026-02-21 (20:30):** Added FEAT-004 (Language Selection & Localization) — P1. Tamil-only users (and other regional languages) need upfront language selection. Proposed: Q0 language picker → 11 Indian languages → full translation of 77 questions + intro messages. TAM expansion opportunity (200M+ non-English speakers in India matchmaking market).

**2026-02-21 (20:28):** ✅ **BUG-001 FULLY FIXED (3rd attempt)** — Migration 10 applied. Fixed JSONB lateral join syntax in `calculate_tier_completion` (column "key" does not exist error). Bot restarted. NOW actually ready for full test.

**2026-02-21 (20:22):** Migration 09 applied. Fixed `calculate_tier_completion` function (city→city_current, marital_history→marital_status, dietary_restrictions→diet). ⚠️ Found additional JSONB syntax error.

**2026-02-21 (20:13):** ✅ **BUG-001 SHIPPED** — Schema migration 08 complete! Fixed trigger (NEW.user_id→NEW.id), added 49 columns, renamed 9 columns, updated indexes/triggers/functions. Applied to Supabase, bot restarted. Execution time: 8 minutes. ⚠️ Found additional issue: calculate_tier_completion still referenced old column names.

**2026-02-21 (20:10):** **SCHEMA VERIFICATION COMPLETE** — BUG-001 updated with full analysis. Massive mismatch: 66% of `users` fields missing (35/53), 70% of `preferences` fields missing (14/20). Immediate fix: trigger uses `NEW.user_id` → change to `NEW.id`. Full report: `/JODI/SCHEMA_VERIFICATION_REPORT.md`. Migration required: 49 columns + 13 renames.

**2026-02-21 (19:47):** Added BUG-001 (Database Trigger Error on User Update) — **CRITICAL P0 BLOCKER**. Bot crashes after user selects gender. Trigger function `trigger_recalculate_completeness()` references `NEW.user_id` but column doesn't exist. Blocks all onboarding after Q1.

**2026-02-21 (Evening):** Added FEAT-003 (Consent Handling for Proxy Submissions) — P0. First question flow needs consent gate: self/family/friend → connection type → consent check → allow form fill but block matching until consent obtained.

**2026-02-21 (Afternoon):** Initial tracker created. Foundation work documented (100+ data framework, schema, onboarding sequence). Ready for user feedback tracking.

---

**How to Use This Document:**
1. Add new items with unique ID (FEAT-###, IMP-###, BUG-###)
2. Update Status as work progresses
3. Move completed items to "Done" section with ship date
4. Review priorities weekly
5. Archive Done items quarterly (keep last 90 days visible)
