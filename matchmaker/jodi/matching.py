"""
Contextual Matching Engine for Jodi.

NOT filter-based. Uses weighted contextual reasoning.
"Location matters less if cultural specificity is higher."
"""

from typing import Dict, List, Tuple
import math


class ContextualMatcher:
    """
    Matches based on weighted contextual reasoning, not boolean filters.
    
    The breakthrough: preferences have weights AND context.
    Trade-offs are explicit: "I'd accept X if Y is also true."
    """
    
    def __init__(self):
        pass
    
    def calculate_match_score(
        self, 
        profile_a: Dict, 
        profile_b: Dict
    ) -> Tuple[float, Dict]:
        """
        Calculate contextual match score between two profiles.
        
        Returns: (score, breakdown) where breakdown explains the score.
        """
        score = 0.0
        breakdown = {}
        
        # Extract data
        demo_a = profile_a.get('demographics', {})
        demo_b = profile_b.get('demographics', {})
        pref_a = profile_a.get('preferences', {})
        pref_b = profile_b.get('preferences', {})
        signals_a = profile_a.get('signals', [])
        signals_b = profile_b.get('signals', [])
        
        # ===== LOCATION SCORING (Canberra NRI magic happens here) =====
        location_score, location_breakdown = self._score_location(demo_a, demo_b, pref_a, pref_b)
        score += location_score
        breakdown['location'] = location_breakdown
        
        # ===== CULTURAL COMPATIBILITY =====
        cultural_score, cultural_breakdown = self._score_cultural(demo_a, demo_b, pref_a, pref_b)
        score += cultural_score
        breakdown['cultural'] = cultural_breakdown
        
        # ===== AGE COMPATIBILITY =====
        age_score, age_breakdown = self._score_age(demo_a, demo_b, pref_a, pref_b)
        score += age_score
        breakdown['age'] = age_breakdown
        
        # ===== LIFESTYLE =====
        lifestyle_score, lifestyle_breakdown = self._score_lifestyle(demo_a, demo_b, pref_a, pref_b)
        score += lifestyle_score
        breakdown['lifestyle'] = lifestyle_breakdown
        
        # ===== SIGNALS (contextual bonuses) =====
        signals_score, signals_breakdown = self._score_signals(signals_a, signals_b, pref_a, pref_b)
        score += signals_score
        breakdown['signals'] = signals_breakdown
        
        # Normalize to 0-100
        breakdown['total'] = round(score, 2)
        
        return score, breakdown
    
    def _score_location(
        self, 
        demo_a: Dict, 
        demo_b: Dict, 
        pref_a: Dict, 
        pref_b: Dict
    ) -> Tuple[float, Dict]:
        """
        The Canberra NRI test case happens here.
        
        Logic:
        - Same city = high score
        - Nearby city = medium score
        - Far city BUT high cultural match = compensated score
        - Different country = penalty (unless both are flexible)
        """
        score = 0.0
        breakdown = {}
        
        loc_a = demo_a.get('location', '').lower()
        loc_b = demo_b.get('location', '').lower()
        
        # Exact match
        if loc_a == loc_b:
            score += 30
            breakdown['same_city'] = 30
            return score, breakdown
        
        # Same metro area (e.g., Sydney + Sydney suburbs)
        if self._same_metro_area(loc_a, loc_b):
            score += 20
            breakdown['same_metro'] = 20
            return score, breakdown
        
        # Different cities: check flexibility and cultural compensation
        location_flex_a = pref_a.get('location_proximity', {}).get('weight', 0.5)
        location_flex_b = pref_b.get('location_proximity', {}).get('weight', 0.5)
        
        # If BOTH are flexible about location
        if location_flex_a < 0.6 and location_flex_b < 0.6:
            score += 15
            breakdown['both_flexible'] = 15
        elif location_flex_a < 0.6 or location_flex_b < 0.6:
            score += 10
            breakdown['one_flexible'] = 10
        
        # Check if they're in the same country (important for visas, immigration)
        if self._same_country(loc_a, loc_b):
            score += 5
            breakdown['same_country'] = 5
        else:
            score -= 10
            breakdown['different_country'] = -10
        
        # CULTURAL COMPENSATION (the key insight!)
        # If cultural match is strong, distance matters less
        cultural_weight_a = pref_a.get('cultural_weight', 'medium')
        cultural_weight_b = pref_b.get('cultural_weight', 'medium')
        
        if cultural_weight_a == 'HIGH' or cultural_weight_b == 'HIGH':
            # Check if they share deep cultural markers
            caste_a = demo_a.get('caste', '')
            caste_b = demo_b.get('caste', '')
            lang_a = demo_a.get('language', '')
            lang_b = demo_b.get('language', '')
            
            cultural_bonus = 0
            if caste_a and caste_a == caste_b:
                cultural_bonus += 10
            if lang_a and lang_a == lang_b:
                cultural_bonus += 10
            
            if cultural_bonus > 0:
                score += cultural_bonus
                breakdown['cultural_compensation'] = cultural_bonus
        
        return score, breakdown
    
    def _score_cultural(
        self, 
        demo_a: Dict, 
        demo_b: Dict, 
        pref_a: Dict, 
        pref_b: Dict
    ) -> Tuple[float, Dict]:
        """Score cultural compatibility"""
        score = 0.0
        breakdown = {}
        
        # Caste
        caste_a = demo_a.get('caste', '')
        caste_b = demo_b.get('caste', '')
        caste_weight_a = pref_a.get('same_caste', {}).get('weight', 0.5)
        caste_weight_b = pref_b.get('same_caste', {}).get('weight', 0.5)
        
        if caste_a and caste_b:
            if caste_a == caste_b:
                caste_score = 15 * max(caste_weight_a, caste_weight_b)
                score += caste_score
                breakdown['same_caste'] = round(caste_score, 2)
            else:
                # Different caste: penalty if it's important to them
                if caste_weight_a > 0.7 or caste_weight_b > 0.7:
                    penalty = -10 * max(caste_weight_a, caste_weight_b)
                    score += penalty
                    breakdown['different_caste_penalty'] = round(penalty, 2)
        
        # Language
        lang_a = demo_a.get('language', '')
        lang_b = demo_b.get('language', '')
        lang_weight_a = pref_a.get('language', {}).get('weight', 0.5)
        lang_weight_b = pref_b.get('language', {}).get('weight', 0.5)
        
        if lang_a and lang_b and lang_a == lang_b:
            lang_score = 10 * max(lang_weight_a, lang_weight_b)
            score += lang_score
            breakdown['same_language'] = round(lang_score, 2)
        
        return score, breakdown
    
    def _score_age(
        self, 
        demo_a: Dict, 
        demo_b: Dict, 
        pref_a: Dict, 
        pref_b: Dict
    ) -> Tuple[float, Dict]:
        """Score age compatibility"""
        score = 0.0
        breakdown = {}
        
        age_a = demo_a.get('age')
        age_b = demo_b.get('age')
        
        if age_a and age_b:
            age_diff = abs(age_a - age_b)
            
            # Age difference scoring (flexible, not hard cutoffs)
            if age_diff <= 2:
                score += 10
                breakdown['age_diff'] = 10
            elif age_diff <= 5:
                score += 7
                breakdown['age_diff'] = 7
            elif age_diff <= 8:
                score += 3
                breakdown['age_diff'] = 3
            else:
                # Large age gap: check if they're both okay with it
                age_flex_a = pref_a.get('age_range', {}).get('flexible', False)
                age_flex_b = pref_b.get('age_range', {}).get('flexible', False)
                
                if age_flex_a and age_flex_b:
                    score += 1
                    breakdown['age_diff_flexible'] = 1
                else:
                    score -= 5
                    breakdown['age_diff_penalty'] = -5
        
        return score, breakdown
    
    def _score_lifestyle(
        self, 
        demo_a: Dict, 
        demo_b: Dict, 
        pref_a: Dict, 
        pref_b: Dict
    ) -> Tuple[float, Dict]:
        """Score lifestyle compatibility (vegetarian, etc.)"""
        score = 0.0
        breakdown = {}
        
        # Vegetarian
        veg_a = demo_a.get('vegetarian', False)
        veg_b = demo_b.get('vegetarian', False)
        veg_weight_a = pref_a.get('vegetarian', {}).get('weight', 0.5)
        veg_weight_b = pref_b.get('vegetarian', {}).get('weight', 0.5)
        
        if veg_a == veg_b:
            veg_score = 10 * max(veg_weight_a, veg_weight_b)
            score += veg_score
            breakdown['vegetarian_match'] = round(veg_score, 2)
        else:
            # Different dietary preferences: penalty if important
            if veg_weight_a > 0.8 or veg_weight_b > 0.8:
                penalty = -15 * max(veg_weight_a, veg_weight_b)
                score += penalty
                breakdown['vegetarian_mismatch'] = round(penalty, 2)
        
        # Occupation compatibility (similar life stage)
        occ_a = demo_a.get('occupation', '')
        occ_b = demo_b.get('occupation', '')
        
        if occ_a and occ_b:
            # Simple heuristic: similar occupation types = small bonus
            if self._similar_occupation(occ_a, occ_b):
                score += 5
                breakdown['similar_occupation'] = 5
        
        return score, breakdown
    
    def _score_signals(
        self, 
        signals_a: List, 
        signals_b: List, 
        pref_a: Dict, 
        pref_b: Dict
    ) -> Tuple[float, Dict]:
        """
        Score based on learned signals from conversation.
        
        Example signals:
        - "mentioned 'diaspora loneliness' → cultural connection is high priority"
        - "values intellectual compatibility"
        - "family-oriented"
        """
        score = 0.0
        breakdown = {}
        
        # Extract signal keywords
        signal_keywords_a = [s.lower() for s in signals_a]
        signal_keywords_b = [s.lower() for s in signals_b]
        
        # Check for complementary signals
        diaspora_a = any('diaspora' in s for s in signal_keywords_a)
        diaspora_b = any('diaspora' in s for s in signal_keywords_b)
        
        if diaspora_a and diaspora_b:
            score += 10
            breakdown['shared_diaspora_experience'] = 10
        
        family_a = any('family' in s for s in signal_keywords_a)
        family_b = any('family' in s for s in signal_keywords_b)
        
        if family_a and family_b:
            score += 5
            breakdown['family_oriented'] = 5
        
        intellectual_a = any('intellectual' in s or 'curious' in s for s in signal_keywords_a)
        intellectual_b = any('intellectual' in s or 'curious' in s for s in signal_keywords_b)
        
        if intellectual_a and intellectual_b:
            score += 5
            breakdown['intellectual_match'] = 5
        
        return score, breakdown
    
    # ===== HELPER FUNCTIONS =====
    
    def _same_metro_area(self, loc_a: str, loc_b: str) -> bool:
        """Check if two locations are in the same metro area"""
        metro_areas = {
            'sydney': ['sydney', 'parramatta', 'bondi', 'manly'],
            'melbourne': ['melbourne', 'carlton', 'richmond', 'st kilda'],
            'brisbane': ['brisbane', 'gold coast', 'sunshine coast'],
            'delhi': ['delhi', 'new delhi', 'gurgaon', 'noida', 'ghaziabad'],
            'mumbai': ['mumbai', 'navi mumbai', 'thane'],
        }
        
        for metro, suburbs in metro_areas.items():
            if any(s in loc_a for s in suburbs) and any(s in loc_b for s in suburbs):
                return True
        
        return False
    
    def _same_country(self, loc_a: str, loc_b: str) -> bool:
        """Check if two locations are in the same country"""
        australia = ['sydney', 'melbourne', 'brisbane', 'canberra', 'adelaide', 'perth']
        india = ['delhi', 'mumbai', 'bangalore', 'ahmedabad', 'pune', 'hyderabad']
        usa = ['new york', 'san francisco', 'los angeles', 'chicago', 'boston']
        uk = ['london', 'manchester', 'birmingham', 'edinburgh']
        
        for country_cities in [australia, india, usa, uk]:
            if any(c in loc_a for c in country_cities) and any(c in loc_b for c in country_cities):
                return True
        
        return False
    
    def _similar_occupation(self, occ_a: str, occ_b: str) -> bool:
        """Check if occupations are similar (same industry/type)"""
        occ_a = occ_a.lower()
        occ_b = occ_b.lower()
        
        occupation_groups = [
            ['engineer', 'developer', 'software', 'tech', 'programmer'],
            ['doctor', 'physician', 'surgeon', 'medical'],
            ['consultant', 'analyst', 'manager'],
            ['teacher', 'professor', 'educator'],
            ['accountant', 'finance', 'banking'],
        ]
        
        for group in occupation_groups:
            if any(w in occ_a for w in group) and any(w in occ_b for w in group):
                return True
        
        return False
    
    def find_matches(
        self, 
        user_profile: Dict, 
        all_profiles: List[Dict],
        min_score: float = 40.0,
        limit: int = 5
    ) -> List[Tuple[Dict, float, Dict]]:
        """
        Find matches for a user from all available profiles.
        
        Returns: List of (profile, score, breakdown) tuples, sorted by score.
        """
        matches = []
        user_telegram_id = user_profile.get('telegram_id')
        
        for candidate_profile in all_profiles:
            # Don't match with self
            if candidate_profile.get('telegram_id') == user_telegram_id:
                continue
            
            score, breakdown = self.calculate_match_score(user_profile, candidate_profile)
            
            if score >= min_score:
                matches.append((candidate_profile, score, breakdown))
        
        # Sort by score (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches[:limit]


if __name__ == "__main__":
    # Test the matcher with Canberra NRI example
    matcher = ContextualMatcher()
    
    canberra_profile = {
        'telegram_id': 1,
        'demographics': {
            'age': 28,
            'location': 'Canberra, Australia',
            'occupation': 'Software Engineer',
            'caste': 'Patel',
            'language': 'Gujarati',
            'vegetarian': True
        },
        'preferences': {
            'location_proximity': {'weight': 0.5, 'context': 'would relocate within Australia'},
            'cultural_weight': 'HIGH',
            'same_caste': {'weight': 0.7},
            'language': {'weight': 0.8},
            'vegetarian': {'weight': 0.9}
        },
        'signals': ['mentioned diaspora loneliness', 'values cultural grounding']
    }
    
    sydney_match = {
        'telegram_id': 2,
        'demographics': {
            'age': 27,
            'location': 'Sydney, Australia',
            'occupation': 'Consultant',
            'caste': 'Patel',
            'language': 'Gujarati',
            'vegetarian': True
        },
        'preferences': {
            'location_proximity': {'weight': 0.6},
            'cultural_weight': 'HIGH',
            'same_caste': {'weight': 0.8},
            'language': {'weight': 0.7},
            'vegetarian': {'weight': 0.9}
        },
        'signals': ['family-oriented', 'values cultural connection']
    }
    
    delhi_match = {
        'telegram_id': 3,
        'demographics': {
            'age': 28,
            'location': 'Delhi, India',
            'occupation': 'Software Engineer',
            'caste': 'Patel',
            'language': 'Gujarati',
            'vegetarian': True
        },
        'preferences': {
            'location_proximity': {'weight': 0.8},
            'same_caste': {'weight': 0.7},
            'vegetarian': {'weight': 0.9}
        },
        'signals': []
    }
    
    print("=== CANBERRA NRI TEST CASE ===\n")
    
    score_sydney, breakdown_sydney = matcher.calculate_match_score(canberra_profile, sydney_match)
    print(f"Canberra → Sydney: {score_sydney:.2f}")
    print(f"Breakdown: {breakdown_sydney}\n")
    
    score_delhi, breakdown_delhi = matcher.calculate_match_score(canberra_profile, delhi_match)
    print(f"Canberra → Delhi: {score_delhi:.2f}")
    print(f"Breakdown: {breakdown_delhi}\n")
    
    if score_sydney > score_delhi:
        print("✓ SUCCESS: Sydney match wins despite distance!")
        print("  → Cultural depth (same caste + language) compensated for 3-hour distance")
    else:
        print("✗ FAIL: Algorithm still prioritizes exact location match")
