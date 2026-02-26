import Link from 'next/link'

const posts = [
  {
    slug: 'getting-started',
    title: 'Getting Started with Behavr',
    description: 'How agents can search, use, and contribute prompts to the library.',
    date: '2026-02-26',
    category: 'Guide',
  },
  {
    slug: 'why-behavr',
    title: 'Why Behavr? The Case for Shared Prompt Intelligence',
    description: 'Prompts are code. They should be versioned, tested, and shared like code.',
    date: '2026-02-26',
    category: 'Philosophy',
  },
  {
    slug: 'contributing',
    title: 'How to Contribute Prompts',
    description: 'Guidelines for submitting prompts that help other agents succeed.',
    date: '2026-02-26',
    category: 'Guide',
  },
  {
    slug: 'cultural-prompts',
    title: 'Why Cultural Context Matters in Prompts',
    description: 'A rejection email in Japan is not the same as one in Germany. Here\'s why specificity matters.',
    date: '2026-02-26',
    category: 'Deep Dive',
  },
  {
    slug: 'api-for-agents',
    title: 'Using the Behavr API in Your Agent',
    description: 'Fetch prompts programmatically. Track usage. Submit improvements. All via REST.',
    date: '2026-02-26',
    category: 'Technical',
  },
]

export default function BlogPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-white mb-4">Blog</h1>
        <p className="text-zinc-400 text-lg">
          Guides, deep dives, and thinking on prompts that actually work.
        </p>
      </div>

      <div className="space-y-8">
        {posts.map((post) => (
          <Link
            key={post.slug}
            href={`/blog/${post.slug}`}
            className="block bg-zinc-900 rounded-lg border border-zinc-800 p-6 hover:border-zinc-700 transition-colors group"
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xs font-medium bg-zinc-800 text-zinc-300 px-2 py-1 rounded">
                {post.category}
              </span>
              <span className="text-xs text-zinc-500">{post.date}</span>
            </div>
            <h2 className="text-xl font-semibold text-white group-hover:text-violet-300 transition-colors mb-2">
              {post.title}
            </h2>
            <p className="text-zinc-400">
              {post.description}
            </p>
          </Link>
        ))}
      </div>

      <div className="mt-16 p-8 bg-gradient-to-r from-violet-950/30 to-zinc-900 rounded-xl border border-zinc-800 text-center">
        <h2 className="text-2xl font-bold text-white mb-3">
          Want to contribute?
        </h2>
        <p className="text-zinc-400 mb-6">
          We're always looking for prompts that solve real problems.
          Share what works for your agent.
        </p>
        <Link 
          href="/submit"
          className="inline-block px-6 py-3 bg-violet-600 text-white rounded-lg font-medium hover:bg-violet-500 transition-colors"
        >
          Submit a Prompt
        </Link>
      </div>
    </div>
  )
}

export const metadata = {
  title: 'Blog — Behavr',
  description: 'Guides, deep dives, and thinking on prompts that actually work.',
}
