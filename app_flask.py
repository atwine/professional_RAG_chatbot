"""
Health AI Consultant - Flask Backend
A professional RAG-powered health consultation application using Flask and Ollama.
"""
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Import our modules (will add more as we develop them)
from config import config

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load configuration
app.config.from_object(config)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        'status': 'healthy',
        'version': '0.1.0',
        'service': 'Health AI Consultant API'
    })

# Main entry point
if __name__ == '__main__':
    app.run(
        debug=app.config.get('DEBUG', True),
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 5000)
    )
