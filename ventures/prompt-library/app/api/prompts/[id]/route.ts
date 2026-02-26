import { NextRequest, NextResponse } from 'next/server'
import pool from '@/lib/db'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const searchParams = request.nextUrl.searchParams
    const fetchedBy = searchParams.get('fetched_by') || 'anonymous'
    const source = searchParams.get('source') || 'web'

    // Get the prompt
    const promptResult = await pool.query(
      `SELECT * FROM prompts WHERE id = $1`,
      [id]
    )

    if (promptResult.rows.length === 0) {
      return NextResponse.json({ error: 'Prompt not found' }, { status: 404 })
    }

    const prompt = promptResult.rows[0]

    // Track the fetch
    await pool.query(
      `INSERT INTO prompt_fetches (prompt_id, fetched_by, source) VALUES ($1, $2, $3)`,
      [id, fetchedBy, source]
    )

    // Get version chain
    const versionChainQuery = `
      WITH RECURSIVE version_chain AS (
        -- Find the root (earliest version)
        SELECT id, upstream_id, downstream_id, version_number, created_at, is_latest_in_chain
        FROM prompts
        WHERE id = $1
        
        UNION ALL
        
        -- Follow upstream to root
        SELECT p.id, p.upstream_id, p.downstream_id, p.version_number, p.created_at, p.is_latest_in_chain
        FROM prompts p
        INNER JOIN version_chain vc ON p.id = vc.upstream_id
      )
      SELECT * FROM version_chain
      
      UNION
      
      -- Follow downstream from root
      WITH RECURSIVE downstream AS (
        SELECT id, upstream_id, downstream_id, version_number, created_at, is_latest_in_chain
        FROM prompts
        WHERE id = (
          SELECT id FROM version_chain 
          WHERE upstream_id IS NULL 
          LIMIT 1
        )
        
        UNION ALL
        
        SELECT p.id, p.upstream_id, p.downstream_id, p.version_number, p.created_at, p.is_latest_in_chain
        FROM prompts p
        INNER JOIN downstream d ON p.upstream_id = d.id
      )
      SELECT * FROM downstream
      ORDER BY version_number
    `

    const versionChainResult = await pool.query(versionChainQuery, [id])

    return NextResponse.json({
      id: prompt.id,
      title: prompt.title,
      prompt_text: prompt.prompt_text,
      category: prompt.category,
      tags: prompt.tags,
      submitted_by: prompt.submitted_by,
      signals: {
        fetches: prompt.fetch_count,
        upvotes: prompt.upvote_count,
        downvotes: prompt.downvote_count,
        feedback_count: prompt.feedback_count,
      },
      version: {
        number: prompt.version_number,
        upstream_id: prompt.upstream_id,
        downstream_id: prompt.downstream_id,
        notes: prompt.version_notes,
        is_latest: prompt.is_latest_in_chain,
      },
      version_chain: versionChainResult.rows.map((v: any) => ({
        id: v.id,
        version: v.version_number,
        created_at: v.created_at,
        is_latest: v.is_latest_in_chain,
      })),
      created_at: prompt.created_at,
    })
  } catch (error) {
    console.error('Get prompt error:', error)
    return NextResponse.json({ error: 'Failed to get prompt' }, { status: 500 })
  }
}
