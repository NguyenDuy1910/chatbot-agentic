# Ask API Documentation

The Ask API provides intelligent question-answering capabilities with intent classification and routing to appropriate workflows.

## Endpoints

### POST `/api/v1/ask`

Submit a question to the AI assistant.

**Request Body:**
```json
{
  "query": "What is the total revenue for Q1 2024?",
  "project_id": "project-123",
  "histories": [
    {
      "sql": "SELECT * FROM sales WHERE year = 2023",
      "question": "Show me sales from 2023"
    }
  ],
  "configurations": {
    "language": "English",
    "timezone": {
      "name": "UTC"
    }
  },
  "ignore_sql_generation_reasoning": false,
  "enable_column_pruning": false,
  "use_dry_plan": false,
  "allow_dry_plan_fallback": true,
  "custom_instruction": null
}
```

**Response:**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### GET `/api/v1/ask/{query_id}`

Get the result of a previously submitted question.

**Response:**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "finished",
  "intent": "TEXT_TO_SQL",
  "rephrased_question": "What is the total revenue for Q1 2024?",
  "intent_reasoning": "User is asking for aggregated data from database",
  "confidence_score": 0.95,
  "sql": "SELECT SUM(revenue) FROM sales WHERE quarter = 'Q1' AND year = 2024",
  "sql_results": {
    "columns": ["total_revenue"],
    "rows": [[1500000]]
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Values:**
- `understanding`: Initial processing
- `classifying`: Classifying intent
- `searching`: Searching for relevant data
- `planning`: Planning SQL generation
- `generating`: Generating SQL
- `correcting`: Correcting SQL errors
- `finished`: Query completed successfully
- `failed`: Query failed
- `stopped`: Query was stopped by user

### POST `/api/v1/ask/{query_id}/stop`

Stop a running query.

**Response:**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Intent Types

The Ask service automatically classifies queries into different intents:

### TEXT_TO_SQL
Queries that require SQL generation and database access.
- Example: "What is the total revenue for Q1 2024?"
- Workflow: SQL Processing Graph

### GENERAL
General questions about data or the system.
- Example: "How do I interpret this data?"
- Workflow: Assistance & Visualization Graph

### USER_GUIDE
Questions about how to use the system.
- Example: "How do I create a new report?"
- Workflow: Assistance & Visualization Graph

### MISLEADING_QUERY
Unclear or ambiguous queries that need clarification.
- Example: "Show me the thing from yesterday"
- Workflow: Assistance & Visualization Graph

## Usage Example

### Python
```python
import requests
import time

# Submit question
response = requests.post(
    "http://localhost:8000/api/v1/ask",
    json={
        "query": "What is the total revenue for Q1 2024?",
        "project_id": "project-123",
        "configurations": {
            "language": "English"
        }
    },
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

query_id = response.json()["query_id"]

# Poll for results
while True:
    result = requests.get(
        f"http://localhost:8000/api/v1/ask/{query_id}",
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    ).json()
    
    if result["status"] in ["finished", "failed", "stopped"]:
        print(result)
        break
    
    time.sleep(1)
```

### JavaScript
```javascript
// Submit question
const response = await fetch('http://localhost:8000/api/v1/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  body: JSON.stringify({
    query: 'What is the total revenue for Q1 2024?',
    project_id: 'project-123',
    configurations: {
      language: 'English'
    }
  })
});

const { query_id } = await response.json();

// Poll for results
const pollResult = async () => {
  const result = await fetch(`http://localhost:8000/api/v1/ask/${query_id}`, {
    headers: { 'Authorization': 'Bearer YOUR_TOKEN' }
  }).then(r => r.json());
  
  if (['finished', 'failed', 'stopped'].includes(result.status)) {
    console.log(result);
  } else {
    setTimeout(pollResult, 1000);
  }
};

pollResult();
```

## Error Handling

All endpoints return standard HTTP status codes:
- `200 OK`: Request successful
- `404 Not Found`: Query not found or expired
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Ask service not initialized

Error responses include a detail message:
```json
{
  "detail": "Query not found or expired"
}
```

