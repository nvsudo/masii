import { NextRequest, NextResponse } from 'next/server'
import pool from '@/lib/db'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { title, prompt_text, category, tags, submitted_by } = body

    if (!title || !prompt_text) {
      return NextResponse.json(
        { error: 'title and prompt_text are required' },
        { status: 400 }
      )
    }

    const result = await pool.query(
      `INSERT INTO prompts (title, prompt_text, category, tags, submitted_by)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING *`,
      [title, prompt_text, category, tags || [], submitted_by || 'anonymous']
    )

    const prompt = result.rows[0]

    return NextResponse.json({
      id: prompt.id,
      title: prompt.title,
      prompt_text: prompt.prompt_text,
      category: prompt.category,
      tags: prompt.tags,
      submitted_by: prompt.submitted_by,
      version_number: prompt.version_number,
      created_at: prompt.created_at,
    }, { status: 201 })
  } catch (error) {
    console.error('Create prompt error:', error)
    return NextResponse.json({ error: 'Failed to create prompt' }, { status: 500 })
  }
}
