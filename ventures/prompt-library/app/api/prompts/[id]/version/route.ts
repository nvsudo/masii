import { NextRequest, NextResponse } from 'next/server'
import pool from '@/lib/db'

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const body = await request.json()
    const { prompt_text, version_notes, submitted_by } = body

    if (!prompt_text) {
      return NextResponse.json(
        { error: 'prompt_text is required' },
        { status: 400 }
      )
    }

    // Get the original prompt
    const originalResult = await pool.query(
      `SELECT * FROM prompts WHERE id = $1`,
      [id]
    )

    if (originalResult.rows.length === 0) {
      return NextResponse.json({ error: 'Original prompt not found' }, { status: 404 })
    }

    const original = originalResult.rows[0]

    // Start transaction
    const client = await pool.connect()
    try {
      await client.query('BEGIN')

      // Create new version
      const newVersionResult = await client.query(
        `INSERT INTO prompts (
          title, prompt_text, category, tags, submitted_by,
          upstream_id, version_number, version_notes, is_latest_in_chain
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, TRUE)
        RETURNING *`,
        [
          original.title,
          prompt_text,
          original.category,
          original.tags,
          submitted_by || 'anonymous',
          id,
          original.version_number + 1,
          version_notes || ''
        ]
      )

      const newVersion = newVersionResult.rows[0]

      // Update original to point to new version and mark as not latest
      await client.query(
        `UPDATE prompts 
         SET downstream_id = $1, is_latest_in_chain = FALSE
         WHERE id = $2`,
        [newVersion.id, id]
      )

      await client.query('COMMIT')

      return NextResponse.json({
        id: newVersion.id,
        title: newVersion.title,
        prompt_text: newVersion.prompt_text,
        version_number: newVersion.version_number,
        version_notes: newVersion.version_notes,
        upstream_id: newVersion.upstream_id,
        created_at: newVersion.created_at,
      }, { status: 201 })
    } catch (error) {
      await client.query('ROLLBACK')
      throw error
    } finally {
      client.release()
    }
  } catch (error) {
    console.error('Create version error:', error)
    return NextResponse.json({ error: 'Failed to create version' }, { status: 500 })
  }
}
