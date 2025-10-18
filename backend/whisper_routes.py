"""
Whisper API Routes
------------------
Routes for video transcription and subtitle translation using OpenAI Whisper and GPT.
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import subprocess
import tempfile
from openai import OpenAI
from whisper_chunked import transcribe_audio_chunked, get_audio_duration, should_use_chunking

whisper_bp = Blueprint('whisper', __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuration
UPLOAD_FOLDER = Path('uploads')
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm', 'mp3', 'wav', 'm4a'}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_audio_ffmpeg(video_path, audio_path):
    """
    Extract audio from video using ffmpeg with precise timestamp handling.

    Args:
        video_path: Path to input video file
        audio_path: Path to output audio file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use M4A format (AAC codec) for Whisper API compatibility
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-map', '0:a:0',
            '-vn',
            '-acodec', 'aac',  # AAC codec in M4A container
            '-ar', '44100',     # Keep standard sample rate
            '-avoid_negative_ts', 'make_zero',
            '-y',
            str(audio_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        return True
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr}")
        return False
    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        return False


@whisper_bp.route('/api/transcribe', methods=['POST'])
def transcribe_video():
    """
    Transcribe video audio using OpenAI Whisper.

    Form data:
        - video: Video file
        - targetLanguage: Target language code (optional, default: 'en')
        - sourceLanguage: Source language code (optional, auto-detect if not provided)
        - culturalContext: Cultural context for transcription (optional)
        - tone: Desired tone (optional)

    Returns:
        JSON with subtitles and metadata
    """
    # Check if file is present
    if 'video' not in request.files:
        return jsonify({'error': 'No video file uploaded'}), 400

    file = request.files['video']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    video_path = None
    audio_path = None
    audio_file = None

    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        video_path = UPLOAD_FOLDER / filename
        file.save(str(video_path))

        # Create temporary audio file (use .m4a for Whisper API compatibility)
        audio_path = video_path.with_suffix('.m4a')

        print(f'Extracting audio from video...')
        success = extract_audio_ffmpeg(video_path, audio_path)

        if not success:
            return jsonify({'error': 'Failed to extract audio from video'}), 500

        print(f'Transcribing audio with Whisper...')

        # Get context settings
        target_language = request.form.get('targetLanguage', 'en')
        source_language = request.form.get('sourceLanguage', 'auto')
        cultural_context = request.form.get('culturalContext', '')
        tone = request.form.get('tone', '')

        # Check audio duration to decide on chunking
        duration = get_audio_duration(audio_path)
        use_chunking = should_use_chunking(duration, threshold=600)  # 10 minutes

        if use_chunking:
            print(f'Using chunked transcription for long video ({duration:.2f}s)')

            # Prepare Whisper options
            whisper_options = {}
            if source_language and source_language not in ['auto', 'auto-detect']:
                whisper_options['language'] = source_language

            if cultural_context or tone:
                prompt = ''
                if cultural_context:
                    prompt += f'Cultural context: {cultural_context}. '
                if tone:
                    prompt += f'Tone: {tone}.'
                whisper_options['prompt'] = prompt.strip()

            # Use chunked transcription
            subtitles = transcribe_audio_chunked(
                audio_path,
                chunk_duration=300,  # 5-minute chunks
                **whisper_options
            )

            detected_language = subtitles[0].get('language', 'en') if subtitles else 'en'

        else:
            print(f'Using standard transcription for short video ({duration:.2f}s)')

            # Open audio file for transcription
            audio_file = open(audio_path, 'rb')

            # Prepare Whisper API options
            transcription_options = {
                'file': audio_file,
                'model': 'whisper-1',
                'response_format': 'verbose_json',
                'timestamp_granularities': ['segment']
            }

            # Add language if source language is specified
            if source_language and source_language not in ['auto', 'auto-detect']:
                transcription_options['language'] = source_language

            # Add prompt for better context (optional)
            if cultural_context or tone:
                prompt = ''
                if cultural_context:
                    prompt += f'Cultural context: {cultural_context}. '
                if tone:
                    prompt += f'Tone: {tone}.'
                transcription_options['prompt'] = prompt.strip()

            # Call Whisper API
            transcription = client.audio.transcriptions.create(**transcription_options)

            # Format the response into subtitles
            subtitles = []
            for index, segment in enumerate(transcription.segments):
                subtitles.append({
                    'id': index + 1,
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })

            detected_language = transcription.language

        print(f'Transcription complete: {len(subtitles)} subtitles generated')

        return jsonify({
            'success': True,
            'subtitles': subtitles,
            'metadata': {
                'duration': duration,
                'language': detected_language,
                'segmentCount': len(subtitles),
                'chunked': use_chunking
            }
        })

    except Exception as e:
        print(f'Transcription error: {str(e)}')
        return jsonify({
            'error': 'Failed to transcribe video',
            'details': str(e)
        }), 500

    finally:
        # Close audio file handle if open
        if audio_file:
            try:
                audio_file.close()
            except:
                pass

        # Clean up uploaded files
        if video_path and video_path.exists():
            try:
                video_path.unlink()
            except:
                pass
        if audio_path and audio_path.exists():
            try:
                audio_path.unlink()
            except:
                pass


@whisper_bp.route('/api/translate', methods=['POST'])
def translate_subtitles():
    """
    Translate subtitles using OpenAI GPT.

    JSON body:
        - subtitles: Array of subtitle objects
        - targetLanguage: Target language code
        - sourceLanguage: Source language code (optional)
        - culturalContext: Cultural context (optional)
        - tone: Desired tone (optional)

    Returns:
        JSON with translated subtitles and metadata
    """
    try:
        data = request.get_json()

        subtitles = data.get('subtitles')
        target_language = data.get('targetLanguage')
        source_language = data.get('sourceLanguage')
        cultural_context = data.get('culturalContext', '')
        tone = data.get('tone', '')

        if not subtitles or not isinstance(subtitles, list):
            return jsonify({'error': 'Invalid subtitles data'}), 400

        if not target_language:
            return jsonify({'error': 'Target language is required'}), 400

        print(f'Translating {len(subtitles)} subtitles to {target_language}...')

        # Prepare subtitle text for translation
        subtitle_texts = '\n'.join([sub['text'] for sub in subtitles])

        # Language name mapping for better context
        language_names = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'ja': 'Japanese', 'ko': 'Korean', 'zh': 'Chinese', 'ar': 'Arabic',
            'hi': 'Hindi', 'pt': 'Portuguese'
        }

        target_lang_name = language_names.get(target_language, target_language)
        source_lang_name = language_names.get(source_language, 'the source language') if source_language else 'the source language'

        # Build context-aware prompt
        context_note = ''
        if cultural_context:
            context_note += f'\nCultural context: {cultural_context}'
        if tone:
            tone_descriptions = {
                'neutral': 'balanced and natural',
                'formal': 'polite and respectful',
                'casual': 'relaxed and friendly',
                'humorous': 'fun and engaging'
            }
            tone_desc = tone_descriptions.get(tone, tone)
            context_note += f'\nDesired tone: {tone_desc}'

        # Use GPT-4 for translation
        system_prompt = f"""You are an expert subtitle localizer specializing in natural, conversational translations. Your goal is to convey meaning and emotion, not literal word-for-word translation.

Guidelines:
- Translate for natural flow and readability in {target_lang_name}
- Adapt idioms, expressions, and cultural references to {target_lang_name} equivalents
- Use casual, conversational language that sounds native
- Prioritize how a native speaker would naturally express the same idea
- Keep subtitles concise and easy to read quickly
- Preserve the emotional tone and character personality
- Avoid overly formal or stilted language unless the original is formal
- Don't add explanatory notes or extra context
- Maintain the same number of lines
{context_note}

Context: These are anime/video subtitles, so use appropriate localization conventions.

Output format: One translated subtitle per line, without numbering or timestamps."""

        completion = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': subtitle_texts
                }
            ],
            temperature=0.5
        )

        translated_text = completion.choices[0].message.content.strip()
        translated_lines = [line for line in translated_text.split('\n') if line.strip()]

        # Map translations back to subtitle objects
        translated_subtitles = []
        for index, sub in enumerate(subtitles):
            translated_subtitles.append({
                **sub,
                'text': translated_lines[index] if index < len(translated_lines) else sub['text']
            })

        print('Translation complete')

        return jsonify({
            'success': True,
            'subtitles': translated_subtitles,
            'metadata': {
                'sourceLanguage': source_language or 'auto',
                'targetLanguage': target_language,
                'subtitleCount': len(translated_subtitles)
            }
        })

    except Exception as e:
        print(f'Translation error: {str(e)}')
        return jsonify({
            'error': 'Failed to translate subtitles',
            'details': str(e)
        }), 500
