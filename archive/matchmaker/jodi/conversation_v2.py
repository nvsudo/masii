"""
Conversation Orchestrator for Jodi V2 — 4-Tier Data Capture Framework

THIS IS THE PRODUCT. The conversation quality and signal extraction matter most.

Implements:
- Tier-aware signal extraction with confidence scoring
- Data routing to correct schema locations (hard filters vs signals)
- Progress tracking across 4 tiers
- MVP activation gates
- Model enforcement (opus/sonnet/gpt-5 only)

Author: Blitz
Date: 2026-02-11
"""

from typing import Dict, List, Optional, Tuple
import anthropic
import os
import json
from datetime import datetime, date

from db_postgres_v2 import JodiDB, json_serializer


class ConversationOrchestratorV2:
    """
    Orchestrates multi-session conversations with tier-aware data extraction.
    
    Key responsibilities:
    1. Extract signals from user messages with confidence scores
    2. Route extracted data to correct schema locations
    3. Track tier progress after each extraction
    4. Check MVP activation gates
    5. Generate contextual next questions
    """
    
    # Tier definitions
    TIER_DEFINITIONS = {
        1: {
            'name': 'THE BASICS',
            'description': 'Identity, demographics, hard deal-breakers',
            'duration': '5-7 min',
            'required_fields': 15,  # Full name, DOB, gender, religion, etc.
            'completion_threshold': 100.0  # Must be 100% for MVP
        },
        2: {
            'name': 'READY',
            'description': 'Lifestyle, values, relationship style',
            'duration': '3-7 days',
            'target_fields': 40,  # 13 lifestyle + 10 values + 10 relationship + 7 preferences
            'completion_threshold': 70.0  # 70%+ activates matching
        },
        3: {
            'name': 'DEEP PROFILE',
            'description': 'Psychological signals, family depth, behavioral patterns',
            'duration': 'Weeks 2-4',
            'target_fields': 30,  # 14 personality + 8 family + 8 media
            'completion_threshold': 50.0  # Nice-to-have, not blocking
        },
        4: {
            'name': 'CALIBRATED',
            'description': 'Post-match learning, revealed preferences',
            'duration': 'Ongoing',
            'completion_threshold': 0.0  # No minimum
        }
    }
    
    # Model quality enforcement
    ALLOWED_MODELS = [
        'claude-opus-4-5',
        'claude-sonnet-4-5',
        'claude-opus-4-20250514',
        'claude-sonnet-4-20250514',
        'gpt-5'
    ]
    
    # Confidence thresholds
    CONFIDENCE_THRESHOLDS = {
        'store_minimum': 0.70,  # Don't store signals below this
        'explicit': 1.0,  # Direct asks
        'strong_inference': 0.85,  # Clear from context
        'moderate_inference': 0.70,  # Educated guess
    }
    
    def __init__(self, anthropic_api_key: str = None, model: str = 'claude-sonnet-4-20250514'):
        self.client = anthropic.Anthropic(
            api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.db = JodiDB()
        
        # Enforce model quality
        if model not in self.ALLOWED_MODELS:
            raise ValueError(
                f"Model {model} not allowed. Must use opus/sonnet/gpt-5 for extraction quality. "
                f"Allowed: {self.ALLOWED_MODELS}"
            )
        self.model = model
    
    def get_welcome_message(self) -> str:
        """Initial message when user starts."""
        return (
            "Namaste! 🙏\n\n"
            "I'm Jodi, your matchmaking companion. Think of me as a friend who's really good "
            "at connecting people.\n\n"
            "We'll have a few conversations over the next few days — nothing rushed. "
            "I'll get to know you, understand what matters to you, and when I have a clear picture, "
            "I'll start introducing you to people I think you'd genuinely connect with.\n\n"
            "Let's start simple: tell me about yourself! Who are you, what do you do, where are you from?"
        )
    
    def process_user_message(
        self,
        telegram_id: int,
        user_message: str,
        conversation_history: List[Dict]
    ) -> Dict:
        """
        Main orchestration method: process user message and extract signals.
        
        Args:
            telegram_id: User's Telegram ID
            user_message: User's latest message
            conversation_history: Recent messages [{role, content}, ...]
        
        Returns:
            {
                'extracted_data': {...},  # What was learned
                'tier_progress': {...},   # Current progress
                'mvp_status': {...},      # MVP activation status
                'next_message': str,       # Bot's response
                'completeness': float      # Overall % (0-100)
            }
        """
        print(f"   🔧 [ORCH-1] Starting orchestration for user {telegram_id}")
        print(f"   🔧 [ORCH-1] Message length: {len(user_message)} chars")
        print(f"   🔧 [ORCH-1] History length: {len(conversation_history)} messages")
        
        # Get current profile state
        profile = self.db.get_full_profile(telegram_id)
        if not profile:
            # New user - create profile
            print(f"   🔧 [ORCH-1] New user, creating profile...")
            self.db.create_user(telegram_id)
            profile = self.db.get_full_profile(telegram_id)
        
        # Extract signals from user message
        print(f"   🧠 [ORCH-2] Calling _extract_signals...")
        try:
            extracted = self._extract_signals(user_message, conversation_history, profile)
            print(f"   ✅ [ORCH-2] Extraction succeeded")
            print(f"      - Hard filters: {list(extracted.get('hard_filters', {}).keys())}")
            signal_count = sum(len(v) for v in extracted.get('signals', {}).values())
            print(f"      - Signals count: {signal_count}")
            print(f"      - Tier: {extracted.get('tier')}")
        except Exception as e:
            print(f"   ❌ [ORCH-2] Extraction FAILED: {type(e).__name__}: {e}")
            raise
        
        # Route extracted data to schema
        print(f"   📤 [ORCH-3] Routing data to database...")
        try:
            self._route_to_schema(telegram_id, extracted)
            print(f"   ✅ [ORCH-3] Data routed successfully")
        except Exception as e:
            print(f"   ❌ [ORCH-3] Routing FAILED: {type(e).__name__}: {e}")
            raise
        
        # Update tier progress
        print(f"   📊 [ORCH-4] Updating tier progress...")
        try:
            tier_progress = self._update_tier_progress(telegram_id, extracted)
            print(f"   ✅ [ORCH-4] Tier progress updated")
            print(f"      - Completions: T1={tier_progress.get('tier1_completion')}%, T2={tier_progress.get('tier2_completion')}%")
        except Exception as e:
            print(f"   ❌ [ORCH-4] Progress update FAILED: {type(e).__name__}: {e}")
            raise
        
        # Check MVP activation
        print(f"   🎯 [ORCH-5] Checking MVP activation...")
        mvp_status = self.db.check_mvp_activation(telegram_id)
        
        # Calculate completeness
        completeness = self.db.calculate_user_completeness(telegram_id)
        print(f"   ✅ [ORCH-5] MVP check complete, completeness: {completeness}%")
        
        # Generate next message
        print(f"   💭 [ORCH-6] Generating next message...")
        try:
            next_message = self._generate_next_message(
                telegram_id,
                user_message,
                conversation_history,
                tier_progress,
                mvp_status,
                completeness
            )
            print(f"   ✅ [ORCH-6] Message generated: '{next_message[:50]}'")
        except Exception as e:
            print(f"   ❌ [ORCH-6] Message generation FAILED: {type(e).__name__}: {e}")
            raise
        
        print(f"   ✅ [ORCH-COMPLETE] Orchestration finished")
        
        return {
            'extracted_data': extracted,
            'tier_progress': tier_progress,
            'mvp_status': dict(mvp_status) if mvp_status else None,
            'next_message': next_message,
            'completeness': completeness
        }
    
    def _extract_signals(
        self,
        user_message: str,
        conversation_history: List[Dict],
        profile: Dict
    ) -> Dict:
        """
        Extract signals from user message using Claude with confidence scoring.
        
        Returns:
            {
                'hard_filters': {field: value},  # Tier 1 explicit data
                'signals': {
                    'lifestyle': {field: {value, confidence, source}},
                    'values': {...},
                    'relationship_style': {...},
                    ...
                },
                'preferences': {
                    'hard_filters': {...},
                    'soft_preferences': {...}
                },
                'tier': int,  # Which tier this data belongs to
                'open_ended': bool  # Was this an open-ended response?
            }
        """
        # Build extraction prompt
        recent_history = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-6:]
        ])
        
        current_profile_summary = json.dumps({
            'demographics': profile.get('user', {}),
            'existing_signals': profile.get('signals', {}),
            'tier_progress': profile.get('tier_progress', {})
        }, indent=2, default=json_serializer)
        
        extraction_prompt = f"""
You are analyzing a conversation for a matchmaking platform. Extract ALL learnable information from the user's latest message.

User said: "{user_message}"

Recent conversation:
{recent_history}

Current profile:
{current_profile_summary}

Extract and return a JSON object with:

1. **hard_filters** - Tier 1 explicit facts (only if directly stated):
   - full_name, date_of_birth, age, gender_identity, sexual_orientation
   - city, country, nationality, ethnicity, native_languages (array)
   - religion, religious_practice_level, children_intent, marital_history
   - smoking, drinking, dietary_restrictions
   - relationship_intent, relationship_timeline
   - occupation, industry, education_level, caste_community, height_cm

2. **signals** - Tier 2-3 inferred characteristics (with confidence 0.0-1.0):
   Categories: lifestyle, values, relationship_style, personality, family_background, media_signals
   
   Format per signal:
   {{
     "field_name": {{
       "value": <any type>,
       "confidence": <0.70-1.00>,  // Don't return if <0.70
       "source": "explicit" | "inferred",
       "reasoning": "<why you inferred this>"
     }}
   }}
   
   Example lifestyle signals:
   - work_style, work_life_balance, income_bracket, financial_style
   - living_situation, exercise_fitness, diet_food_culture, travel_frequency
   - social_energy, weekend_pattern, pet_ownership, substance_use
   
   Example values signals:
   - political_orientation, family_values, gender_role_views
   - cultural_identity_strength, ambition_level, philanthropy_giving
   - environmental_views, education_importance
   
   Example relationship_style signals:
   - love_language, conflict_style, independence_needs
   - past_relationship_count, reason_last_ended
   - green_flags_sought (array), red_flags_cited (array)
   - physical_type_preference, intellectual_match_preference

3. **preferences** - What they're looking for in a partner:
   {{
     "hard_filters": {{
       "age_min": <int>,
       "age_max": <int>,
       "gender_preference": [<array>],
       "location_preference": [<array>],
       "religion_preference": [<array>],
       "children_preference": <string>
     }},
     "soft_preferences": {{
       "field": {{"values": [...], "weight": <0-1>, "type": "exact_match"|"range"}}
     }},
     "dealbreakers": [<array of strings>],
     "green_flags": [<array of strings>]
   }}

4. **tier** - Which tier does this data belong to? (1|2|3|4)
5. **open_ended** - Was this a substantive open-ended response? (true|false)
   True if: >20 words, describes experiences/feelings/preferences in depth

Return ONLY valid JSON. No markdown, no explanations outside JSON.

CRITICAL RULES:
- Confidence >= 0.70 required to store
- Explicit (directly stated) = 1.0
- Strong inference (clear from context) = 0.85-0.95
- Moderate inference = 0.70-0.84
- Weak guess (<0.70) = DO NOT INCLUDE
- Include reasoning for all inferences

**CRITICAL: Date of Birth Handling**
If user mentions their birth date:
1. Extract to "date_of_birth" field in hard_filters
2. Format as YYYY-MM-DD (ISO 8601)
3. Confidence = 1.0 (explicit)
4. Age will be calculated automatically (don't extract "age" separately)

Valid formats:
- "I was born on May 15, 1995" → "1995-05-15"
- "My birthday is 05/15/1995" → "1995-05-15"
- "15th May 1995" → "1995-05-15"

DO NOT extract if:
- User only mentions age ("I'm 28") - need explicit DOB
- Date is ambiguous or unclear

**Button Fields (Only extract if EXPLICITLY stated):**
These fields use Telegram buttons, so only extract if user explicitly states them:
- gender_identity, sexual_orientation, smoking, drinking
- religion, children_intent, marital_history
- relationship_intent, relationship_timeline
- dietary_restrictions, education_level

DO NOT infer these from context. Confidence must be 1.0 (explicit) for button fields.
"""
        
        print(f"      🌐 [API-1] Preparing Claude API call...")
        print(f"      🌐 [API-1] Model: {self.model}")
        print(f"      🌐 [API-1] API key present: {bool(self.client.api_key)}")
        
        try:
            print(f"      🌐 [API-2] Calling Anthropic API...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": extraction_prompt}]
            )
            print(f"      ✅ [API-2] API call succeeded")
            print(f"         - Response length: {len(response.content[0].text)} chars")
            print(f"         - Usage: input={response.usage.input_tokens}, output={response.usage.output_tokens}")
            
            response_text = response.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.rsplit("```", 1)[0]
            
            print(f"      📋 [API-3] Parsing JSON response...")
            extracted = json.loads(response_text)
            print(f"      ✅ [API-3] JSON parsed successfully")
            print(f"         - Keys: {list(extracted.keys())}")
            
            # Validate and filter by confidence threshold
            print(f"      🔍 [API-4] Filtering by confidence threshold...")
            extracted = self._filter_by_confidence(extracted)
            print(f"      ✅ [API-4] Filtering complete")
            
            return extracted
        
        except json.JSONDecodeError as e:
            print(f"      ❌ [API-3] JSON parsing FAILED: {e}")
            print(f"         - Raw response: {response_text[:200] if 'response_text' in locals() else 'N/A'}")
            # Return empty extraction on error
            return {
                'hard_filters': {},
                'signals': {},
                'preferences': {},
                'tier': 1,
                'open_ended': len(user_message.split()) > 20
            }
        except Exception as e:
            print(f"      ❌ [API-2] API call FAILED: {type(e).__name__}: {e}")
            if hasattr(self.client, 'api_key') and self.client.api_key:
                print(f"         - API key (first 10): {self.client.api_key[:10]}")
            else:
                print(f"         - API key: NONE")
            import traceback
            traceback.print_exc()
            # Return empty extraction on error
            return {
                'hard_filters': {},
                'signals': {},
                'preferences': {},
                'tier': 1,
                'open_ended': len(user_message.split()) > 20
            }
    
    def _filter_by_confidence(self, extracted: Dict) -> Dict:
        """Remove signals below confidence threshold."""
        threshold = self.CONFIDENCE_THRESHOLDS['store_minimum']
        
        if 'signals' in extracted:
            for category in extracted['signals']:
                if isinstance(extracted['signals'][category], dict):
                    # Filter fields by confidence
                    filtered = {
                        field: data
                        for field, data in extracted['signals'][category].items()
                        if isinstance(data, dict) and data.get('confidence', 0) >= threshold
                    }
                    extracted['signals'][category] = filtered
        
        return extracted
    
    def _route_to_schema(self, telegram_id: int, extracted: Dict):
        """Route extracted data to correct database tables/columns."""
        
        # 1. Hard filters → users table
        if extracted.get('hard_filters'):
            self.db.update_user_hard_filters(telegram_id, extracted['hard_filters'])
        
        # 2. Signals → user_signals JSONB (by category)
        if extracted.get('signals'):
            for category, signals in extracted['signals'].items():
                if signals:  # Not empty
                    self.db.upsert_user_signals(telegram_id, category, signals)
        
        # 3. Preferences → user_preferences table
        if extracted.get('preferences'):
            prefs = extracted['preferences']
            self.db.upsert_user_preferences(
                telegram_id,
                hard_filters=prefs.get('hard_filters'),
                soft_preferences=prefs.get('soft_preferences'),
                dealbreakers=prefs.get('dealbreakers'),
                green_flags=prefs.get('green_flags')
            )
    
    def _update_tier_progress(self, telegram_id: int, extracted: Dict) -> Dict:
        """Update tier progress tracking after extraction."""
        
        # Determine which fields were completed
        completed_fields = {
            'tier1': list(extracted.get('hard_filters', {}).keys()),
            'tier2': [],
            'tier3': [],
            'tier4': []
        }
        
        # Map signals to tiers
        tier2_categories = ['lifestyle', 'values', 'relationship_style']
        tier3_categories = ['personality', 'family_background', 'media_signals']
        tier4_categories = ['match_learnings']
        
        for category, signals in extracted.get('signals', {}).items():
            if category in tier2_categories:
                completed_fields['tier2'].extend(signals.keys())
            elif category in tier3_categories:
                completed_fields['tier3'].extend(signals.keys())
            elif category in tier4_categories:
                completed_fields['tier4'].extend(signals.keys())
        
        # Calculate tier completion percentages
        # Note: This is approximate - full calculation done in SQL function
        tier_completions = {}
        
        # Get current progress to calculate deltas
        current_progress = self.db.get_tier_progress(telegram_id)
        
        # Build open-ended response if applicable
        open_ended_response = None
        if extracted.get('open_ended'):
            open_ended_response = {
                'question': 'Open-ended question',  # Would come from conversation context
                'response': 'User response',  # Truncated for storage
                'signals_extracted': sum(len(s) for s in extracted.get('signals', {}).values()),
                'asked_at': datetime.now().isoformat()
            }
        
        # Update tier progress
        result = self.db.update_tier_progress(
            telegram_id,
            tier_completions=tier_completions if tier_completions else None,
            completed_fields=completed_fields,
            open_ended_response=open_ended_response,
            session_increment=False  # Session increment happens at conversation start
        )
        
        return result
    
    def _generate_next_message(
        self,
        telegram_id: int,
        user_message: str,
        conversation_history: List[Dict],
        tier_progress: Dict,
        mvp_status: Dict,
        completeness: float
    ) -> str:
        """
        Generate the next conversational message.
        
        Logic:
        1. If Tier 1 incomplete → ask for missing hard filters
        2. If Tier 1 complete but < 70% Tier 2 → ask lifestyle/values questions
        3. If MVP achieved → offer to show matches
        4. Otherwise → deepen understanding
        """
        
        # Get current tier level
        tier1_completion = tier_progress.get('tier1_completion', 0) if tier_progress else 0
        tier2_completion = tier_progress.get('tier2_completion', 0) if tier_progress else 0
        
        # Check MVP status
        meets_mvp = mvp_status.get('meets_mvp', False) if mvp_status else False
        blocked_reasons = mvp_status.get('blocked_reasons', []) if mvp_status else []
        
        # Build context for Claude
        recent_history = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in conversation_history[-4:]
        ])
        
        # Different prompts based on progress
        if meets_mvp:
            # MVP achieved - offer matches
            return (
                f"I feel like I have a good understanding of who you are now! "
                f"Your profile is {completeness:.0f}% complete. 🎉\n\n"
                f"Ready to see some matches? I've found a few people I think you'd connect with."
            )
        
        elif tier1_completion < 100:
            # Still need Tier 1 basics
            prompt = f"""
You're a warm matchmaker getting to know someone. They just said: "{user_message}"

Recent conversation:
{recent_history}

Their profile is {tier1_completion:.0f}% complete (Tier 1: THE BASICS).
Still need: {blocked_reasons[0] if blocked_reasons else 'core demographics'}

Generate a natural follow-up question to complete their basic profile.
Be conversational, not interrogative. ONE question only.

Focus on missing Tier 1 fields:
- Identity (age, location, occupation)
- Religious/cultural background
- Relationship intent and timeline
- Life situation (children, marital history)
- Lifestyle basics (smoking, drinking, diet)

Your question:"""
        
        elif tier2_completion < 70:
            # Need more Tier 2 (lifestyle, values, preferences)
            prompt = f"""
You're a matchmaker who knows the basics about this person. Now going deeper.

They just said: "{user_message}"

Recent conversation:
{recent_history}

Their profile: {tier1_completion:.0f}% Tier 1 (complete), {tier2_completion:.0f}% Tier 2.
Need 70% Tier 2 to start matching.

Generate a warm, curious question to understand:
- Lifestyle patterns (work, fitness, social life, weekends)
- Values (family, ambition, political/cultural views)
- What they're looking for in a partner

Be natural. ONE question. No lists.

Your question:"""
        
        else:
            # Tier 2 sufficient, build depth
            prompt = f"""
You're a matchmaker deepening your understanding of this person.

They said: "{user_message}"

Recent conversation:
{recent_history}

Profile: {completeness:.0f}% complete. Almost ready to match!

Generate a thoughtful follow-up to understand:
- Relationship history and what they learned
- Family dynamics and expectations
- What excites them about meeting someone

Be warm and curious. ONE question.

Your question:"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
        
        except Exception as e:
            print(f"❌ Response generation error: {e}")
            # Fallback
            return "Tell me more about that! I want to understand you better."
    
    def get_progress_summary(self, telegram_id: int) -> str:
        """Generate a user-facing progress summary."""
        profile = self.db.get_full_profile(telegram_id)
        if not profile:
            return "Profile not started."
        
        tier_progress = profile.get('tier_progress')
        completeness = profile.get('completeness', 0)
        mvp_status = profile.get('mvp_status')
        
        if not tier_progress:
            return f"Your profile is {completeness:.0f}% complete. Let's keep building it!"
        
        tier1 = tier_progress.get('tier1_completion', 0)
        tier2 = tier_progress.get('tier2_completion', 0)
        tier3 = tier_progress.get('tier3_completion', 0)
        
        meets_mvp = mvp_status.get('meets_mvp', False) if mvp_status else False
        
        if meets_mvp:
            return (
                f"✅ Your profile is {completeness:.0f}% complete and ready to match!\n\n"
                f"**THE BASICS:** {tier1:.0f}%\n"
                f"**READY:** {tier2:.0f}%\n"
                f"**DEEP PROFILE:** {tier3:.0f}%"
            )
        else:
            blocked = mvp_status.get('blocked_reasons', []) if mvp_status else []
            blockers_text = "\n".join(f"  • {reason}" for reason in blocked[:3])
            
            return (
                f"Your profile is {completeness:.0f}% complete.\n\n"
                f"**Progress:**\n"
                f"• THE BASICS: {tier1:.0f}%\n"
                f"• READY: {tier2:.0f}%\n"
                f"• DEEP PROFILE: {tier3:.0f}%\n\n"
                f"**To start matching:**\n"
                f"{blockers_text}"
            )


if __name__ == '__main__':
    # Test conversation flow
    print("=== JODI V2 CONVERSATION ORCHESTRATOR TEST ===\n")
    
    conv = ConversationOrchestratorV2()
    
    # Simulate conversation
    test_telegram_id = 888888888
    
    print(f"Welcome message:\n{conv.get_welcome_message()}\n")
    
    # User response
    test_message = "I'm Raj, 28, working as a software engineer in Mumbai. I'm from a Gujarati family, vegetarian."
    
    result = conv.process_user_message(
        test_telegram_id,
        test_message,
        conversation_history=[
            {"role": "assistant", "content": conv.get_welcome_message()},
            {"role": "user", "content": test_message}
        ]
    )
    
    print(f"Extracted data: {json.dumps(result['extracted_data'], indent=2, default=json_serializer)}\n")
    print(f"Completeness: {result['completeness']:.1f}%\n")
    print(f"MVP Status: {result['mvp_status']}\n")
    print(f"Next message: {result['next_message']}\n")
    
    # Progress summary
    summary = conv.get_progress_summary(test_telegram_id)
    print(f"Progress summary:\n{summary}\n")
    
    print("✅ Test complete!")
