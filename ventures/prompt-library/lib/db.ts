import { Pool } from 'pg'

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  // Fly.io internal network doesn't need SSL
  ssl: false
})

export default pool
