import express from 'express';
import cors from 'cors';
import multer from 'multer';
import OpenAI from 'openai';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import ffmpeg from 'fluent-ffmpeg';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Middleware
app.use(cors());
app.use(express.json());

// Configure multer for file uploads
const upload = multer({
  dest: 'uploads/',
  limits: {
    fileSize: 100 * 1024 * 1024 // 100MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedMimes = ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime', 'audio/mpeg', 'audio/wav'];
    if (allowedMimes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only video and audio files are allowed.'));
    }
  }
});

// Ensure uploads directory exists
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

// Extract audio from video using ffmpeg
function extractAudio(videoPath, audioPath) {
  return new Promise((resolve, reject) => {
    ffmpeg(videoPath)
      .output(audioPath)
      .audioCodec('libmp3lame')
      .audioFrequency(16000) // Whisper works well with 16kHz
      .audioChannels(1) // Mono audio
      .on('end', () => resolve(audioPath))
      .on('error', (err) => reject(err))
      .run();
  });
}

// POST endpoint for video transcription
app.post('/api/transcribe', upload.single('video'), async (req, res) => {
  let videoPath = null;
  let audioPath = null;

  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No video file uploaded' });
    }

    videoPath = req.file.path;
    audioPath = videoPath + '.mp3';

    console.log('Extracting audio from video...');
    await extractAudio(videoPath, audioPath);

    console.log('Transcribing audio with Whisper...');

    // Get context settings from request body
    const {
      targetLanguage = 'en',
      sourceLanguage,
      culturalContext,
      tone
    } = req.body;

    // Prepare Whisper API options
    const transcriptionOptions = {
      file: fs.createReadStream(audioPath),
      model: 'whisper-1',
      response_format: 'verbose_json',
      timestamp_granularities: ['segment']
    };

    // Add language if source language is specified
    // Skip if auto-detect (Whisper auto-detects by default when language is not provided)
    if (sourceLanguage && sourceLanguage !== 'auto' && sourceLanguage !== 'auto-detect') {
      transcriptionOptions.language = sourceLanguage;
    }

    // Add prompt for better context (optional)
    if (culturalContext || tone) {
      let prompt = '';
      if (culturalContext) prompt += `Cultural context: ${culturalContext}. `;
      if (tone) prompt += `Tone: ${tone}.`;
      transcriptionOptions.prompt = prompt.trim();
    }

    const transcription = await openai.audio.transcriptions.create(transcriptionOptions);

    // Format the response into subtitles
    const subtitles = transcription.segments.map((segment, index) => ({
      id: index + 1,
      start: segment.start,
      end: segment.end,
      text: segment.text.trim()
    }));

    console.log(`Transcription complete: ${subtitles.length} subtitles generated`);

    res.json({
      success: true,
      subtitles,
      metadata: {
        duration: transcription.duration,
        language: transcription.language,
        segmentCount: subtitles.length
      }
    });

  } catch (error) {
    console.error('Transcription error:', error);
    res.status(500).json({
      error: 'Failed to transcribe video',
      details: error.message
    });
  } finally {
    // Clean up uploaded files
    if (videoPath && fs.existsSync(videoPath)) {
      fs.unlinkSync(videoPath);
    }
    if (audioPath && fs.existsSync(audioPath)) {
      fs.unlinkSync(audioPath);
    }
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'backend-whisper-api',
    timestamp: new Date().toISOString()
  });
});

app.listen(PORT, () => {
  console.log(`Backend Whisper API server running on http://localhost:${PORT}`);
  console.log(`OpenAI API Key configured: ${process.env.OPENAI_API_KEY ? 'Yes' : 'No'}`);
});
