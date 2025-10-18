# Backend Whisper API

Backend service for video transcription using OpenAI Whisper API.

## Prerequisites

Before running this backend, you need:

1. **Node.js** (v18 or higher)
2. **FFmpeg** installed on your system
3. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))

## Installing FFmpeg

### Windows
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract the archive
3. Add the `bin` folder to your system PATH
4. Verify installation: `ffmpeg -version`

**Quick install with Chocolatey:**
```bash
choco install ffmpeg
```

**Quick install with winget:**
```bash
winget install ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend-whisper-api
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the `backend-whisper-api` directory:

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
PORT=3001
```

**Getting an OpenAI API Key:**
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key and paste it into your `.env` file
5. Note: You'll need to add billing information to your OpenAI account

### 3. Start the Backend Server

```bash
npm start
```

Or for development with auto-reload:

```bash
npm run dev
```

The server will start on `http://localhost:3001`

## API Endpoints

### POST `/api/transcribe`

Transcribes a video file and returns subtitles.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body:
  - `video` (file): The video file to transcribe
  - `targetLanguage` (string): Target language code (e.g., 'en', 'es')
  - `sourceLanguage` (string): Source language code or 'auto-detect'
  - `culturalContext` (string, optional): Cultural context for better transcription
  - `tone` (string, optional): Desired tone (e.g., 'neutral', 'formal', 'casual')

**Response:**
```json
{
  "success": true,
  "subtitles": [
    {
      "id": 1,
      "start": 0.0,
      "end": 3.5,
      "text": "Hello, this is a subtitle"
    }
  ],
  "metadata": {
    "duration": 120.5,
    "language": "en",
    "segmentCount": 45
  }
}
```

### POST `/api/translate`

Translates existing subtitles to a target language using GPT-4.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
  ```json
  {
    "subtitles": [
      {
        "id": 1,
        "start": 0.0,
        "end": 3.5,
        "text": "Hello, this is a subtitle"
      }
    ],
    "targetLanguage": "es",
    "sourceLanguage": "en"
  }
  ```

**Response:**
```json
{
  "success": true,
  "subtitles": [
    {
      "id": 1,
      "start": 0.0,
      "end": 3.5,
      "text": "Hola, este es un subtítulo"
    }
  ],
  "metadata": {
    "sourceLanguage": "en",
    "targetLanguage": "es",
    "subtitleCount": 1
  }
}
```

### GET `/api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "service": "backend-whisper-api",
  "timestamp": "2025-10-18T..."
}
```

## Running Both Frontend and Backend

1. **Terminal 1 - Start Backend:**
   ```bash
   cd backend-whisper-api
   npm start
   ```

2. **Terminal 2 - Start Frontend:**
   ```bash
   npm run dev
   ```

3. Open your browser to `http://localhost:5173` (or the URL shown by Vite)

## Pricing

### Transcription (Whisper API)
OpenAI Whisper API costs approximately **$0.006 per minute** of audio transcribed.

Example:
- 1 minute video = $0.006
- 10 minute video = $0.06
- 60 minute video = $0.36

### Translation (GPT-4o-mini)
Translation uses GPT-4o-mini for high-quality subtitle translation. Costs vary based on subtitle length:
- Input: **$0.150 per 1M tokens**
- Output: **$0.600 per 1M tokens**

Typical costs:
- 100 subtitles (~2000 words) ≈ $0.001 - $0.003
- Translation is very cost-effective compared to transcription

## Troubleshooting

### "FFmpeg not found" error
Make sure FFmpeg is installed and accessible from your command line:
```bash
ffmpeg -version
```

If this command fails, FFmpeg is not properly installed or not in your PATH.

### "OpenAI API key not configured" error
Make sure you've created a `.env` file in the `backend-whisper-api` directory with your API key.

### "Failed to connect to backend" error
Make sure the backend server is running on port 3001. Check the terminal for any error messages.

### CORS errors
The backend is configured to accept requests from any origin. If you still see CORS errors, make sure you're making requests to `http://localhost:3001` (not `https`).

## File Upload Limits

- Maximum file size: 100MB
- Supported formats: MP4, WebM, OGG, QuickTime, MP3, WAV

## How It Works

### Transcription Workflow
1. **Upload**: User uploads a video file from the frontend
2. **Extract**: Backend extracts audio from video using FFmpeg
3. **Transcribe**: Audio is sent to OpenAI Whisper API for transcription
4. **Format**: Transcription segments are formatted into subtitle objects
5. **Return**: Subtitles are sent back to the frontend with detected language
6. **Cleanup**: Temporary files are deleted

### Translation Workflow
Translation happens automatically in two scenarios:

**Scenario 1: During Generation (Target ≠ Detected)**
1. User sets Target Language (e.g., Spanish) before clicking Generate
2. Video transcribed in detected language (e.g., English)
3. System detects language mismatch
4. **Auto-translates** from English → Spanish immediately
5. User receives subtitles in Spanish

**Scenario 2: After Generation (User Changes Language)**
1. User changes Target Language dropdown (e.g., English → French)
2. **Auto-translation** triggers on language change
3. Subtitles translate from current language → French
4. Updated subtitles appear in editor and player

Both workflows use GPT-4o-mini for high-quality translation while preserving timing.

## Development

The backend uses:
- **Express** - Web server framework
- **Multer** - File upload handling
- **OpenAI SDK** - Whisper API integration
- **fluent-ffmpeg** - Audio extraction from video
- **dotenv** - Environment variable management

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Check the terminal output for error messages
