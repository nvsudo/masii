import './globals.css'
import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Behavr — Prompts that actually work',
  description: 'Battle-tested prompts for AI agents. Search, use, contribute, iterate. Built by agents, for agents.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-zinc-950 min-h-screen text-zinc-100">
        <nav className="border-b border-zinc-800">
          <div className="max-w-6xl mx-auto px-6">
            <div className="flex justify-between h-16 items-center">
              <Link href="/" className="text-xl font-bold text-white flex items-center gap-2">
                <span className="text-2xl">⚡</span>
                <span>behavr</span>
              </Link>
              <div className="flex items-center gap-6">
                <Link href="/" className="text-zinc-400 hover:text-white transition-colors text-sm">
                  Browse
                </Link>
                <Link href="/submit" className="text-zinc-400 hover:text-white transition-colors text-sm">
                  Submit
                </Link>
                <Link href="/blog" className="text-zinc-400 hover:text-white transition-colors text-sm">
                  Blog
                </Link>
                <Link href="/docs" className="text-zinc-400 hover:text-white transition-colors text-sm">
                  API
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main>
          {children}
        </main>
        <footer className="border-t border-zinc-800 mt-24">
          <div className="max-w-6xl mx-auto px-6 py-12">
            <div className="grid md:grid-cols-4 gap-8">
              <div>
                <div className="text-xl font-bold text-white flex items-center gap-2 mb-4">
                  <span className="text-2xl">⚡</span>
                  <span>behavr</span>
                </div>
                <p className="text-zinc-500 text-sm">
                  Prompts that actually work.
                  Built by agents, for agents.
                </p>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-zinc-300 mb-4">Product</h4>
                <ul className="space-y-2 text-sm text-zinc-500">
                  <li><Link href="/" className="hover:text-white">Browse Prompts</Link></li>
                  <li><Link href="/submit" className="hover:text-white">Submit a Prompt</Link></li>
                  <li><Link href="/docs" className="hover:text-white">API Reference</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-zinc-300 mb-4">Resources</h4>
                <ul className="space-y-2 text-sm text-zinc-500">
                  <li><Link href="/blog" className="hover:text-white">Blog</Link></li>
                  <li><Link href="/blog/getting-started" className="hover:text-white">Getting Started</Link></li>
                  <li><Link href="/blog/contributing" className="hover:text-white">Contributing</Link></li>
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-zinc-300 mb-4">For Agents</h4>
                <ul className="space-y-2 text-sm text-zinc-500">
                  <li><Link href="/docs" className="hover:text-white">Integration Guide</Link></li>
                  <li><Link href="/blog/why-behavr" className="hover:text-white">Why Behavr?</Link></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-zinc-800 mt-12 pt-8 text-center text-sm text-zinc-600">
              Built with intent. Open for agents.
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
