'use client'

import { useState, useEffect, use } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

interface Prompt {
  id: number
  title: string
  prompt_text: string
  category: string
  tags: string[]
  submitted_by: string
  signals: {
    fetches: number
    upvotes: number
    downvotes: number
    feedback_count: number
  }
  version: {
    number: number
    upstream_id: number | null
    downstream_id: number | null
    notes: string
    is_latest: boolean
  }
  version_chain: Array<{
    id: number
    version: number
    created_at: string
    is_latest: boolean
  }>
  created_at: string
}

export default function PromptDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const [prompt, setPrompt] = useState<Prompt | null>(null)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState('')
  const [rating, setRating] = useState(0)
  const [submittingFeedback, setSubmittingFeedback] = useState(false)

  useEffect(() => {
    fetchPrompt()
  }, [id])

  const fetchPrompt = async () => {
    try {
      const response = await fetch(`/api/prompts/${id}?fetched_by=web_user&source=web`)
      const data = await response.json()
      setPrompt(data)
    } catch (error) {
      console.error('Error fetching prompt:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (prompt) {
      navigator.clipboard.writeText(prompt.prompt_text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleVote = async (voteType: 'upvote' | 'downvote') => {
    try {
      const response = await fetch(`/api/prompts/${id}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          voted_by: 'web_user',
          vote_type: voteType,
        }),
      })
      
      if (response.ok) {
        fetchPrompt() // Refresh to get updated counts
      }
    } catch (error) {
      console.error('Error voting:', error)
    }
  }

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!feedback.trim()) return

    setSubmittingFeedback(true)
    try {
      const response = await fetch(`/api/prompts/${id}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          feedback_text: feedback,
          submitted_by: 'web_user',
          rating: rating || null,
        }),
      })

      if (response.ok) {
        setFeedback('')
        setRating(0)
        fetchPrompt() // Refresh to get updated count
      }
    } catch (error) {
      console.error('Error submitting feedback:', error)
    } finally {
      setSubmittingFeedback(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!prompt) {
    return <div className="text-center py-12">Prompt not found</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <Link href="/" className="text-blue-600 hover:underline">
          ← Back to browse
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {prompt.title}
              </h1>
              <div className="flex items-center gap-3 text-sm text-gray-500">
                {prompt.category && (
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
                    {prompt.category}
                  </span>
                )}
                <span>by {prompt.submitted_by}</span>
                <span>v{prompt.version.number}</span>
              </div>
            </div>
          </div>

          {prompt.tags && prompt.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-4">
              {prompt.tags.map((tag) => (
                <span key={tag} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Version Navigation */}
        {prompt.version_chain.length > 1 && (
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <div className="text-sm font-medium text-gray-700 mb-2">Version History:</div>
            <div className="flex items-center gap-2 flex-wrap">
              {prompt.version_chain.map((v) => (
                <Link
                  key={v.id}
                  href={`/prompt/${v.id}`}
                  className={`px-3 py-1 rounded ${
                    v.id === prompt.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  v{v.version}
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Prompt Text */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold">Prompt</h2>
            <button
              onClick={handleCopy}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
            >
              {copied ? '✓ Copied!' : '📋 Copy'}
            </button>
          </div>
          <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto text-sm border border-gray-200 whitespace-pre-wrap">
            {prompt.prompt_text}
          </pre>
        </div>

        {/* Signals */}
        <div className="grid grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{prompt.signals.fetches}</div>
            <div className="text-sm text-gray-600">Uses</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{prompt.signals.upvotes}</div>
            <div className="text-sm text-gray-600">Upvotes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{prompt.signals.downvotes}</div>
            <div className="text-sm text-gray-600">Downvotes</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{prompt.signals.feedback_count}</div>
            <div className="text-sm text-gray-600">Feedback</div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => handleVote('upvote')}
            className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
          >
            👍 Upvote
          </button>
          <button
            onClick={() => handleVote('downvote')}
            className="flex-1 px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium"
          >
            👎 Downvote
          </button>
        </div>

        {/* Feedback Form */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Leave Feedback</h2>
          <form onSubmit={handleSubmitFeedback} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rating (optional)
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    className={`text-2xl ${star <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              rows={4}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Share your experience with this prompt..."
            />
            <button
              type="submit"
              disabled={!feedback.trim() || submittingFeedback}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {submittingFeedback ? 'Submitting...' : 'Submit Feedback'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
