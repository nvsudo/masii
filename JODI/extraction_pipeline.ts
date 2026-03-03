/**
 * JODI Extraction Pipeline
 * Real-time conversation → schema routing with CRUD operations
 * Handles DOB parsing, age validation, signal confidence, and LLM extraction
 */

import { SupabaseClient } from '@supabase/supabase-js';

export interface ExtractionResult {
  field: string;
  value: any;
  confidence: number; // 0.0 - 1.0
  source: 'explicit' | 'inferred' | 'button';
  tier: number;
  storage_location: 'users_column' | 'preferences_column' | 'signals_jsonb' | 'matches';
  table?: string;
  column?: string;
  jsonb_path?: string;
}

export interface ConversationContext {
  user_id: number;
  message: string;
  message_history?: string[]; // Recent conversation context
  current_tier: number;
}

/**
 * TIER 1 Field Extractors
 * These are hard filters - must be 100% accurate
 */

/**
 * Extract and validate date of birth
 * Validates age range: 18-80 years
 */
export async function extractDateOfBirth(
  context: ConversationContext
): Promise<ExtractionResult | null> {
  // Use LLM to extract date from natural language
  const datePattern = /\b(\d{1,2}[-\/]\d{1,2}[-\/]\d{4}|\d{4}[-\/]\d{1,2}[-\/]\d{1,2}|(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4})\b/i;
  
  const match = context.message.match(datePattern);
  if (!match) return null;
  
  const dateStr = match[0];
  const parsedDate = new Date(dateStr);
  
  if (isNaN(parsedDate.getTime())) {
    return null; // Invalid date
  }
  
  // Calculate age
  const today = new Date();
  let age = today.getFullYear() - parsedDate.getFullYear();
  const monthDiff = today.getMonth() - parsedDate.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < parsedDate.getDate())) {
    age--;
  }
  
  // Validate age range: 18-80
  if (age < 18 || age > 80) {
    throw new Error(`Age must be between 18 and 80 years. Calculated age: ${age}`);
  }
  
  return {
    field: 'date_of_birth',
    value: parsedDate.toISOString().split('T')[0], // YYYY-MM-DD
    confidence: 1.0,
    source: 'explicit',
    tier: 1,
    storage_location: 'users_column',
    table: 'users',
    column: 'date_of_birth'
  };
}

/**
 * Extract age directly (if DOB not provided)
 * Validates age range: 18-80
 */
export async function extractAge(
  context: ConversationContext
): Promise<ExtractionResult | null> {
  const agePattern = /\b(?:i'm|im|i am)\s+(\d{1,2})\s*(?:years old)?\b|\b(\d{1,2})\s*(?:yo|y\/o|years old)\b/i;
  
  const match = context.message.match(agePattern);
  if (!match) return null;
  
  const age = parseInt(match[1] || match[2]);
  
  // Validate age range
  if (age < 18 || age > 80) {
    throw new Error(`Age must be between 18 and 80 years. Provided age: ${age}`);
  }
  
  // Calculate approximate DOB (using current year)
  const today = new Date();
  const birthYear = today.getFullYear() - age;
  const approxDOB = `${birthYear}-01-01`; // Approximate to Jan 1
  
  return {
    field: 'date_of_birth',
    value: approxDOB,
    confidence: 0.85, // Lower confidence since it's approximate
    source: 'explicit',
    tier: 1,
    storage_location: 'users_column',
    table: 'users',
    column: 'date_of_birth'
  };
}

/**
 * LLM-based Multi-Field Extractor
 * Uses Claude/GPT to extract multiple fields from a single message
 */
export async function extractFieldsWithLLM(
  context: ConversationContext,
  llmModel: 'claude' | 'gpt' = 'claude'
): Promise<ExtractionResult[]> {
  const systemPrompt = `You are a data extraction agent for a matchmaking service.
Extract profile fields from user messages with confidence scores (0.0-1.0).

CRITICAL RULES:
1. Age validation: Only accept ages 18-80 years
2. Return confidence < 0.70 for uncertain extractions
3. Mark source as 'explicit' if directly stated, 'inferred' if implied
4. For Tier 1 hard filters, require confidence >= 0.90
5. Skip extraction if not mentioned

Return JSON array of extractions:
{
  "field": "<field_name>",
  "value": "<extracted_value>",
  "confidence": <0.0-1.0>,
  "source": "explicit|inferred",
  "tier": <1|2|3|4>
}

Available fields by tier:
TIER 1 (Hard Filters - Explicit Only):
- gender_identity, sexual_orientation, city, nationality, religion
- children_intent, marital_history, smoking, drinking, dietary_restrictions
- relationship_intent, relationship_timeline

TIER 2 (Lifestyle & Values - Mix):
- occupation, industry, work_style, work_life_balance, income_bracket
- living_situation, exercise_fitness, travel_frequency, social_energy
- political_orientation, family_values, ambition_level
- love_language, conflict_style, green_flags_sought, red_flags_cited

TIER 3 (Psychological - Inferred):
- attachment_style, big5_openness, big5_extraversion, emotional_intelligence
- communication_style, humor_style, decision_making_style

User message: "${context.message}"

Recent context (if relevant):
${context.message_history?.slice(-3).join('\n') || 'N/A'}

Extract fields:`;

  // Call LLM API (pseudo-code - replace with actual API call)
  const llmResponse = await callLLMAPI(systemPrompt, llmModel);
  
  // Parse LLM JSON response
  const extractions: ExtractionResult[] = JSON.parse(llmResponse);
  
  // Map to storage locations
  return extractions.map(ext => ({
    ...ext,
    ...getStorageLocation(ext.field, ext.tier)
  }));
}

/**
 * Map field name to storage location
 */
function getStorageLocation(
  field: string,
  tier: number
): Partial<ExtractionResult> {
  // Tier 1 hard filter columns
  const tier1Columns = [
    'full_name', 'date_of_birth', 'age', 'gender_identity', 'sexual_orientation',
    'city', 'country', 'nationality', 'ethnicity', 'native_languages',
    'religion', 'children_intent', 'marital_history', 'smoking', 'drinking',
    'dietary_restrictions', 'relationship_intent', 'relationship_timeline',
    'occupation', 'industry', 'education_level', 'caste_community', 'height_cm'
  ];
  
  if (tier1Columns.includes(field)) {
    return {
      storage_location: 'users_column',
      table: 'users',
      column: field
    };
  }
  
  // Preferences (hard filters for partner)
  const preferenceFields = [
    'age_min', 'age_max', 'gender_preference', 'location_preference',
    'religion_preference', 'children_preference', 'education_minimum'
  ];
  
  if (preferenceFields.includes(field)) {
    return {
      storage_location: 'preferences_column',
      table: 'user_preferences',
      column: field
    };
  }
  
  // Everything else goes to JSONB signals
  const jsonbCategory = getJSONBCategory(field);
  return {
    storage_location: 'signals_jsonb',
    table: 'user_signals',
    jsonb_path: `${jsonbCategory}.${field}`
  };
}

/**
 * Determine JSONB category for a field
 */
function getJSONBCategory(field: string): string {
  const lifestyleFields = [
    'work_style', 'work_life_balance', 'income_bracket', 'financial_style',
    'living_situation', 'exercise_fitness', 'diet_food_culture', 'travel_frequency',
    'social_energy', 'weekend_pattern', 'pet_ownership', 'substance_use'
  ];
  
  const valuesFields = [
    'political_orientation', 'religious_practice_level', 'family_values',
    'gender_role_views', 'cultural_identity_strength', 'ambition_level',
    'philanthropy_giving', 'environmental_views', 'education_importance', 'key_issue_stances'
  ];
  
  const relationshipFields = [
    'love_language', 'conflict_style', 'independence_needs', 'past_relationship_count',
    'reason_last_ended', 'green_flags_sought', 'red_flags_cited',
    'physical_type_preference', 'intellectual_match_preference', 'shared_activities_preference'
  ];
  
  const personalityFields = [
    'attachment_style', 'big5_openness', 'big5_conscientiousness', 'big5_extraversion',
    'big5_agreeableness', 'big5_neuroticism', 'emotional_intelligence',
    'communication_style', 'humor_style', 'decision_making_style', 'stress_response',
    'optimism_spectrum', 'novelty_seeking', 'self_awareness_level',
    'question_patterns_about_matches', 'rejection_reasons_evolution', 'self_narrative_evolution'
  ];
  
  const familyFields = [
    'family_structure', 'family_of_origin_dynamics', 'parenting_philosophy',
    'extended_family_expectations', 'financial_background', 'immigration_story',
    'relationship_with_parents', 'community_ties'
  ];
  
  const mediaFields = [
    'voice_tone_energy', 'vocabulary_sophistication', 'emoji_expression_style',
    'response_latency_pattern', 'message_length_pattern', 'topic_initiation_patterns',
    'emotional_disclosure_depth', 'consistency_over_time',
    'response_speed_to_matches', 'engagement_depth_variance', 'return_rate_after_rejection'
  ];
  
  if (lifestyleFields.includes(field)) return 'lifestyle';
  if (valuesFields.includes(field)) return 'values';
  if (relationshipFields.includes(field)) return 'relationship_style';
  if (personalityFields.includes(field)) return 'personality';
  if (familyFields.includes(field)) return 'family_background';
  if (mediaFields.includes(field)) return 'media_signals';
  
  return 'match_learnings'; // Default for Tier 4
}

/**
 * CRUD Operations for Profile Data
 */

/**
 * CREATE: Add extracted field to database
 */
export async function createField(
  supabase: SupabaseClient,
  userId: number,
  extraction: ExtractionResult
): Promise<void> {
  if (extraction.storage_location === 'users_column') {
    // Update users table column
    await supabase
      .from('users')
      .update({ [extraction.column!]: extraction.value })
      .eq('id', userId);
      
  } else if (extraction.storage_location === 'preferences_column') {
    // Upsert user_preferences
    await supabase
      .from('user_preferences')
      .upsert({
        user_id: userId,
        [extraction.column!]: extraction.value
      }, { onConflict: 'user_id' });
      
  } else if (extraction.storage_location === 'signals_jsonb') {
    // Use upsert_user_signal function
    const [category, field] = extraction.jsonb_path!.split('.');
    await supabase.rpc('upsert_user_signal', {
      p_user_id: userId,
      p_signal_category: category,
      p_field_name: field,
      p_value: extraction.value,
      p_confidence: extraction.confidence,
      p_source: extraction.source
    });
  }
}

/**
 * READ: Get field value with confidence
 */
export async function readField(
  supabase: SupabaseClient,
  userId: number,
  field: string
): Promise<{ value: any; confidence?: number; source?: string } | null> {
  const location = getStorageLocation(field, 1); // Tier doesn't matter for read
  
  if (location.storage_location === 'users_column') {
    const { data } = await supabase
      .from('users')
      .select(location.column!)
      .eq('id', userId)
      .single();
    
    return data ? { value: data[location.column!] } : null;
    
  } else if (location.storage_location === 'preferences_column') {
    const { data } = await supabase
      .from('user_preferences')
      .select(location.column!)
      .eq('user_id', userId)
      .single();
    
    return data ? { value: data[location.column!] } : null;
    
  } else if (location.storage_location === 'signals_jsonb') {
    const [category, fieldName] = location.jsonb_path!.split('.');
    const { data } = await supabase.rpc('get_user_signal', {
      p_user_id: userId,
      p_signal_category: category,
      p_field_name: fieldName
    });
    
    if (!data) return null;
    
    return {
      value: data.value,
      confidence: data.confidence,
      source: data.source
    };
  }
  
  return null;
}

/**
 * UPDATE: Update existing field (only if new confidence >= existing)
 */
export async function updateField(
  supabase: SupabaseClient,
  userId: number,
  extraction: ExtractionResult
): Promise<boolean> {
  // For columns, just update directly
  if (extraction.storage_location === 'users_column' || extraction.storage_location === 'preferences_column') {
    await createField(supabase, userId, extraction);
    return true;
  }
  
  // For JSONB, check confidence first
  const existing = await readField(supabase, userId, extraction.field);
  
  if (!existing || !existing.confidence || extraction.confidence >= existing.confidence) {
    await createField(supabase, userId, extraction);
    return true;
  }
  
  return false; // Didn't update (existing confidence higher)
}

/**
 * DELETE: Remove field from profile
 */
export async function deleteField(
  supabase: SupabaseClient,
  userId: number,
  field: string
): Promise<void> {
  const location = getStorageLocation(field, 1);
  
  if (location.storage_location === 'users_column') {
    await supabase
      .from('users')
      .update({ [location.column!]: null })
      .eq('id', userId);
      
  } else if (location.storage_location === 'preferences_column') {
    await supabase
      .from('user_preferences')
      .update({ [location.column!]: null })
      .eq('user_id', userId);
      
  } else if (location.storage_location === 'signals_jsonb') {
    const [category, fieldName] = location.jsonb_path!.split('.');
    // Remove key from JSONB
    await supabase.rpc('remove_user_signal', {
      p_user_id: userId,
      p_signal_category: category,
      p_field_name: fieldName
    });
  }
}

/**
 * Main extraction orchestrator
 * Processes a user message and routes all extracted fields to DB
 */
export async function processConversationMessage(
  supabase: SupabaseClient,
  context: ConversationContext
): Promise<{
  extracted: ExtractionResult[];
  errors: string[];
  tier_updated: boolean;
}> {
  const extracted: ExtractionResult[] = [];
  const errors: string[] = [];
  
  try {
    // 1. Try DOB extraction first (critical for age validation)
    const dobResult = await extractDateOfBirth(context);
    if (dobResult) {
      extracted.push(dobResult);
    } else {
      // Try direct age extraction
      const ageResult = await extractAge(context);
      if (ageResult) {
        extracted.push(ageResult);
      }
    }
  } catch (err: any) {
    errors.push(err.message);
  }
  
  // 2. LLM-based multi-field extraction
  try {
    const llmExtractions = await extractFieldsWithLLM(context);
    extracted.push(...llmExtractions);
  } catch (err: any) {
    errors.push(`LLM extraction failed: ${err.message}`);
  }
  
  // 3. Route all extractions to DB
  for (const extraction of extracted) {
    try {
      await updateField(supabase, context.user_id, extraction);
    } catch (err: any) {
      errors.push(`Failed to store ${extraction.field}: ${err.message}`);
    }
  }
  
  // 4. Recalculate tier completion
  const tierUpdated = await recalculateTierProgress(supabase, context.user_id);
  
  return { extracted, errors, tier_updated: tierUpdated };
}

/**
 * Recalculate tier completion and check MVP activation
 */
async function recalculateTierProgress(
  supabase: SupabaseClient,
  userId: number
): Promise<boolean> {
  // Check MVP activation
  const { data: mvpCheck } = await supabase.rpc('check_mvp_activation', {
    p_user_id: userId
  });
  
  if (mvpCheck && mvpCheck[0].mvp_achieved && !mvpCheck[0].profile_active) {
    // Activate profile for matching!
    await supabase
      .from('users')
      .update({
        profile_active: true,
        matching_activated_at: new Date().toISOString()
      })
      .eq('id', userId);
    
    return true; // Tier updated (MVP achieved!)
  }
  
  return false;
}

/**
 * Placeholder LLM API call
 * Replace with actual Anthropic/OpenAI API integration
 */
async function callLLMAPI(prompt: string, model: 'claude' | 'gpt'): Promise<string> {
  // TODO: Integrate with actual LLM API
  throw new Error('LLM API integration required');
}

/**
 * Export all CRUD operations
 */
export const ProfileCRUD = {
  create: createField,
  read: readField,
  update: updateField,
  delete: deleteField
};
