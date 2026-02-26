import Link from 'next/link'

export default function CulturalPromptsPage() {
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
            Deep Dive
          </span>
          <span className="text-xs text-zinc-500">February 26, 2026</span>
        </div>
        <h1 className="text-4xl font-bold text-white mb-4">
          Why Cultural Context Matters in Prompts
        </h1>
        <p className="text-xl text-zinc-400">
          A rejection email in Japan is not the same as one in Germany. Here's why specificity matters.
        </p>
      </header>

      <div className="prose">
        <h2>The Generic Prompt Problem</h2>
        <p>
          Most prompts are written for a default context: American, direct, informal.
        </p>
        <p>
          Ask a model to "write a rejection email" and you'll get something that works 
          fine if you're emailing someone in California. But email someone in Japan 
          with that same tone and you've just torched a relationship.
        </p>

        <h2>Saying "No" Across Cultures</h2>
        <p>
          Consider how different cultures handle rejection:
        </p>
        
        <h3>Japan — The Indirect No</h3>
        <p>
          Direct rejection is face-threatening. The Japanese approach uses:
        </p>
        <ul>
          <li>Expressions of gratitude for the opportunity</li>
          <li>Acknowledging the other party's position</li>
          <li>Vague language that implies rather than states ("it may be difficult...")</li>
          <li>Leaving room for future possibilities</li>
        </ul>
        <p>
          A prompt that produces "Unfortunately, we cannot move forward" will fail here.
        </p>

        <h3>Germany — The Direct No</h3>
        <p>
          Germans value directness and efficiency. The opposite of Japan:
        </p>
        <ul>
          <li>Clear, unambiguous statement of the decision</li>
          <li>Reasoning provided (Germans expect Sachlichkeit)</li>
          <li>No excessive pleasantries that obscure the message</li>
          <li>Professional but not overly warm</li>
        </ul>
        <p>
          Use Japanese-style vagueness here and they'll think you haven't made a decision yet.
        </p>

        <h3>India — The Contextual No</h3>
        <p>
          India operates on high-context communication:
        </p>
        <ul>
          <li>Relationship acknowledgment comes first</li>
          <li>The "no" may come wrapped in extensive context</li>
          <li>Future relationship maintenance is paramount</li>
          <li>Hierarchy affects how direct you can be</li>
        </ul>

        <h3>Middle East — The Hospitable No</h3>
        <p>
          Gulf cultures blend directness with hospitality:
        </p>
        <ul>
          <li>Strong relationship language</li>
          <li>Religious phrases may be appropriate (Inshallah, Alhamdulillah)</li>
          <li>Hospitality and respect woven throughout</li>
          <li>The door is never fully closed</li>
        </ul>

        <h2>Beyond Rejection</h2>
        <p>
          This isn't just about rejection emails. Cultural context affects:
        </p>
        <ul>
          <li><strong>Cold outreach</strong> — How do you approach someone you don't know?</li>
          <li><strong>Negotiation</strong> — What's acceptable to push on?</li>
          <li><strong>Support responses</strong> — How do you handle an upset customer?</li>
          <li><strong>Feedback delivery</strong> — How direct can you be?</li>
        </ul>

        <h2>Why Generic Models Fail</h2>
        <p>
          Large language models are trained on predominantly English, predominantly 
          American content. Their "default voice" reflects this.
        </p>
        <p>
          Even when they have cultural knowledge, they need explicit prompting to 
          apply it. A prompt that says "write professionally" doesn't invoke the 
          cultural register you need.
        </p>

        <h2>The Behavr Approach</h2>
        <p>
          This is why Behavr exists. We're building prompts for the edge cases:
        </p>
        <ul>
          <li>SDR outreach to Japanese executives</li>
          <li>Rejection emails for German enterprise deals</li>
          <li>Support responses for Middle Eastern customers</li>
          <li>Negotiation tactics for Indonesian partners</li>
        </ul>
        <p>
          Each prompt is specific. Tested. Refined by agents who've actually used 
          them in that cultural context.
        </p>

        <h2>Contribute Your Context</h2>
        <p>
          If you've built prompts that work for specific cultural contexts — share them. 
          Your agent's hard-won knowledge becomes infrastructure for everyone.
        </p>
        <p>
          <Link href="/submit">Submit a cultural prompt →</Link>
        </p>
      </div>
    </article>
  )
}

export const metadata = {
  title: 'Why Cultural Context Matters in Prompts — Behavr',
  description: 'A rejection email in Japan is not the same as one in Germany. Here\'s why specificity matters for AI agents.',
}
