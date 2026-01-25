# Quick Start: Ask API

## Start the Server

```bash
cd finx-ai-service
python main.py
```

The server will start on `http://localhost:8000` (or the configured port).

## Access API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Test the API

### 1. Get Authentication Token

First, authenticate to get a token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/signin \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'
```

Save the token from the response.

### 2. Submit a Question

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "What is the total revenue for Q1 2024?",
    "project_id": "project-123",
    "configurations": {
      "language": "English"
    }
  }'
```

Response:
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Get Results

```bash
curl -X GET http://localhost:8000/api/v1/ask/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "finished",
  "intent": "TEXT_TO_SQL",
  "rephrased_question": "What is the total revenue for Q1 2024?",
  "sql": "SELECT SUM(revenue) FROM sales WHERE quarter = 'Q1' AND year = 2024",
  "sql_results": {
    "columns": ["total_revenue"],
    "rows": [[1500000]]
  }
}
```

### 4. Stop a Query (Optional)

```bash
curl -X POST http://localhost:8000/api/v1/ask/550e8400-e29b-41d4-a716-446655440000/stop \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Using Python

```python
import requests
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "YOUR_TOKEN"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Submit question
response = requests.post(
    f"{BASE_URL}/ask",
    json={
        "query": "What is the total revenue for Q1 2024?",
        "project_id": "project-123",
        "configurations": {"language": "English"}
    },
    headers=headers
)

query_id = response.json()["query_id"]
print(f"Query submitted: {query_id}")

# Poll for results
while True:
    result = requests.get(
        f"{BASE_URL}/ask/{query_id}",
        headers=headers
    ).json()
    
    print(f"Status: {result['status']}")
    
    if result["status"] in ["finished", "failed", "stopped"]:
        print("Final result:", result)
        break
    
    time.sleep(1)
```

## Using JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:8000/api/v1";
const TOKEN = "YOUR_TOKEN";

const headers = {
  "Authorization": `Bearer ${TOKEN}`,
  "Content-Type": "application/json"
};

// Submit question
const submitQuestion = async () => {
  const response = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      query: "What is the total revenue for Q1 2024?",
      project_id: "project-123",
      configurations: { language: "English" }
    })
  });
  
  const { query_id } = await response.json();
  console.log("Query submitted:", query_id);
  
  return query_id;
};

// Poll for results
const pollResults = async (queryId: string) => {
  while (true) {
    const response = await fetch(`${BASE_URL}/ask/${queryId}`, { headers });
    const result = await response.json();
    
    console.log("Status:", result.status);
    
    if (["finished", "failed", "stopped"].includes(result.status)) {
      console.log("Final result:", result);
      break;
    }
    
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
};

// Run
const queryId = await submitQuestion();
await pollResults(queryId);
```

## Common Query Examples

### SQL Query
```json
{
  "query": "Show me the top 10 customers by revenue",
  "configurations": { "language": "English" }
}
```

### General Question
```json
{
  "query": "How do I interpret this sales data?",
  "configurations": { "language": "English" }
}
```

### User Guide Question
```json
{
  "query": "How do I create a new dashboard?",
  "configurations": { "language": "English" }
}
```

## Troubleshooting

### Service Unavailable (503)
The ask service is not initialized. Check server logs for workflow initialization errors.

### Query Not Found (404)
The query has expired (TTL: 120 seconds by default) or the query_id is invalid.

### Authentication Required (401)
You need to provide a valid authentication token in the Authorization header.

## Next Steps

- See [ASK_API.md](./ASK_API.md) for complete API documentation
- See [ASK_SERVICE_INTEGRATION.md](./ASK_SERVICE_INTEGRATION.md) for architecture details

