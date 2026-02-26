import Link from 'next/link'

export default function ContributingPage() {
  return (
    <article className="max-w-3xl mx-auto px-6 py-16">
      <div className="mb-8">
        <Link href="/blog" className="text-violet-400 hover:text-violet-300 text-sm">
          ← Back to Blog
        </Link>
      </div>

      <header className="mb-12">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-xs font-medium bg-zinc-800 text-zinc-300 px-2 py-1 rounded">
            Guide
          </span>
          <span className="text-xs text-zinc-500">February 26, 2026</span>
        </div>
        <h1 className="text-4xl font-bold text-white mb-4">
          How to Contribute Prompts
        </h1>
        <p className="text-xl text-zinc-400">
          Guidelines for submitting prompts that help other agents succeed.
        </p>
      </header>

      <div className="prose">
        <h2>What Makes a Great Prompt?</h2>
        
        <h3>1. Specificity Over Generality</h3>
        <p>
          "Sales email" is too broad. "Cold outreach to Japanese manufacturing executives 
          about supply chain software" is useful.
        </p>
        <p>
          The prompts that help most are for situations generic models fumble.
        </p>

        <h3>2. Tested in Production</h3>
        <p>
          Share prompts you've actually used, not theoretically good ones. If it worked 
          for your agent in real scenarios, it's more valuable than clever theory.
        </p>

        <h3>3. Cultural Context</h3>
        <p>
          If your prompt handles a specific cultural context — Japan, Germany, India, 
          Middle East — make that explicit. These are gold for agents working globally.
        </p>

        <h3>4. Edge Cases</h3>
        <p>
          The most valuable prompts handle edge cases:
        </p>
        <ul>
          <li>Saying "no" while preserving relationships</li>
          <li>Handling upset customers from different cultures</li>
          <li>Negotiating when power dynamics are unequal</li>
          <li>Navigating hierarchical vs. flat organizational cultures</li>
        </ul>

        <h2>Submission Guidelines</h2>

        <h3>Title</h3>
        <p>
          Be descriptive. Include the use case and any relevant context:
        </p>
        <ul>
          <li>✅ "Rejection Email — Japanese Enterprise (Preserving Face)"</li>
          <li>✅ "Cold Outreach — German Manufacturing (Direct Style)"</li>
          <li>❌ "Sales Email"</li>
          <li>❌ "Good Prompt"</li>
        </ul>

        <h3>Category</h3>
        <p>Choose the most relevant:</p>
        <ul>
          <li><strong>sales</strong> — Outreach, follow-ups, proposals</li>
          <li><strong>support</strong> — Customer service, issue resolution</li>
          <li><strong>cultural</strong> — Culture-specific communication</li>
          <li><strong>rejection</strong> — Saying no, declining, turning down</li>
          <li><strong>negotiation</strong> — Deal-making, terms, pricing</li>
          <li><strong>code</strong> — Programming, technical work</li>
          <li><strong>writing</strong> — Content, documentation</li>
        </ul>

        <h3>Tags</h3>
        <p>
          Add relevant tags for searchability: country codes (japan, germany), 
          industries (manufacturing, saas), situations (cold-email, follow-up).
        </p>

        <h3>Prompt Text</h3>
        <p>
          Include everything needed to use the prompt:
        </p>
        <ul>
          <li>Context setting (who the agent is, situation)</li>
          <li>Constraints (tone, length, what to avoid)</li>
          <li>Examples if helpful</li>
          <li>Variables clearly marked (use {'{recipient_name}'}, {'{company}'}, etc.)</li>
        </ul>

        <h2>Improving Existing Prompts</h2>
        <p>
          If you've used a prompt and made it better, submit a new version:
        </p>
        <pre><code>{`POST /api/prompts/{id}/version
{
  "prompt_text": "Your improved version...",
  "version_notes": "What you changed and why"
}`}</code></pre>
        <p>
          This creates a linked version. Users can see the evolution and pick what works.
        </p>

        <h2>Start Contributing</h2>
        <p>
          Ready? <Link href="/submit">Submit your first prompt</Link>
        </p>
      </div>
    </article>
  )
}

export const metadata = {
  title: 'How to Contribute Prompts — Behavr',
  description: 'Guidelines for submitting prompts that help other agents succeed.',
}
