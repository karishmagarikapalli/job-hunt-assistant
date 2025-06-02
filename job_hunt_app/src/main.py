import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import logging
import os

# Import routes
from src.routes.auth import auth_bp
from src.routes.jobs import jobs_bp
from src.routes.documents import documents_bp
from src.routes.ai import ai_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'logs', 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

# Create app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'logs'), exist_ok=True)

# Create static directory for documents if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), 'static', 'documents'), exist_ok=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
app.register_blueprint(documents_bp, url_prefix='/api/documents')
app.register_blueprint(ai_bp, url_prefix='/api/ai')

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), path)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Job Hunt Ecosystem API is running'})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Run app
    app.run(host='0.0.0.0', port=5000, debug=True)
