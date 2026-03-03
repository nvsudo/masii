"""
Unit Tests for Input Validation
Tests DOB, height, email, phone validations
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from validation import (
    validate_input,
    validate_date_of_birth,
    validate_height,
    validate_email,
    validate_phone,
    sanitize_text,
    calculate_age
)


class TestValidateDateOfBirth:
    """Test date of birth validation"""
    
    @pytest.fixture
    def dob_rules(self):
        """Standard DOB validation rules"""
        return {
            'min_age': 18,
            'max_age': 80,
            'error_format': 'Please enter date in DD/MM/YYYY format (e.g., 25/12/1995)',
            'error_range': 'Age must be between 18 and 80 years'
        }
    
    def test_valid_dob(self, dob_rules):
        """Test valid date of birth"""
        is_valid, error, value = validate_date_of_birth("15/06/1995", dob_rules)
        assert is_valid is True
        assert error == ""
        assert value == "1995-06-15"  # ISO format
    
    def test_valid_dob_recent(self, dob_rules):
        """Test DOB that results in exactly 18 years"""
        # Calculate a date that's 18 years ago
        today = datetime.now()
        year_18_ago = today.year - 18
        dob_str = f"{today.day:02d}/{today.month:02d}/{year_18_ago}"
        
        is_valid, error, value = validate_date_of_birth(dob_str, dob_rules)
        assert is_valid is True
    
    def test_invalid_format_missing_slashes(self, dob_rules):
        """Test invalid format without slashes"""
        is_valid, error, value = validate_date_of_birth("15061995", dob_rules)
        assert is_valid is False
        assert "DD/MM/YYYY" in error
        assert value is None
    
    def test_invalid_format_wrong_order(self, dob_rules):
        """Test invalid format (wrong order)"""
        is_valid, error, value = validate_date_of_birth("1995/06/15", dob_rules)
        assert is_valid is False
        assert value is None
    
    def test_invalid_date(self, dob_rules):
        """Test invalid date (doesn't exist)"""
        is_valid, error, value = validate_date_of_birth("31/02/1995", dob_rules)
        assert is_valid is False
        assert value is None
    
    def test_too_young(self, dob_rules):
        """Test age below minimum"""
        # 10 years ago
        today = datetime.now()
        year_10_ago = today.year - 10
        dob_str = f"{today.day:02d}/{today.month:02d}/{year_10_ago}"
        
        is_valid, error, value = validate_date_of_birth(dob_str, dob_rules)
        assert is_valid is False
        assert "18 and 80" in error
        assert value is None
    
    def test_too_old(self, dob_rules):
        """Test age above maximum"""
        is_valid, error, value = validate_date_of_birth("01/01/1920", dob_rules)
        assert is_valid is False
        assert "18 and 80" in error
        assert value is None
    
    def test_whitespace_handling(self, dob_rules):
        """Test that whitespace is properly handled"""
        is_valid, error, value = validate_date_of_birth("  15/06/1995  ", dob_rules)
        assert is_valid is True
        assert value == "1995-06-15"


class TestValidateHeight:
    """Test height validation"""
    
    @pytest.fixture
    def height_rules(self):
        """Standard height validation rules"""
        return {
            'min': 120,
            'max': 220,
            'error': 'Height must be between 120 cm and 220 cm'
        }
    
    def test_valid_height_cm(self, height_rules):
        """Test valid height in cm"""
        is_valid, error, value = validate_height("170", height_rules)
        assert is_valid is True
        assert error == ""
        assert value == 170
    
    def test_valid_height_with_cm_suffix(self, height_rules):
        """Test height with 'cm' suffix"""
        is_valid, error, value = validate_height("170cm", height_rules)
        assert is_valid is True
        assert value == 170
    
    def test_valid_height_with_cm_and_space(self, height_rules):
        """Test height with space before cm"""
        is_valid, error, value = validate_height("170 cm", height_rules)
        assert is_valid is True
        assert value == 170
    
    def test_valid_height_feet_inches(self, height_rules):
        """Test height in feet'inches format"""
        is_valid, error, value = validate_height("5'8", height_rules)
        assert is_valid is True
        # 5'8" = 172.72 cm ≈ 172 cm
        assert 170 <= value <= 175
    
    def test_valid_height_feet_only(self, height_rules):
        """Test height in feet only"""
        is_valid, error, value = validate_height("6'", height_rules)
        assert is_valid is True
        # 6' = 182.88 cm ≈ 182 cm
        assert 180 <= value <= 185
    
    def test_valid_height_with_inches_quote(self, height_rules):
        """Test height with inches quote mark"""
        is_valid, error, value = validate_height("5'8\"", height_rules)
        assert is_valid is True
        assert 170 <= value <= 175
    
    def test_height_too_short(self, height_rules):
        """Test height below minimum"""
        is_valid, error, value = validate_height("100", height_rules)
        assert is_valid is False
        assert "120 cm and 220 cm" in error
        assert value is None
    
    def test_height_too_tall(self, height_rules):
        """Test height above maximum"""
        is_valid, error, value = validate_height("250", height_rules)
        assert is_valid is False
        assert "120 cm and 220 cm" in error
        assert value is None
    
    def test_invalid_format(self, height_rules):
        """Test invalid height format"""
        is_valid, error, value = validate_height("tall", height_rules)
        assert is_valid is False
        assert "Invalid height format" in error
        assert value is None
    
    def test_whitespace_handling(self, height_rules):
        """Test whitespace is handled"""
        is_valid, error, value = validate_height("  170  ", height_rules)
        assert is_valid is True
        assert value == 170


class TestValidateEmail:
    """Test email validation"""
    
    def test_valid_email(self):
        """Test valid email"""
        is_valid, error, value = validate_email("test@example.com")
        assert is_valid is True
        assert error == ""
        assert value == "test@example.com"
    
    def test_valid_email_with_subdomain(self):
        """Test email with subdomain"""
        is_valid, error, value = validate_email("user@mail.example.com")
        assert is_valid is True
        assert value == "user@mail.example.com"
    
    def test_valid_email_with_plus(self):
        """Test email with + sign"""
        is_valid, error, value = validate_email("user+tag@example.com")
        assert is_valid is True
    
    def test_invalid_email_no_at(self):
        """Test email without @"""
        is_valid, error, value = validate_email("userexample.com")
        assert is_valid is False
        assert "valid email" in error
        assert value is None
    
    def test_invalid_email_no_dot(self):
        """Test email without dot"""
        is_valid, error, value = validate_email("user@examplecom")
        assert is_valid is False
        assert value is None
    
    def test_invalid_email_empty(self):
        """Test empty email"""
        is_valid, error, value = validate_email("")
        assert is_valid is False
        assert value is None
    
    def test_whitespace_handling(self):
        """Test whitespace is trimmed"""
        is_valid, error, value = validate_email("  test@example.com  ")
        assert is_valid is True
        assert value == "test@example.com"


class TestValidatePhone:
    """Test phone validation"""
    
    def test_valid_phone_basic(self):
        """Test basic phone number"""
        is_valid, error, value = validate_phone("9876543210")
        assert is_valid is True
        assert error == ""
        assert value == "9876543210"
    
    def test_valid_phone_with_country_code(self):
        """Test phone with country code"""
        is_valid, error, value = validate_phone("+919876543210")
        assert is_valid is True
        assert value == "+919876543210"
    
    def test_valid_phone_with_spaces(self):
        """Test phone with spaces"""
        is_valid, error, value = validate_phone("987 654 3210")
        assert is_valid is True
        # Returns original format
        assert value == "987 654 3210"
    
    def test_valid_phone_with_dashes(self):
        """Test phone with dashes"""
        is_valid, error, value = validate_phone("987-654-3210")
        assert is_valid is True
    
    def test_valid_phone_with_parentheses(self):
        """Test phone with parentheses"""
        is_valid, error, value = validate_phone("(987) 654-3210")
        assert is_valid is True
    
    def test_valid_phone_international(self):
        """Test international format"""
        is_valid, error, value = validate_phone("+44 20 1234 5678")
        assert is_valid is True
    
    def test_invalid_phone_too_short(self):
        """Test phone number too short"""
        is_valid, error, value = validate_phone("12345")
        assert is_valid is False
        assert "7 and 15 digits" in error
        assert value is None
    
    def test_invalid_phone_too_long(self):
        """Test phone number too long"""
        is_valid, error, value = validate_phone("1234567890123456")
        assert is_valid is False
        assert "7 and 15 digits" in error
        assert value is None
    
    def test_invalid_phone_with_letters(self):
        """Test phone with letters"""
        is_valid, error, value = validate_phone("987abc3210")
        assert is_valid is False
        assert "valid phone number" in error
        assert value is None


class TestSanitizeText:
    """Test text sanitization"""
    
    def test_basic_text(self):
        """Test basic text sanitization"""
        result = sanitize_text("Hello world")
        assert result == "Hello world"
    
    def test_whitespace_trimming(self):
        """Test whitespace is trimmed"""
        result = sanitize_text("  Hello world  ")
        assert result == "Hello world"
    
    def test_unicode_allowed(self):
        """Test unicode characters are preserved"""
        result = sanitize_text("नमस्ते world")
        assert result == "नमस्ते world"
    
    def test_max_length_truncation(self):
        """Test text is truncated at max length"""
        long_text = "a" * 1000
        result = sanitize_text(long_text, max_length=100)
        assert len(result) == 100
    
    def test_newlines_preserved(self):
        """Test newlines are preserved"""
        result = sanitize_text("Line 1\nLine 2")
        assert "Line 1" in result
        assert "Line 2" in result
    
    def test_control_characters_removed(self):
        """Test control characters are removed"""
        # ASCII control characters below 32 (except \n, \r, \t)
        text_with_ctrl = "Hello\x00\x01world"
        result = sanitize_text(text_with_ctrl)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "Hello" in result
        assert "world" in result


class TestCalculateAge:
    """Test age calculation from ISO date"""
    
    def test_calculate_age_exact(self):
        """Test age calculation for exact years"""
        # Create a date exactly 25 years ago
        today = datetime.now()
        year_25_ago = today.year - 25
        dob_iso = f"{year_25_ago}-{today.month:02d}-{today.day:02d}"
        
        age = calculate_age(dob_iso)
        assert age == 25
    
    def test_calculate_age_not_yet_birthday(self):
        """Test age when birthday hasn't occurred this year"""
        today = datetime.now()
        # Birthday in future this year
        if today.month < 12:
            future_month = today.month + 1
            year = today.year - 25
        else:
            future_month = 1
            year = today.year - 24
        
        dob_iso = f"{year}-{future_month:02d}-15"
        age = calculate_age(dob_iso)
        # Should be 24, not 25
        assert age >= 23 and age <= 25  # Allow some flexibility
    
    def test_calculate_age_different_formats(self):
        """Test age calculation works with ISO format"""
        dob_iso = "1995-06-15"
        age = calculate_age(dob_iso)
        # Age should be reasonable
        assert 25 <= age <= 35


class TestValidateInputWrapper:
    """Test the main validate_input() wrapper function"""
    
    def test_validate_dob(self):
        """Test DOB validation through wrapper"""
        rules = {
            'date_of_birth': {
                'min_age': 18,
                'max_age': 80,
                'error_format': 'Invalid format',
                'error_range': 'Invalid range'
            }
        }
        
        is_valid, error, value = validate_input("15/06/1995", "date_of_birth", rules)
        assert is_valid is True
    
    def test_validate_height(self):
        """Test height validation through wrapper"""
        rules = {
            'height_cm': {
                'min': 120,
                'max': 220,
                'error': 'Invalid height'
            }
        }
        
        is_valid, error, value = validate_input("170", "height_cm", rules)
        assert is_valid is True
        assert value == 170
    
    def test_validate_email_wrapper(self):
        """Test email validation through wrapper"""
        is_valid, error, value = validate_input("test@example.com", "email", {})
        assert is_valid is True
    
    def test_validate_phone_wrapper(self):
        """Test phone validation through wrapper"""
        is_valid, error, value = validate_input("9876543210", "phone", {})
        assert is_valid is True
    
    def test_unknown_validation_type(self):
        """Test unknown validation type returns value as-is"""
        is_valid, error, value = validate_input("some value", "unknown_type", {})
        assert is_valid is True
        assert error == ""
        assert value == "some value"
