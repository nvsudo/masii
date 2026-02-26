import { NextRequest, NextResponse } from 'next/server'
import pool from '@/lib/db'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const q = searchParams.get('q') || ''
    const category = searchParams.get('category')
    const tags = searchParams.get('tags')?.split(',').filter(Boolean)
    const limit = parseInt(searchParams.get('limit') || '20')
    const sortBy = searchParams.get('sort') || 'created_at'

    let query = `
      SELECT 
        id, title, prompt_text, category, tags, submitted_by,
        upstream_id, downstream_id, version_number, version_notes,
        created_at, fetch_count, upvote_count, downvote_count, feedback_count,
        is_deprecated, is_latest_in_chain
      FROM prompts
      WHERE is_deprecated = FALSE
    `
    const values: any[] = []
    let paramCount = 0

    if (q) {
      paramCount++
      query += ` AND (
        to_tsvector('english', title) @@ plainto_tsquery('english', $${paramCount})
        OR to_tsvector('english', prompt_text) @@ plainto_tsquery('english', $${paramCount})
      )`
      values.push(q)
    }

    if (category) {
      paramCount++
      query += ` AND category = $${paramCount}`
      values.push(category)
    }

    if (tags && tags.length > 0) {
      paramCount++
      query += ` AND tags && $${paramCount}::text[]`
      values.push(tags)
    }

    // Sort
    const sortColumn = {
      'created_at': 'created_at DESC',
      'popular': 'fetch_count DESC',
      'top_rated': 'upvote_count DESC',
    }[sortBy] || 'created_at DESC'
    
    query += ` ORDER BY ${sortColumn} LIMIT $${paramCount + 1}`
    values.push(limit)

    const result = await pool.query(query, values)

    const prompts = result.rows.map((row: any) => ({
      id: row.id,
      title: row.title,
      prompt_text: row.prompt_text,
      category: row.category,
      tags: row.tags,
      submitted_by: row.submitted_by,
      signals: {
        fetches: row.fetch_count,
        upvotes: row.upvote_count,
        downvotes: row.downvote_count,
        feedback_count: row.feedback_count,
      },
      version: {
        number: row.version_number,
        upstream_id: row.upstream_id,
        downstream_id: row.downstream_id,
        is_latest: row.is_latest_in_chain,
      },
      created_at: row.created_at,
    }))

    return NextResponse.json({
      prompts,
      total: prompts.length,
    })
  } catch (error) {
    console.error('Search error:', error)
    return NextResponse.json({ error: 'Search failed' }, { status: 500 })
  }
}
