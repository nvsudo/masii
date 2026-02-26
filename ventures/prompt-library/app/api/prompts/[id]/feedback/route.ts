import { NextRequest, NextResponse } from 'next/server'
import pool from '@/lib/db'

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const body = await request.json()
    const { feedback_text, submitted_by, rating } = body

    if (!feedback_text) {
      return NextResponse.json(
        { error: 'feedback_text is required' },
        { status: 400 }
      )
    }

    if (rating && (rating < 1 || rating > 5)) {
      return NextResponse.json(
        { error: 'rating must be between 1 and 5' },
        { status: 400 }
      )
    }

    const result = await pool.query(
      `INSERT INTO prompt_feedback (prompt_id, feedback_text, submitted_by, rating)
       VALUES ($1, $2, $3, $4)
       RETURNING *`,
      [id, feedback_text, submitted_by || 'anonymous', rating || null]
    )

    const feedback = result.rows[0]

    return NextResponse.json({
      id: feedback.id,
      feedback_text: feedback.feedback_text,
      submitted_by: feedback.submitted_by,
      rating: feedback.rating,
      submitted_at: feedback.submitted_at,
    }, { status: 201 })
  } catch (error) {
    console.error('Feedback error:', error)
    return NextResponse.json({ error: 'Failed to submit feedback' }, { status: 500 })
  }
}
