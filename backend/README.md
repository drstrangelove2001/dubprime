# DubPrime Backend API

Unified Flask backend for video transcription, translation, and audio processing.

## Features

- **Video Transcription**: OpenAI Whisper API integration for accurate speech-to-text
  - **Auto-chunking**: Videos over 10 minutes are automatically split into 5-minute chunks to prevent sync drift
- **Subtitle Translation**: GPT-powered natural language translation with localization
- **Audio Extraction**: Extract and process audio from video files
- **Video Analysis**: Gemini-powered video frame analysis

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install flask>=3.0.0 flask-cors>=4.0.0 openai>=1.0.0 python-dotenv>=1.0.1 opencv-python>=4.7.0 numpy>=1.24.0 moviepy>=1.0.3 Pillow>=10.3.0 google-genai>=0.3.0 pandas>=2.0.0 werkzeug>=3.0.0
```

**Or install individually:**

```bash
# Flask web framework
pip install flask>=3.0.0 flask-cors>=4.0.0

# OpenAI for Whisper and GPT
pip install openai>=1.0.0

# Environment variables
pip install python-dotenv>=1.0.1

# Video/Audio processing
pip install opencv-python>=4.7.0 numpy>=1.24.0 moviepy>=1.0.3 Pillow>=10.3.0

# Google Gemini
pip install google-genai>=0.3.0

# Data processing
pip install pandas>=2.0.0

# Utilities
pip install werkzeug>=3.0.0
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Install FFmpeg

FFmpeg is required for audio extraction. Install it:

**Windows (using Chocolatey):**
```bash
choco install ffmpeg
```

**Windows (using Scoop):**
```bash
scoop install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:3001`

## API Endpoints

### Health Check
```
GET /api/health
```

### Transcribe Video
```
POST /api/transcribe
Content-Type: multipart/form-data

Fields:
- video: Video file (required)
- targetLanguage: Target language code (optional, default: 'en')
- sourceLanguage: Source language code (optional, auto-detect)
- culturalContext: Cultural context for transcription (optional)
- tone: Desired tone (optional)

Response:
{
  "success": true,
  "subtitles": [...],
  "metadata": {
    "duration": 120.5,
    "language": "ja",
    "segmentCount": 45
  }
}
```

### Translate Subtitles
```
POST /api/translate
Content-Type: application/json

Body:
{
  "subtitles": [...],
  "targetLanguage": "en",
  "sourceLanguage": "ja",
  "culturalContext": "Japanese anime",
  "tone": "casual"
}

Response:
{
  "success": true,
  "subtitles": [...],
  "metadata": {
    "sourceLanguage": "ja",
    "targetLanguage": "en",
    "subtitleCount": 45
  }
}
```

## Project Structure

```
backend/
├── app.py                  # Main Flask application
├── whisper_routes.py       # Whisper transcription & translation routes
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .env.example           # Example environment variables
├── audio-extraction/       # Audio extraction module
├── video-analysis/         # Video analysis module
├── uploads/               # Temporary upload directory
└── outputs/               # Output directory
```

## Development

To run in development mode with auto-reload:

```bash
export FLASK_ENV=development  # or set FLASK_ENV=development on Windows
python app.py
```

## Notes

- Maximum file size: 500MB
- Supported formats: MP4, AVI, MOV, MKV, FLV, WMV, WEBM
- Temporary files are automatically cleaned up after processing
