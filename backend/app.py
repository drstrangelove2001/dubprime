"""
DubPrime Backend API
--------------------
Unified Flask API for video transcription, translation, and audio processing.
"""

from flask import Flask
from flask_cors import CORS
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
app.config['UPLOAD_FOLDER'] = Path('uploads')
app.config['OUTPUT_FOLDER'] = Path('outputs')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'mp3', 'wav', 'm4a'}

# Create folders if they don't exist
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)

# Import route blueprints
from whisper_routes import whisper_bp

# Register blueprints
app.register_blueprint(whisper_bp)

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'service': 'dubprime-backend',
        'openai_configured': bool(os.getenv('OPENAI_API_KEY'))
    }


def main():
    """Run the API server."""
    print("\n" + "="*70)
    print("DubPrime Backend API Server")
    print("="*70)
    print("\nEndpoints:")
    print("  GET  /api/health            - Health check")
    print("  POST /api/transcribe        - Transcribe video with Whisper")
    print("  POST /api/translate         - Translate subtitles")
    print("\nStarting server on http://localhost:3001")
    print("="*70 + "\n")

    app.run(debug=True, host='0.0.0.0', port=3001)


if __name__ == '__main__':
    main()
