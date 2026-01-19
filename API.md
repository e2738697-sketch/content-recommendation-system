# API Documentation

## Content Recommendation System REST API

Complete API reference for the Content Recommendation System.

### Base URL

```
http://localhost:8000
```

### Authentication

Current version supports environment-based authentication through Supabase and Feishu credentials.

---

## Endpoints

### Health Check

**GET** `/health`

Verify that the API server is running.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

### Content Management

#### Upload Content

**POST** `/api/content/upload`

Upload new content to the system.

**Request Body:**
```json
{
  "platform": "xiaohongshu",
  "title": "Product Review",
  "description": "Great product!",
  "author_id": "user123",
  "author_name": "John Doe",
  "like_count": 100,
  "comment_count": 20,
  "collect_count": 50
}
```

**Response:**
```json
{
  "content_id": "uuid-string",
  "status": "uploaded"
}
```

---

#### List Content

**GET** `/api/content/list`

Retrieve list of content with optional filtering.

**Query Parameters:**
- `platform` (optional): Filter by platform
- `limit` (optional): Number of records to return (default: 10)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "data": [...],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

---

### Tagging & Classification

#### Auto Tag Content

**POST** `/api/tagging/auto-tag`

Automatically tag content using AI.

**Request Body:**
```json
{
  "content_id": "uuid-string"
}
```

**Response:**
```json
{
  "content_id": "uuid-string",
  "tags": {
    "category": "beauty",
    "price_band": "premium",
    "scenario": "daily",
    "style": "minimalist",
    "sentiment_score": 0.85
  }
}
```

---

### User Personas

#### Create Persona

**POST** `/api/persona/create`

Create a new user persona for targeting.

**Request Body:**
```json
{
  "name": "Beauty Enthusiast",
  "demographics": {
    "age_range": "25-35",
    "gender": "female"
  },
  "price_sensitivity": 0.6,
  "interaction_pref": "high",
  "interests": {
    "beauty": 1.0,
    "fashion": 0.8,
    "lifestyle": 0.6
  }
}
```

**Response:**
```json
{
  "persona_id": "uuid-string",
  "status": "created"
}
```

---

### Recommendations

#### Get Recommendations

**GET** `/api/recommendations`

Get content recommendations for a specific persona.

**Query Parameters:**
- `persona_id` (required): UUID of the persona
- `limit` (optional): Number of recommendations (default: 20)

**Response:**
```json
{
  "persona_id": "uuid-string",
  "recommendations": [
    {
      "content_id": "uuid-string",
      "score": 0.95,
      "rank": 1
    }
  ]
}
```

---

### Statistics

#### Get System Stats

**GET** `/api/stats`

Retrieve system statistics and metrics.

**Response:**
```json
{
  "total_content": 1000,
  "total_personas": 50,
  "total_recommendations": 5000,
  "last_crawl": "2024-01-01T00:00:00Z",
  "last_tag": "2024-01-01T01:00:00Z"
}
```

---

## Error Responses

### Common Error Codes

- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Resource not found
- `500`: Internal Server Error - Server error

**Error Response Format:**
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "status": 400
}
```

---

## Rate Limiting

Current implementation does not enforce rate limiting in development mode.
Production deployments should implement appropriate rate limiting.

---

## Webhooks

Feishu synchronization triggers are handled automatically based on GitHub Actions schedules.
