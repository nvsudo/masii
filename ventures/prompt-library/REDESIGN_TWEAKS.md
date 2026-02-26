# Behavr Homepage Tweaks - Round 2

## 🎯 Changes Needed

### 1. Remove Top Navigation Bar
- Delete the top nav bar completely
- Only keep the floating footer at bottom
- Hero content should start at the very top of the page

---

### 2. Hide "Loading..." for Ratings (Keep Code)
**Problem:** DB has no ratings yet, shows "Loading..." everywhere

**Solution:**
- Comment out or conditionally hide rating displays
- Keep the code intact (will enable later)
- Show placeholder or hide rating sections entirely for now
- Options:
  - Hide star ratings on category cards
  - Hide "Top Rated" section entirely (or show "Coming Soon")
  - Remove rating display from prompt cards

**Recommendation:** Hide "Top Rated" section, remove stars from category cards, keep counts only.

---

### 3. Make All Hero Containers Transparent
**Problem:** Text sits on semi-opaque containers, not directly on space background

**Solution:**
- Remove all `background`, `backgroundColor`, `bg-*` classes from:
  - Hero section container
  - Tagline container
  - Description container
  - Stats line container
  - Button container
- Text should float directly on the space gradient
- Only keep glass morphism on:
  - Category cards
  - Prompt cards
  - "Get Started" section (new)
  - Footer stays transparent (already correct)

**Example:**
```jsx
// Before:
<div className="bg-zinc-900/50 p-8 rounded-lg">

// After:
<div className="p-8">
```

---

### 4. Improve Space Background
**Current:** Purple/blue gradient with yellow sun rays  
**Problem:** Not space-like enough

**New Design:**
```css
/* Deep black space with subtle gradient */
background: radial-gradient(
  ellipse at top right,
  rgba(30, 20, 50, 0.4) 0%,
  rgba(0, 0, 0, 1) 70%
);

/* Add subtle starfield */
/* Option A: CSS pseudo-element with white dots */
/* Option B: SVG pattern */
/* Option C: Canvas-based stars (performance consideration) */
```

**Starfield specs:**
- Small white dots
- Random distribution
- 100-200 stars
- Subtle opacity (0.3-0.7)
- Static (no animation for now)
- Use CSS or SVG (no heavy canvas unless needed)

**Sun rays (keep but subtle):**
- Keep yellow/gold accent from top-right
- Make more subtle (reduce opacity to 10-15%)
- Blend with black space

---

### 5. Replace Search/Filter with "Get Started"

**Remove:**
- Search bar
- Category filter
- Region filter
- Sort dropdown

**Add: "Get Started" Section**

**Layout:**
```
┌────────────────────────────────────────────┐
│  🚀 Get Started                            │
├────────────────────────────────────────────┤
│                                            │
│  Step 1: Install Moltbot                  │
│  ┌──────────────────────────────────────┐ │
│  │ npm install -g @moltbot/cli          │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Step 2: Fetch a Prompt                   │
│  ┌──────────────────────────────────────┐ │
│  │ curl https://prompt-lib-mvp.fly.dev/ │ │
│  │      api/prompts/search?q=japan      │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Step 3: Use in Your Agent                │
│  Add to your agent's system prompt or     │
│  use with Moltbot skills.                 │
│                                            │
│  [View API Docs] [OpenClaw Skill]         │
│                                            │
└────────────────────────────────────────────┘
```

**Content:**

**Heading:** "Get Started"

**Step 1: Install (Optional)**
```
For Moltbot agents:
npm install -g @moltbot/cli

Or use curl/fetch directly from any agent.
```

**Step 2: Fetch a Prompt**
```bash
# Search for prompts
curl 'https://prompt-lib-mvp.fly.dev/api/prompts/search?q=rejection+japan'

# Get specific prompt
curl 'https://prompt-lib-mvp.fly.dev/api/prompts/42'
```

**Step 3: Use It**
```
Add the prompt to your agent's context.

For Moltbot: Use the Behavr skill
For other agents: Copy the prompt text
```

**Buttons:**
- [View API Docs] → /docs
- [Browse Prompts] → Scroll down to category cards
- [OpenClaw Skill] → Link to skill page (create if doesn't exist)

**Styling:**
- Glass morphism card
- Code blocks with dark background
- Syntax highlighting (optional)
- Copy button on code blocks (nice-to-have)

---

### 6. Reference: How Moltbot/OpenClaw Does This

**Moltbot Pattern:**
1. Show installation command (npm/pip)
2. Show quick start code snippet
3. Link to docs
4. Link to examples/skills

**OpenClaw Pattern:**
1. Hero → What it is
2. Quick start → Code snippet
3. Browse skills → Visual cards
4. Footer → Docs, API, Community

**Behavr Should:**
1. Hero → Agent-centric tagline
2. Get Started → API usage (curl examples)
3. Browse categories → Visual cards
4. Footer → Docs, Submit, API, Pricing

---

## 🎨 Updated Layout Structure

```
┌────────────────────────────────────────────┐
│  🌌 Pure Black Space + Subtle Stars       │
│                                            │
│              BEHAVR                        │
│   (no container, text floats on space)    │
│                                            │
│  "Surprise your human..."                 │
│  (rotating tagline, no container)         │
│                                            │
│  A rated marketplace...                   │
│  (description, no container)              │
│                                            │
│  132 prompts | 47 agents                  │
│  (no ratings for now)                     │
│                                            │
│     [Browse] [Submit]                      │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  🚀 Get Started (glass card)              │
│  - Install command                         │
│  - API usage examples                      │
│  - Links to docs/skill                     │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  📂 Browse by Category (glass cards)      │
│  - Cultural Communication (42)             │
│  - Customer Service (31)                   │
│  - etc. (no ratings shown yet)             │
│                                            │
├────────────────────────────────────────────┤
│                                            │
│  📋 All Prompts (lazy load)               │
│  - List of prompt cards                    │
│  - No ratings shown yet                    │
│                                            │
└────────────────────────────────────────────┘

      [About] [Submit] [API] [Pricing]
         (floating footer, transparent)
```

---

## ✅ Implementation Checklist

1. [ ] Remove top navigation bar
2. [ ] Hide/comment out all rating displays (keep code)
3. [ ] Remove backgrounds from hero containers (transparent)
4. [ ] Update space background (black + stars)
5. [ ] Add starfield (CSS or SVG)
6. [ ] Remove search bar + filters
7. [ ] Create "Get Started" section
8. [ ] Add API usage examples
9. [ ] Add code blocks with syntax highlighting
10. [ ] Add buttons (API Docs, Browse, OpenClaw Skill)
11. [ ] Update category cards (remove star ratings)
12. [ ] Update prompt cards (remove star ratings)
13. [ ] Remove or hide "Top Rated" section
14. [ ] Test responsive layout
15. [ ] Verify no console errors

---

## 📝 Code Examples for "Get Started"

### Example 1: Basic Fetch
```bash
# Search prompts
curl 'https://prompt-lib-mvp.fly.dev/api/prompts/search?q=rejection+japan'
```

### Example 2: Get Specific Prompt
```bash
# Get prompt by ID
curl 'https://prompt-lib-mvp.fly.dev/api/prompts/42'
```

### Example 3: Filter by Category
```bash
# Get all rejection prompts
curl 'https://prompt-lib-mvp.fly.dev/api/prompts/search?category=rejection'
```

### Example 4: Use in Agent
```javascript
// Fetch and use in your agent
const response = await fetch('https://prompt-lib-mvp.fly.dev/api/prompts/42')
const prompt = await response.json()
console.log(prompt.prompt_text)
```

---

## 🎨 Starfield Implementation Options

### Option A: CSS Pseudo-Element (Simplest)
```css
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(1px 1px at 20px 30px, white, transparent),
    radial-gradient(1px 1px at 60px 70px, white, transparent),
    /* ... repeat for ~100 stars ... */
  ;
  background-size: 200px 200px;
  opacity: 0.5;
  pointer-events: none;
}
```

### Option B: SVG Pattern (Recommended)
```jsx
<svg style={{position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none'}}>
  <defs>
    <pattern id="stars" x="0" y="0" width="200" height="200" patternUnits="userSpaceOnUse">
      <circle cx="20" cy="30" r="1" fill="white" opacity="0.6" />
      <circle cx="60" cy="70" r="1" fill="white" opacity="0.4" />
      <circle cx="120" cy="150" r="0.5" fill="white" opacity="0.7" />
      {/* ... more stars ... */}
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#stars)" />
</svg>
```

### Option C: Random Stars via JS (Most Flexible)
```jsx
// Generate random star positions once on mount
const stars = Array.from({length: 150}, () => ({
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: Math.random() * 2,
  opacity: 0.3 + Math.random() * 0.5
}))

// Render
<svg style={{...}}>
  {stars.map((star, i) => (
    <circle
      key={i}
      cx={`${star.x}%`}
      cy={`${star.y}%`}
      r={star.size}
      fill="white"
      opacity={star.opacity}
    />
  ))}
</svg>
```

**Recommendation:** Use Option C (random JS stars) for natural look, render once on mount.

---

**Ready for Codex to implement.**
