#!/bin/bash
# ============================================================================
# JODI Schema Migration Runner
# Runs all schema upgrades in order against Supabase
# ============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}JODI Schema Migration Runner${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if SUPABASE_DB_URL is set
if [ -z "$SUPABASE_DB_URL" ]; then
  echo -e "${RED}Error: SUPABASE_DB_URL environment variable not set${NC}"
  echo "Set it with: export SUPABASE_DB_URL='postgresql://...'"
  exit 1
fi

# Confirm before running
echo -e "${YELLOW}This will modify the following tables:${NC}"
echo "  - users (add columns)"
echo "  - user_signals (new table)"
echo "  - user_preferences (new table)"
echo "  - tier_progress (new table)"
echo "  - matches (new table)"
echo ""
echo -e "${YELLOW}Database: ${SUPABASE_DB_URL}${NC}"
echo ""
read -p "Continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
  echo "Migration cancelled."
  exit 0
fi

# Run migrations in order
MIGRATIONS=(
  "01_users_table_upgrade.sql"
  "02_user_signals_table.sql"
  "03_user_preferences_table.sql"
  "04_tier_progress_table.sql"
  "05_matches_table.sql"
)

for migration in "${MIGRATIONS[@]}"; do
  echo -e "${GREEN}Running: $migration${NC}"
  psql "$SUPABASE_DB_URL" -f "$migration"
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Success${NC}"
  else
    echo -e "${RED}✗ Failed${NC}"
    exit 1
  fi
  echo ""
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All migrations completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Show table summary
echo -e "${YELLOW}Verifying tables...${NC}"
psql "$SUPABASE_DB_URL" -c "
  SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) AS size
  FROM information_schema.tables
  WHERE table_schema = 'public'
    AND table_name IN ('users', 'user_signals', 'user_preferences', 'tier_progress', 'matches')
  ORDER BY table_name;
"

echo ""
echo -e "${GREEN}Schema upgrade complete! ✓${NC}"
