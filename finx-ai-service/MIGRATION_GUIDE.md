# Migration Guide: SimpleLLMGenerator → LLMService

This guide helps you migrate from `SimpleLLMGenerator` to the new `LLMService`.

## Why Migrate?

The new `LLMService` provides:
- ✅ Better architecture with provider abstraction
- ✅ More robust error handling
- ✅ Additional features (batch processing, conversation history)
- ✅ Better type hints and documentation
- ✅ Easier to extend and maintain
- ✅ Production-ready with comprehensive testing

## Quick Migration

### Before (SimpleLLMGenerator)

```python
from src.workflows.intent_recommendation.llm_helper import SimpleLLMGenerator

# Create generator
llm = SimpleLLMGenerator(
    provider="gemini",
    model="gemini-2.0-flash-exp",
    temperature=0.7
)

# Generate
response = await llm.generate(
    prompt="What is Python?",
    system_prompt="You are a helpful assistant."
)
```

### After (LLMService)

```python
from src.services.llm_service import LLMService

# Create service
service = LLMService.create(
    provider_type="gemini",
    model="gemini-2.0-flash-exp",
    temperature=0.7
)

# Generate (same API!)
response = await service.generate(
    prompt="What is Python?",
    system_prompt="You are a helpful assistant."
)
```

## Step-by-Step Migration

### Step 1: Update Imports

**Old:**
```python
from src.workflows.intent_recommendation.llm_helper import (
    SimpleLLMGenerator,
    create_llm_generator
)
```

**New:**
```python
from src.services.llm_service import LLMService
```

### Step 2: Update Initialization

#### Pattern 1: Basic Initialization

**Old:**
```python
llm = SimpleLLMGenerator(provider="gemini")
```

**New:**
```python
service = LLMService.create(provider_type="gemini")
```

#### Pattern 2: With Model Specification

**Old:**
```python
llm = SimpleLLMGenerator(
    provider="gemini",
    model="gemini-2.0-flash-exp"
)
```

**New:**
```python
service = LLMService.create(
    provider_type="gemini",
    model="gemini-2.0-flash-exp"
)
```

#### Pattern 3: With Parameters

**Old:**
```python
llm = SimpleLLMGenerator(
    provider="openai",
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000
)
```

**New:**
```python
service = LLMService.create(
    provider_type="openai",
    model="gpt-4o-mini",
    temperature=0.7,
    max_tokens=1000
)
```

#### Pattern 4: Factory Function

**Old:**
```python
llm = create_llm_generator(
    provider="gemini",
    model="gemini-2.0-flash-exp"
)
```

**New:**
```python
service = LLMService.create(
    provider_type="gemini",
    model="gemini-2.0-flash-exp"
)
```

### Step 3: Update Generation Calls

The generation API is mostly compatible!

**Old:**
```python
response = await llm.generate(
    prompt="Your question",
    system_prompt="System instructions",
    response_format={"type": "json_object"}
)
```

**New:**
```python
# Same API works!
response = await service.generate(
    prompt="Your question",
    system_prompt="System instructions",
    response_format={"type": "json_object"}
)
```

### Step 4: Update Callable Usage

If you used the callable interface:

**Old:**
```python
result = await llm("Your prompt", system_prompt="Instructions")
text = result["replies"][0]
```

**New:**
```python
# Option 1: Use generate() directly (recommended)
text = await service.generate("Your prompt", system_prompt="Instructions")

# Option 2: Provider still supports callable interface
provider = service.get_provider()
result = await provider("Your prompt", system_prompt="Instructions")
text = result["replies"][0]
```

## Common Migration Patterns

### Pattern: Configuration-Based Setup

**Old:**
```python
config = get_config()
llm = SimpleLLMGenerator(
    provider=config["llm"]["provider"],
    model=config["llm"]["model"],
    temperature=config["llm"]["temperature"]
)
```

**New:**
```python
config = get_config()
service = LLMService.from_config(config["llm"])
```

### Pattern: Class Dependency Injection

**Old:**
```python
class MyNode:
    def __init__(self, llm: SimpleLLMGenerator):
        self.llm = llm
    
    async def process(self, text: str):
        return await self.llm.generate(text)
```

**New:**
```python
class MyNode:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def process(self, text: str):
        return await self.llm_service.generate(text)
```

### Pattern: Multiple Providers

**Old:**
```python
gemini_llm = SimpleLLMGenerator(provider="gemini")
openai_llm = SimpleLLMGenerator(provider="openai")

response1 = await gemini_llm.generate("Prompt 1")
response2 = await openai_llm.generate("Prompt 2")
```

**New:**
```python
gemini_service = LLMService.create("gemini")
openai_service = LLMService.create("openai")

response1 = await gemini_service.generate("Prompt 1")
response2 = await openai_service.generate("Prompt 2")
```

## New Features You Can Use

### 1. Batch Generation

```python
# New capability!
prompts = ["Question 1", "Question 2", "Question 3"]
responses = await service.generate_batch(prompts)
```

### 2. JSON Output

```python
# Simplified JSON generation
data = await service.generate_json(
    "Return user data in JSON",
    system_prompt="Return valid JSON"
)
# Returns parsed dictionary
```

### 3. Conversation History

```python
# New feature for OpenAI
messages = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "Tell me more"}
]
response = await service.generate_with_history(messages)
```

### 4. Model Information

```python
# Get model details
info = service.get_model_info()
print(f"Using {info['model']} with {info['context_window']} token window")
```

## File-by-File Migration Checklist

### For `nodes/classification.py` and similar files:

- [ ] Update imports
- [ ] Update class constructor to accept `LLMService`
- [ ] Update instance variable names (`self.llm` → `self.llm_service`)
- [ ] Test generation calls still work
- [ ] Run unit tests

### For workflow/graph files:

- [ ] Update service initialization in graph setup
- [ ] Pass `LLMService` instances to nodes
- [ ] Update any direct LLM calls
- [ ] Test end-to-end workflows

### For configuration files:

- [ ] Update provider config structure if needed
- [ ] Test config-based initialization
- [ ] Verify all parameters are supported

## Testing Your Migration

### 1. Unit Tests

```python
import pytest
from src.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_migration():
    # Test basic creation
    service = LLMService.create("gemini")
    
    # Test generation
    response = await service.generate("Test prompt")
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Test model info
    info = service.get_model_info()
    assert "model" in info
    assert "context_window" in info
```

### 2. Integration Tests

```python
async def test_workflow_integration():
    # Create service
    service = LLMService.create("gemini", temperature=0.7)
    
    # Test in your workflow
    from src.workflows.your_workflow import YourNode
    
    node = YourNode(llm_service=service)
    result = await node.process("Test input")
    
    assert result is not None
```

### 3. Manual Testing

```bash
# Run the test suite
python -m src.services.test_llm_service

# Try examples
python -m src.services.llm_service_examples
```

## Troubleshooting

### Issue: Import Error

**Error:** `ModuleNotFoundError: No module named 'src.core.providers'`

**Solution:** Ensure the providers package is created:
```bash
ls -la src/core/providers/
# Should show: __init__.py, gemini_provider.py, openai_provider.py, llm_factory.py
```

### Issue: API Key Not Found

**Error:** `ValueError: GOOGLE_API_KEY not found`

**Solution:** Set environment variables:
```bash
export GOOGLE_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

### Issue: Missing Dependencies

**Error:** `ImportError: openai package not installed`

**Solution:** Install required packages:
```bash
pip install google-generativeai openai
```

### Issue: Different Response Format

**Problem:** Code expects `{"replies": [...]}` dict

**Solution:**
```python
# Old code expected:
result = await llm("prompt")
text = result["replies"][0]

# Option 1: Use provider directly
provider = service.get_provider()
result = await provider("prompt")
text = result["replies"][0]

# Option 2: Use generate() (better)
text = await service.generate("prompt")
```

## Backward Compatibility

For a smooth transition, you can keep both systems running:

```python
# In your transition period
try:
    from src.services.llm_service import LLMService
    USE_NEW_SERVICE = True
except ImportError:
    from src.workflows.intent_recommendation.llm_helper import SimpleLLMGenerator
    USE_NEW_SERVICE = False

# Create service
if USE_NEW_SERVICE:
    llm = LLMService.create("gemini")
else:
    llm = SimpleLLMGenerator(provider="gemini")

# Use (works with both)
response = await llm.generate("Your prompt")
```

## Rollback Plan

If you need to rollback:

1. The old `SimpleLLMGenerator` is still available
2. Keep the old imports in your code
3. The files can coexist without conflicts
4. Switch back by reverting imports

## Support

- Check examples: `src/services/llm_service_examples.py`
- Read docs: `src/services/LLM_SERVICE_README.md`
- Run tests: `python -m src.services.test_llm_service`
- Review implementation: `LLM_SERVICE_IMPLEMENTATION.md`

## Summary Checklist

- [ ] Install dependencies (`google-generativeai`, `openai`)
- [ ] Set environment variables (API keys)
- [ ] Update imports in all files
- [ ] Update initialization code
- [ ] Test generation calls work
- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Update documentation
- [ ] Deploy and monitor

Good luck with your migration! 🚀
