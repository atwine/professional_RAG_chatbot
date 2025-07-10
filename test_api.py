"""
Test script for the Health AI Consultant API endpoints.
This script tests both the chat and document upload endpoints.
"""
import os
import sys
import json
import requests
from pathlib import Path

# Set up the API base URL
API_BASE_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("\n=== Testing Health Endpoint ===")
    
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    
    print("✅ Health endpoint test passed!")
    return True

def test_chat_endpoint():
    """Test the chat endpoint."""
    print("\n=== Testing Chat Endpoint ===")
    
    # Test data
    data = {
        "question": "What are the benefits of regular exercise?",
        "conversation_id": "test_conversation",
        "stream": False
    }
    
    # Make the request
    response = requests.post(f"{API_BASE_URL}/api/chat", json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result.get('answer', '')[:100]}...")
        print(f"Citations: {result.get('citations', [])}")
        print(f"Confidence: {result.get('confidence', 0)}")
        
        assert "answer" in result
        assert isinstance(result.get("citations", []), list)
        assert isinstance(result.get("confidence", 0), (int, float))
        
        print("✅ Chat endpoint test passed!")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def test_document_upload_endpoint():
    """Test the document upload endpoint."""
    print("\n=== Testing Document Upload Endpoint ===")
    
    # Create a test document
    test_file_path = Path("test_document.txt")
    with open(test_file_path, "w") as f:
        f.write("This is a test document for the Health AI Consultant API.\n")
        f.write("It contains information about exercise and nutrition.\n\n")
        f.write("Regular exercise can help improve cardiovascular health and reduce the risk of heart disease.\n")
        f.write("A balanced diet rich in fruits and vegetables provides essential nutrients for overall health.\n")
    
    # Upload the document
    with open(test_file_path, "rb") as f:
        files = {"file": (test_file_path.name, f)}
        response = requests.post(f"{API_BASE_URL}/api/documents/upload", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Document ID: {result.get('document_id', '')}")
        print(f"Filename: {result.get('filename', '')}")
        print(f"Metadata: {json.dumps(result.get('metadata', {}), indent=2)}")
        
        assert result.get("success") is True
        assert "document_id" in result
        assert "metadata" in result
        
        # Clean up
        test_file_path.unlink()
        
        print("✅ Document upload endpoint test passed!")
        return True
    else:
        print(f"Error: {response.json()}")
        # Clean up
        test_file_path.unlink()
        return False

def test_list_documents_endpoint():
    """Test the list documents endpoint."""
    print("\n=== Testing List Documents Endpoint ===")
    
    response = requests.get(f"{API_BASE_URL}/api/documents/")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Documents: {json.dumps(result.get('documents', []), indent=2)}")
        
        assert "documents" in result
        assert isinstance(result["documents"], list)
        
        print("✅ List documents endpoint test passed!")
        return True
    else:
        print(f"Error: {response.json()}")
        return False

def run_all_tests():
    """Run all API tests."""
    print("\n🔍 Running Health AI Consultant API Tests 🔍\n")
    
    # Track test results
    results = {
        "health": False,
        "chat": False,
        "document_upload": False,
        "list_documents": False
    }
    
    try:
        # Test health endpoint
        results["health"] = test_health_endpoint()
        
        # Test chat endpoint
        results["chat"] = test_chat_endpoint()
        
        # Test document upload endpoint
        results["document_upload"] = test_document_upload_endpoint()
        
        # Test list documents endpoint
        results["list_documents"] = test_list_documents_endpoint()
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
    
    # Print summary
    print("\n=== Test Summary ===")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed! 🎉")
    else:
        print("\n⚠️ Some tests failed. Please check the logs above for details.")
    
    return all_passed

if __name__ == "__main__":
    # Check if the Flask app is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
    except requests.ConnectionError:
        print("❌ Error: The Flask app is not running. Please start the app before running tests.")
        print("   Run: python app_flask.py")
        sys.exit(1)
    
    # Run the tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
