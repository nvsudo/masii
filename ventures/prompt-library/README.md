# Prompt Library - Space Edition

Curated collection of real-world B2B sales & ops prompts, packaged as installable Agent Skills.

## 🚀 Current State (2026-02-26)

**Visual Redesign Complete:**
- Black space background with 150 random stars (0.3-0.7 opacity)
- Transparent hero section (text floats on space)
- Top nav hidden (code preserved)
- All ratings hidden (code preserved, commented out)
- Search/filters replaced with "Get Started" CTA
- New `/openclaw-skill` landing page created

**Tech Stack:**
- Next.js 15 + React 19
- TypeScript
- Tailwind CSS
- PostgreSQL (Supabase)

## 📦 Structure

```
app/
├── page.tsx                  # Home (space background + categories)
├── openclaw-skill/page.tsx   # Skill installer landing page
├── prompt/[id]/page.tsx      # Individual prompt view
├── submit/page.tsx           # Submission form
└── api/prompts/              # REST endpoints

components/
├── CategoryCard.tsx          # Category grid cards
└── RotatingTagline.tsx       # Animated hero text

lib/db.ts                     # Supabase client
schema.sql                    # Database schema
```

## 🧪 Running Locally

```bash
npm install
npm run dev
```

Visit: http://localhost:3000

## 🛠 Known Pending Items

See `STATUS.md` for tracked work items.

## 🔗 GitHub

https://github.com/nvsudo/jodi (prompt-library subdirectory)
