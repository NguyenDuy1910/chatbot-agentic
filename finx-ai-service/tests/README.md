# Tests

This directory contains test files for the finx-ai-service application.

## Test Files

### test_gemini_prompt_agent.py

Tests the Question Recommendation pipeline with Google's Gemini Flash 2.5 model.

**Features tested:**
- Direct Gemini API connection
- Question recommendation pipeline
- Multi-category question generation
- Follow-up question generation based on context
- Multilingual support

**Running the test:**

```bash
# From the project root directory
source venv/bin/activate
python -m tests.test_gemini_prompt_agent
```

**Prerequisites:**
1. Set the `GOOGLE_API_KEY` environment variable:
   ```bash
   export GOOGLE_API_KEY='your-api-key-here'
   ```
   Get your API key from: https://makersuite.google.com/app/apikey

2. Ensure dependencies are installed:
   ```bash
   uv pip install -r requirements.txt
   ```

**Expected Output:**
- ✅ Direct API test successful
- ✅ Pipeline created successfully  
- 📋 Generated questions with categories
- ✅ Follow-up questions based on previous context

## Test Structure

```
tests/
├── __init__.py                      # Package initialization
├── test_gemini_prompt_agent.py     # Gemini prompt agent tests
└── README.md                        # This file
```

## Adding New Tests

When adding new test files:

1. Create test files with the prefix `test_`
2. Import from the parent `src` module using:
   ```python
   sys.path.insert(0, str(Path(__file__).parent.parent))
   ```
3. Use proper logging and error handling
4. Document test prerequisites and expected outcomes
5. Follow async/await patterns for async tests

## Notes

- All tests use the `.env` file from the project root
- Tests can be run individually or as part of a test suite
- Ensure virtual environment is activated before running tests
