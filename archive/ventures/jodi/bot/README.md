
# JODI Telegram Bot - Onboarding Flow Implementation

## Overview

This is the production-ready implementation of the JODI Telegram onboarding flow featuring:

- **77 structured questions** across 10 sections
- **Button-based UI** with zero LLM costs during intake
- **Conditional branching** - questions adapt based on answers
- **Multi-select support** for checkbox-style questions
- **Save & resume** - users can pause and continue later
- **Photo upload** with multi-photo support
- **Database-backed** session persistence via Supabase Postgres

## Architecture

```
bot.py                  - Main bot entry point, message routing
onboarding_handler.py   - Onboarding flow orchestration
conditional_logic.py    - Question branching and skip logic
validation.py           - Input validation (dates, heights, etc.)
db_adapter.py          - Database interface (Supabase Postgres)
config.py              - Data-driven question definitions
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
- `TELEGRAM_BOT_TOKEN` - Get from [@BotFather](https://t.me/botfather)
- `DATABASE_URL` - Supabase Postgres connection string

### 3. Database Schema

Ensure the following tables exist in your Supabase database:

- `users` - User profile data
- `user_preferences` - Partner preferences (JSONB)
- `user_signals` - Personality signals (JSONB)
- `conversation_state` - Session state persistence
- `user_photos` - Photo storage

Run migrations from `/ventures/jodi/schema/`:

```bash
cd ../schema
./00_run_migrations.sh
```

### 4. Run the Bot

```bash
python bot.py
```

## Flow Structure

### Phase 1: Intro (7 messages)
- Privacy & trust building
- How Jodi works
- Expectations setting
- Zero data collection

### Phase 2: Structured Questions (77 questions)

**Section A: Identity & Basics (Q1-Q9)**
- Gender, orientation, age, marital status
- Height, body type, complexion
- Disability status

**Section B: Location & Mobility (Q10-Q17)**
- Residency (India/NRI/OCI/Foreign)
- Current location, hometown
- Relocation willingness

**Section C: Religion & Culture (Q18-Q27)**
- Religion, practice level, sect
- Caste/community (conditional)
- Languages, mother tongue
- Manglik status (conditional)

**Section D: Education & Career (Q28-Q32)**
- Education level, institution tier
- Employment status, industry
- Career ambition

**Section E: Financial (Q33-Q37)** [PRIVATE]
- Income bracket, currency
- Net worth, property
- Financial dependents

**Section F: Family (Q38-Q44)**
- Family type, financial status
- Father's occupation
- Living with parents post-marriage
- Family involvement in search

**Section G: Lifestyle (Q45-Q55)**
- Diet, smoking, drinking
- Fitness, social style
- Weekends, pets, sleep schedule

**Section H: Partner Preferences (Q56-Q64)**
- Age range, height, complexion
- Education minimum, income range
- Marital history, children acceptance

**Section I: Values (Q65-Q72)**
- Relationship intent, children timeline
- Gender roles, financial management
- Political leaning, astrology
- Interfaith/intercaste openness

**Section J: Dealbreakers (Q73-Q77)**
- Divorced/widowed/children tolerance
- NRI acceptance
- Maximum age gap

### Phase 3: Photo Upload
- Minimum 1 photo required
- Option to add more

### Phase 4: Conversational Mode
- Transition to LLM-driven conversations
- Deep profile building

## Conditional Logic

Questions dynamically adapt:

| Condition | Questions Affected |
|-----------|-------------------|
| `marital_status == "Never married"` | Skip Q5 (existing children) |
| `residency_type == "Indian citizen (in India)"` | Skip Q11, show Q12 (state) |
| `residency_type != "Indian citizen (in India)"` | Show Q11 (country), skip Q12 |
| `residency_type == NRI/OCI` | Show Q17 (settling country) |
| `religion == Hindu/Jain/Sikh/Buddhist` | Show Q22-Q24 (caste), Q27 (manglik) |
| `religion == Muslim/Christian/etc.` | Skip caste questions |
| `children_intent == "Definitely not"` | Skip Q67 (children timeline) |

## Validation Rules

- **Date of birth**: DD/MM/YYYY, age 18-80
- **Height**: 140-220 cm (accepts cm or feet'inches)
- **Email**: Basic format validation
- **Phone**: 7-15 digits

## Testing

Run conditional logic tests:

```bash
python conditional_logic.py
```

This validates the branching logic against 4 user paths:
1. Hindu, never married, India
2. Muslim, never married, India
3. NRI Hindu, never married, abroad
4. Divorced Hindu, has children, India

## Database Schema Mapping

| Question | Field | Table | Type |
|----------|-------|-------|------|
| Q1 | gender_identity | users | VARCHAR |
| Q2 | looking_for_gender | users | VARCHAR |
| Q3 | date_of_birth | users | DATE |
| Q20 | partner_religion_pref | user_preferences | JSONB |
| Q32 | career_ambition | user_signals | JSONB |
| ... | ... | ... | ... |

Full mapping in `/docs/BLITZ_IMPLEMENTATION_CHECKLIST.md`

## Error Handling

- **Button expected**: "Just tap one of the options above 👆"
- **Photo format**: "Please send a valid image (JPG or PNG)"
- **Network errors**: Auto-retry with user notification
- **Save failures**: Session cached and retried on next interaction

## Session Management

Sessions are persisted to `conversation_state` table:

```json
{
  "user_id": 123456789,
  "current_section": "religion_culture",
  "current_question": 21,
  "answers": {
    "gender_identity": "Male",
    "religion": "Hindu",
    ...
  },
  "skip_questions": [5, 11],
  "multi_select_buffer": {},
  "photo_urls": [],
  "started_at": "2026-02-21T10:30:00Z",
  "last_active": "2026-02-21T10:35:00Z"
}
```

Users can exit mid-flow and resume from the same question.

## Progress Tracking

Use `/progress` command to see:
- Questions completed (X/77)
- Profile completion percentage
- Missing required fields

## Deployment

### Staging

Deploy to Fly.io staging:

```bash
fly deploy --config fly.staging.toml
```

### Production

After staging validation:

```bash
fly deploy --config fly.production.toml
```

## Monitoring

Check logs:

```bash
fly logs -a jodi-matchmaker-staging
```

## Support

For issues or questions, contact:
- **Product**: Seema (seema-agent)
- **Tech**: Kavi (kavi-agent)
- **Code**: Blitz (blitz-agent)

## Status

- [x] Config system (question definitions)
- [x] Onboarding handler (button flow)
- [x] Conditional logic (branching)
- [x] Validation (input checking)
- [x] Database adapter (Supabase)
- [x] Main bot entry point
- [ ] Complete all 77 questions in config.py (currently 1-17)
- [ ] Photo upload to cloud storage (currently using file_id)
- [ ] Conversational mode integration
- [ ] Deploy to staging
- [ ] End-to-end testing
- [ ] Production deployment

## Next Steps

1. **Complete config.py** - Add questions 18-77
2. **Coordinate with Kavi** - Ensure schema matches
3. **Deploy to staging** - Test with real users
4. **Iterate based on feedback**
5. **Production deploy**

---

**Built by**: Blitz  
**Spec by**: Seema  
**Last updated**: February 21, 2026
