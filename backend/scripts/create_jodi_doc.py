#!/usr/bin/env python3
"""Create Google Doc and share with nikunj.vora@gmail.com"""
import google_api, json, urllib.parse

def create_doc(title, content):
    body = {"title": title}
    doc = google_api.api_post('https://docs.googleapis.com/v1/documents', body)
    doc_id = doc['documentId']
    # batchUpdate to set content as simple text
    requests = [{
        'insertText': {'location': {'index': 1}, 'text': content}
    }]
    google_api.api_post(f'https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate', {'requests': requests})
    return doc_id

def share_doc(doc_id, email):
    # Drive permissions API
    body = {"role": "writer", "type": "user", "emailAddress": email}
    google_api.api_post(f'https://www.googleapis.com/drive/v3/files/{doc_id}/permissions', body)

if __name__ == '__main__':
    title = 'Jodi Platform — Database Schema Design (v1)'
    content = '''# Jodi Platform — Database Schema Design (v1)\n**Agreed: 2026-02-10**\n**Participants:** N, Kavi, A\n\n---\n\n## Design Philosophy\n\nHybrid approach balancing query performance with schema flexibility:\n- **Hard filter columns** (real Postgres columns, indexed) for fields queried on every match run\n- **JSONB columns** for structured but evolving preferences and personality data\n- **Separate interactions table** to prevent profile blob bloat\n- **Vector embeddings** ready from day 1 for v2 similarity matching\n\n---\n\n## Schema Overview\n\n### Tables\n\n**1. users**\n- Telegram auth, intake state, timestamps\n- Lightweight identity layer\n\n**2. profiles**\n- Hard filter columns (indexed): dob, gender, location, religion, relationship_intent, smoking, drinking, wants_children, education_level, height_cm\n- JSONB columns: preferences, personality_data, media_signals\n- Vector column: embedding (pgvector, 1536 dimensions)\n- Completeness score, timestamps\n\n**3. interactions** (append-only)\n- Conversation history separated from profiles\n- Columns: user_id, direction, content, extracted_data JSONB, interaction_type, created_at\n- Training data goldmine for future matching model\n\n**4. matches**\n- user_a_id, user_b_id, match_score, score_breakdown JSONB\n- Status, feedback from both sides\n- Snapshot of "why" at time of match\n\n---\n\n## Index Strategy\n\n- B-tree indexes on hard filter columns (age, location, religion, etc.)\n- Composite index on common filter combinations\n- GIN indexes on JSONB columns for key-based queries\n- IVFFlat index on embedding column for similarity search (post-ANALYZE)\n\n---\n\n## Key Design Decisions\n\n| Decision | Rationale |\n|----------|-----------|\n| Hard filters as real columns | Fast WHERE clauses, every match run |\n| Conversations out of profiles | Unbounded growth, doesn't bloat profile reads |\n| Embeddings column from day 1 | No schema migration needed for v2 |\n| JSONB for personality/preferences | Schema evolves as LLM extraction improves |\n| Stored match reasoning | Audit trail, explainability |\n\n---\n\n## Files\n\n- `schema.sql` — `/matchmaker/jodi/schema.sql`\n- `db_postgres.py` — `/matchmaker/jodi/db_postgres.py`\n\n---\n\n## Next Steps\n\n1. Set up Supabase project\n2. Run schema.sql against Supabase Postgres\n3. Configure DATABASE_URL in environment\n4. Test db_postgres.py connection\n5. Deploy bot to Fly.io\n\n---\n\n**Share with:** nikunj.vora@gmail.com (editor access)\n\nUse google_api.py or the Google Docs API to create and share. Return the doc link.\n'''
    doc_id = create_doc(title, content)
    share_doc(doc_id, 'nikunj.vora@gmail.com')
    print(f'https://docs.google.com/document/d/{doc_id}/edit')
