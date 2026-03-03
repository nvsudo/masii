# JODI Bot Test Suite

Comprehensive test suite for JODI Telegram onboarding bot.

## Quick Start

```bash
# Install dependencies
pip install pytest pytest-asyncio pytest-mock

# Run all tests
cd /Users/nikunjvora/clawd/ventures/jodi/bot
python3 -m pytest tests/ -v

# Run specific test module
python3 -m pytest tests/test_conditional_logic.py -v
```

## Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── test_conditional_logic.py      # 50 tests - User paths and branching
├── test_validation.py             # 67 tests - Input validation
├── test_onboarding_handler.py     # 32 tests - Question flow
├── test_db_adapter.py             # 32 tests - Database operations
├── test_config.py                 # ~50 tests - Config validation
├── requirements-test.txt          # Test dependencies
└── TEST_REPORT.md                 # Detailed test report
```

## Test Coverage

### 1. Conditional Logic (50 tests)
- ✅ All 4 user paths (Hindu/Muslim/NRI/Divorced)
- ✅ Skip logic for all conditional questions
- ✅ Section progression
- ✅ Completion percentage

### 2. Validation (67 tests)
- ✅ Date of birth (DD/MM/YYYY → ISO)
- ✅ Height (cm, feet'inches)
- ✅ Email validation
- ✅ Phone validation
- ✅ Text sanitization

### 3. Onboarding Handler (32 tests)
- ✅ Intro flow
- ✅ Question display
- ✅ Button callbacks
- ✅ Multi-select logic
- ✅ Text input handling

### 4. Database Adapter (32 tests)
- ✅ Session management
- ✅ User operations
- ✅ Save answers
- ✅ Photo operations
- ✅ Profile completion

### 5. Config Validation (~50 tests)
- ✅ All 77 questions loadable
- ✅ Required fields present
- ✅ Valid question types
- ✅ Dynamic options

## Test Results

**Status:** ✅ ALL 181 TESTS PASSING

```
============================= 181 passed in 0.23s ==============================
```

## Running Specific Test Classes

```bash
# Conditional logic skip rules
pytest tests/test_conditional_logic.py::TestShouldSkipQuestion -v

# Validation tests
pytest tests/test_validation.py::TestValidateDateOfBirth -v

# Onboarding flow
pytest tests/test_onboarding_handler.py::TestQuestionFlow -v

# Database operations
pytest tests/test_db_adapter.py::TestSessionManagement -v

# Config validation
pytest tests/test_config.py::TestQuestionConfiguration -v
```

## Fixtures (conftest.py)

- `mock_db` - Mock database adapter
- `sample_session` - Sample onboarding session
- `mock_update` - Mock Telegram Update object
- `mock_context` - Mock Telegram Context object
- `mock_callback_query` - Mock CallbackQuery object
- `hindu_never_married_india` - Sample Hindu user answers
- `muslim_never_married_india` - Sample Muslim user answers
- `nri_hindu` - Sample NRI user answers
- `divorced_with_children` - Sample divorced user answers

## Adding New Tests

1. Create test file: `tests/test_<module>.py`
2. Import fixtures from `conftest.py`
3. Use pytest decorators:
   - `@pytest.mark.asyncio` for async tests
   - `@pytest.fixture` for test fixtures
4. Follow naming convention: `test_<description>`
5. Run tests: `pytest tests/test_<module>.py -v`

## Test Categories

### Unit Tests
- `test_conditional_logic.py`
- `test_validation.py`
- `test_db_adapter.py`

### Integration Tests
- `test_onboarding_handler.py`

### Config Validation
- `test_config.py`

## CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install -r tests/requirements-test.txt
      - run: pytest tests/ -v
```

## Troubleshooting

### Import Errors
Ensure `pythonpath = .` is set in `pytest.ini`

### Async Test Errors
Install `pytest-asyncio`: `pip install pytest-asyncio`

### Mock Errors
Install `pytest-mock`: `pip install pytest-mock`

## Documentation

See `TEST_REPORT.md` for:
- Detailed test breakdown
- Coverage analysis
- Known issues
- Recommendations

## Maintenance

- Run tests before every commit
- Update tests when modifying conditional logic
- Add tests for new questions
- Keep fixtures updated with schema changes

---

**Last Updated:** 2025-02-21  
**Test Count:** 181  
**Status:** ✅ All Passing
