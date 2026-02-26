import Link from 'next/link'

export default function OpenClawSkillPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <div className="rounded-2xl border border-white/10 bg-zinc-900/60 p-8 shadow-xl shadow-black/30 backdrop-blur">
        <p className="text-xs uppercase tracking-[0.18em] text-zinc-400">OpenClaw Skill</p>
        <h1 className="mt-3 text-3xl font-bold text-white sm:text-4xl">Behavr Skill for Agent Workflows</h1>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-zinc-300 sm:text-base">
          Use Behavr prompts programmatically inside OpenClaw/Moltbot-style agents. Fetch prompts through the API,
          then inject them into system context or task-specific steps.
        </p>

        <div className="mt-8 grid gap-5 md:grid-cols-2">
          <div className="rounded-xl border border-white/10 bg-black/40 p-4">
            <p className="text-sm font-semibold text-white">Quick Fetch</p>
            <pre className="mt-3 overflow-x-auto text-xs leading-6 text-zinc-200 sm:text-sm">
              <code>{`curl 'https://prompt-lib-mvp.fly.dev/api/prompts/search?q=cultural+japan'`}</code>
            </pre>
          </div>

          <div className="rounded-xl border border-white/10 bg-black/40 p-4">
            <p className="text-sm font-semibold text-white">Agent Integration</p>
            <pre className="mt-3 overflow-x-auto text-xs leading-6 text-zinc-200 sm:text-sm">
              <code>{`const prompt = await fetchPrompt(42)
agent.addSystemContext(prompt.prompt_text)`}</code>
            </pre>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/docs"
            className="inline-flex items-center justify-center rounded-xl border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
          >
            View API Docs
          </Link>
          <Link
            href="/"
            className="inline-flex items-center justify-center rounded-xl border border-white/15 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white hover:bg-white/10"
          >
            Back to Homepage
          </Link>
        </div>
      </div>
    </div>
  )
}
