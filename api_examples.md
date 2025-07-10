# Health AI Consultant API Examples

This document provides examples of how to interact with the Health AI Consultant API using curl commands. These examples can be used for testing or as a reference for frontend integration.

## Health Check

Check if the API is running:

```bash
curl -X GET http://localhost:5000/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "Health AI Consultant API"
}
```

## Chat API

### Basic Chat Request

Send a question to the chat API:

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the benefits of regular exercise?",
    "conversation_id": "test_conversation",
    "stream": false
  }'
```

Expected response:

```json
{
  "answer": "Regular exercise offers numerous health benefits, including improved cardiovascular health, reduced risk of chronic diseases, better weight management, enhanced mental health, and increased energy levels...",
  "citations": [
    "Health Guidelines, Topic: exercise, p. 1"
  ],
  "confidence": 0.85,
  "conversation_id": "test_conversation"
}
```

### Streaming Chat Request

Send a question with streaming enabled:

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the benefits of regular exercise?",
    "conversation_id": "test_conversation",
    "stream": true
  }'
```

This will return a stream of server-sent events (SSE) that can be processed by the frontend.

## Document Management

### Upload Document

Upload a document to the system:

```bash
curl -X POST http://localhost:5000/api/documents/upload \
  -F "file=@/path/to/your/document.pdf"
```

Expected response:

```json
{
  "success": true,
  "document_id": "12345678-1234-5678-1234-567812345678",
  "filename": "document.pdf",
  "metadata": {
    "title": "document.pdf",
    "author": "Unknown",
    "page_count": 5,
    "file_type": "PDF",
    "processed_at": "2023-07-10T21:30:45.123456",
    "chunk_count": 12
  }
}
```

### List Documents

Get a list of all uploaded documents:

```bash
curl -X GET http://localhost:5000/api/documents/
```

Expected response:

```json
{
  "documents": [
    {
      "id": "12345678-1234-5678-1234-567812345678",
      "filename": "document1.pdf",
      "title": "Health Guidelines",
      "author": "John Doe",
      "page_count": 5,
      "file_type": "PDF",
      "processed_at": "2023-07-10T21:30:45.123456",
      "chunk_count": 12
    },
    {
      "id": "87654321-8765-4321-8765-432187654321",
      "filename": "document2.pdf",
      "title": "Nutrition Handbook",
      "author": "Jane Smith",
      "page_count": 10,
      "file_type": "PDF",
      "processed_at": "2023-07-10T22:15:30.654321",
      "chunk_count": 25
    }
  ]
}
```

### Get Document Details

Get details about a specific document:

```bash
curl -X GET http://localhost:5000/api/documents/12345678-1234-5678-1234-567812345678
```

Expected response:

```json
{
  "id": "12345678-1234-5678-1234-567812345678",
  "filename": "document1.pdf",
  "title": "Health Guidelines",
  "author": "John Doe",
  "page_count": 5,
  "file_type": "PDF",
  "processed_at": "2023-07-10T21:30:45.123456",
  "chunk_count": 12
}
```

### Delete Document

Delete a document from the system:

```bash
curl -X DELETE http://localhost:5000/api/documents/12345678-1234-5678-1234-567812345678
```

Expected response:

```json
{
  "success": true,
  "document_id": "12345678-1234-5678-1234-567812345678"
}
```

## Error Handling

All endpoints return appropriate error responses with descriptive messages. For example:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "No file selected",
    "details": ""
  }
}
```

Common error codes:

- `INVALID_REQUEST`: The request was invalid or malformed
- `OLLAMA_CONNECTION_ERROR`: Failed to connect to the Ollama API
- `OLLAMA_GENERATION_ERROR`: Error generating a response from Ollama
- `VECTOR_DB_ERROR`: Error accessing the vector database
- `DOCUMENT_PROCESSING_ERROR`: Error processing a document
- `INTERNAL_SERVER_ERROR`: General server error

## Running the Test Script

A comprehensive test script is provided to verify all API endpoints:

```bash
python test_api.py
```

This will run tests for all endpoints and provide detailed output about the results.
