#!/bin/bash
# Health AI Consultant API - curl examples
# This script contains example curl commands for interacting with the Health AI Consultant API
# Usage: Run individual commands or source this file to use the functions

# Base URL for the API
API_BASE_URL="http://localhost:5000"

# Set text colors for better readability
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print a header for each command
print_header() {
  echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Health check endpoint
health_check() {
  print_header "Health Check"
  curl -s "${API_BASE_URL}/health" | json_pp
}

# Chat with the AI (non-streaming)
chat_question() {
  local question="$1"
  local conversation_id="$2"
  
  print_header "Chat Question: $question"
  
  if [ -z "$conversation_id" ]; then
    # No conversation ID provided
    curl -s -X POST \
      "${API_BASE_URL}/api/chat" \
      -H "Content-Type: application/json" \
      -d "{\"question\": \"$question\", \"stream\": false}" | json_pp
  else
    # With conversation ID
    curl -s -X POST \
      "${API_BASE_URL}/api/chat" \
      -H "Content-Type: application/json" \
      -d "{\"question\": \"$question\", \"conversation_id\": \"$conversation_id\", \"stream\": false}" | json_pp
  fi
}

# Chat with the AI (streaming)
chat_question_stream() {
  local question="$1"
  local conversation_id="$2"
  
  print_header "Chat Question (Streaming): $question"
  
  if [ -z "$conversation_id" ]; then
    # No conversation ID provided
    curl -N -X POST \
      "${API_BASE_URL}/api/chat" \
      -H "Content-Type: application/json" \
      -d "{\"question\": \"$question\", \"stream\": true}"
  else
    # With conversation ID
    curl -N -X POST \
      "${API_BASE_URL}/api/chat" \
      -H "Content-Type: application/json" \
      -d "{\"question\": \"$question\", \"conversation_id\": \"$conversation_id\", \"stream\": true}"
  fi
  
  echo -e "\n"
}

# Upload a document
upload_document() {
  local file_path="$1"
  
  if [ ! -f "$file_path" ]; then
    echo -e "${RED}File not found: $file_path${NC}"
    return 1
  fi
  
  print_header "Upload Document: $(basename "$file_path")"
  
  curl -s -X POST \
    "${API_BASE_URL}/api/documents/upload" \
    -F "file=@$file_path" | json_pp
}

# List all documents
list_documents() {
  print_header "List Documents"
  curl -s "${API_BASE_URL}/api/documents/" | json_pp
}

# Get document details
get_document() {
  local document_id="$1"
  
  print_header "Get Document: $document_id"
  curl -s "${API_BASE_URL}/api/documents/$document_id" | json_pp
}

# Delete a document
delete_document() {
  local document_id="$1"
  
  print_header "Delete Document: $document_id"
  curl -s -X DELETE "${API_BASE_URL}/api/documents/$document_id" | json_pp
}

# Run a full example workflow
run_example_workflow() {
  print_header "Running Example Workflow"
  
  # Check API health
  echo -e "${GREEN}Checking API health...${NC}"
  health_check
  
  # Ask a question without context
  echo -e "\n${GREEN}Asking a question without context...${NC}"
  chat_question "What are the benefits of regular exercise?"
  
  # Ask a follow-up question in the same conversation
  echo -e "\n${GREEN}Asking a follow-up question...${NC}"
  chat_question "How often should I exercise?" "example_conversation"
  
  # Upload a document (if provided)
  if [ -n "$1" ]; then
    echo -e "\n${GREEN}Uploading a document...${NC}"
    upload_output=$(upload_document "$1")
    echo "$upload_output"
    
    # Extract document ID from upload response (requires jq)
    if command -v jq &> /dev/null; then
      document_id=$(echo "$upload_output" | jq -r '.document_id')
      
      if [ -n "$document_id" ] && [ "$document_id" != "null" ]; then
        # List all documents
        echo -e "\n${GREEN}Listing all documents...${NC}"
        list_documents
        
        # Get document details
        echo -e "\n${GREEN}Getting document details...${NC}"
        get_document "$document_id"
        
        # Ask a question about the document
        echo -e "\n${GREEN}Asking a question about the document...${NC}"
        chat_question "Can you summarize the document I just uploaded?"
        
        # Delete the document
        echo -e "\n${GREEN}Deleting the document...${NC}"
        delete_document "$document_id"
      fi
    else
      echo -e "${RED}jq not installed, skipping document operations${NC}"
    fi
  else
    echo -e "\n${RED}No document path provided, skipping document operations${NC}"
  fi
}

# Show usage information
show_usage() {
  echo -e "${BLUE}Health AI Consultant API - curl examples${NC}"
  echo -e "Usage:"
  echo -e "  source api_curl_examples.sh  # Load all functions"
  echo -e ""
  echo -e "Available commands:"
  echo -e "  health_check                                  # Check API health"
  echo -e "  chat_question \"question\" [conversation_id]    # Ask a question"
  echo -e "  chat_question_stream \"question\" [conversation_id]  # Ask a question with streaming"
  echo -e "  upload_document path/to/file.pdf              # Upload a document"
  echo -e "  list_documents                                # List all documents"
  echo -e "  get_document document_id                      # Get document details"
  echo -e "  delete_document document_id                   # Delete a document"
  echo -e "  run_example_workflow [path/to/file.pdf]       # Run a full example workflow"
}

# If script is being executed directly (not sourced), show usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  show_usage
fi
