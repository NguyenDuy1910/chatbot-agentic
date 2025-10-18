# Pipeline Configuration Guide

This directory contains configuration files for the FinX AI Service pipeline with different setups.

## Configuration Files

### 1. config.example.yaml
Full-featured configuration with all available pipelines using Google Gemini models.

**Features:**
- Complete pipeline definitions for all use cases
- Google Gemini 2.0 Flash for LLM tasks
- Google text-embedding-004 for embeddings
- Qdrant vector store integration
- All retrieval, generation, and analysis pipelines

**Use Case:** Production deployment with full capabilities

### 2. config.gemini.minimal.yaml
Minimal configuration focused on core indexing functionality.

**Features:**
- Essential indexing pipelines only
- Simplified settings
- Quick setup for development

**Use Case:** Development and testing of indexing features

## Setup Instructions

### Prerequisites

1. Install required packages:
```bash
pip install google-ai-haystack qdrant-client litellm
```

2. Set up Google API Key:
```bash
export GOOGLE_API_KEY='your-api-key-here'
```
Get your key from: https://makersuite.google.com/app/apikey

3. Start Qdrant (if using local instance):
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Configuration Setup

1. Choose a configuration file based on your needs
2. Copy to `config.yaml`:
```bash
cp config.example.yaml config.yaml
# OR
cp config.gemini.minimal.yaml config.yaml
```

3. Customize settings:
   - Update model names if needed
   - Adjust timeout values
   - Configure endpoints for your environment
   - Set embedding dimensions correctly

### Using the Configuration

The pipeline will automatically load `config.yaml` from:
1. Current working directory
2. `~/.wrenai/config.yaml` (user home directory)

## Configuration Structure

### LLM Provider
```yaml
type: llm
provider: litellm_llm  # or google_genai
models:
  - model: gemini/gemini-2.0-flash-exp
    alias: default
    timeout: 600
    kwargs:
      temperature: 0
      max_tokens: 8192
```

### Embedder Provider
```yaml
type: embedder
provider: litellm_embedder  # or google_genai_embedder
models:
  - model: text-embedding-004
    alias: default
    timeout: 600
```

### Document Store
```yaml
type: document_store
provider: qdrant
location: http://localhost:6333
embedding_model_dim: 768  # IMPORTANT: Match your embedding model
timeout: 120
recreate_index: false
```

### Pipeline Definitions
```yaml
type: pipeline
pipes:
  - name: db_schema_indexing
    embedder: litellm_embedder.default
    document_store: qdrant
  
  - name: question_recommendation
    llm: litellm_llm.default
```

## Available Models

### Google Gemini LLM Models
- `gemini-2.0-flash-exp` - Fast, efficient model (recommended)
- `gemini-1.5-pro` - More capable, slower
- `gemini-1.5-flash` - Balance of speed and capability

### Google Embedding Models
- `text-embedding-004` - 768 dimensions (recommended)
- `embedding-001` - 768 dimensions

## Embedding Model Dimensions

**CRITICAL:** The `embedding_model_dim` in document store configuration MUST match your embedding model:

| Model | Dimensions |
|-------|------------|
| text-embedding-004 | 768 |
| embedding-001 | 768 |
| nomic-embed-text | 768 |

## Pipeline Types

### Indexing Pipelines
- `db_schema_indexing` - Index database schemas
- `historical_question_indexing` - Index past questions
- `table_description_indexing` - Index table descriptions
- `sql_pairs_indexing` - Index SQL query pairs
- `instructions_indexing` - Index custom instructions

### Retrieval Pipelines
- `db_schema_retrieval` - Retrieve relevant schemas
- `historical_question_retrieval` - Find similar past questions
- `sql_pairs_retrieval` - Find similar SQL patterns

### Generation Pipelines
- `sql_generation` - Generate SQL queries
- `question_recommendation` - Generate question suggestions
- `chart_generation` - Generate chart configurations

## Environment Variables

Required:
```bash
export GOOGLE_API_KEY='your-key'
```

Optional:
```bash
export LANGFUSE_PUBLIC_KEY='your-key'
export LANGFUSE_SECRET_KEY='your-secret'
export QDRANT_URL='http://localhost:6333'
```

## Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure GOOGLE_API_KEY is set correctly
   - Check key has appropriate permissions

2. **Embedding Dimension Mismatch**
   - Verify embedding_model_dim matches your model
   - Check model documentation for correct dimensions

3. **Qdrant Connection Failed**
   - Ensure Qdrant is running
   - Check connection URL and port

4. **Timeout Errors**
   - Increase timeout values in configuration
   - Check network connectivity

## Examples

### Running DB Schema Indexing

```python
from src.pipelines.indexing.db_schema import DBSchema
from src.core.provider import EmbedderProvider, DocumentStoreProvider

# Load configuration
# Pipeline will automatically use config.yaml

# Create pipeline
pipeline = DBSchema(
    embedder_provider=embedder_provider,
    document_store_provider=document_store_provider,
    column_batch_size=50
)

# Run indexing
result = await pipeline.run(
    mdl_str=json.dumps(mdl_dict),
    project_id="my_project"
)
```

### Running Question Recommendation

```python
from src.pipelines.generation.question_recommendation import QuestionRecommendation

# Create pipeline with Gemini
pipeline = QuestionRecommendation(
    llm_provider=gemini_provider
)

# Generate questions
result = await pipeline.run(
    contexts=schema_contexts,
    language="en",
    max_questions=5,
    max_categories=3
)
```

## Best Practices

1. **Development**: Use minimal configuration for faster iteration
2. **Production**: Use full configuration with monitoring enabled
3. **Testing**: Set `recreate_index: true` to ensure clean state
4. **Monitoring**: Enable Langfuse for tracking and debugging
5. **Logging**: Use appropriate logging level (DEBUG, INFO, WARNING, ERROR)

## Additional Resources

- [Google Gemini Documentation](https://ai.google.dev/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Haystack Documentation](https://haystack.deepset.ai/)
