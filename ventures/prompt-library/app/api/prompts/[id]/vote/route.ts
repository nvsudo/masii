import { NextRequest, NextResponse } from 'next/server'
import pool from '@/lib/db'

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const body = await request.json()
    const { voted_by, vote_type } = body

    if (!voted_by || !vote_type) {
      return NextResponse.json(
        { error: 'voted_by and vote_type are required' },
        { status: 400 }
      )
    }

    if (!['upvote', 'downvote'].includes(vote_type)) {
      return NextResponse.json(
        { error: 'vote_type must be "upvote" or "downvote"' },
        { status: 400 }
      )
    }

    // Upsert vote (update if user already voted, insert if new)
    await pool.query(
      `INSERT INTO prompt_votes (prompt_id, voted_by, vote_type)
       VALUES ($1, $2, $3)
       ON CONFLICT (prompt_id, voted_by)
       DO UPDATE SET vote_type = $3, voted_at = NOW()`,
      [id, voted_by, vote_type]
    )

    // Get updated counts
    const result = await pool.query(
      `SELECT upvote_count, downvote_count FROM prompts WHERE id = $1`,
      [id]
    )

    return NextResponse.json({
      success: true,
      upvotes: result.rows[0].upvote_count,
      downvotes: result.rows[0].downvote_count,
    })
  } catch (error) {
    console.error('Vote error:', error)
    return NextResponse.json({ error: 'Failed to record vote' }, { status: 500 })
  }
}
