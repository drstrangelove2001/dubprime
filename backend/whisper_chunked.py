"""
Chunked Whisper Transcription
------------------------------
For long videos (>10 minutes), split audio into chunks to prevent sync drift.
"""

import subprocess
from pathlib import Path
import math
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def get_audio_duration(audio_path):
    """Get audio duration in seconds using ffprobe."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        str(audio_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())


def split_audio_chunk(audio_path, start_time, duration, output_path):
    """
    Extract a chunk of audio using ffmpeg.

    Args:
        audio_path: Input audio file
        start_time: Start time in seconds
        duration: Duration in seconds
        output_path: Output file path
    """
    cmd = [
        'ffmpeg',
        '-ss', str(start_time),
        '-i', str(audio_path),
        '-t', str(duration),
        '-acodec', 'aac',  # Re-encode to AAC for M4A container
        '-ar', '44100',    # Keep original sample rate
        '-y',
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def transcribe_audio_chunked(audio_path, chunk_duration=300, **whisper_options):
    """
    Transcribe audio in chunks to prevent sync issues on long videos.

    Args:
        audio_path: Path to audio file
        chunk_duration: Duration of each chunk in seconds (default: 300 = 5 minutes)
        **whisper_options: Additional options for Whisper API (language, prompt, etc.)

    Returns:
        list: Combined subtitles from all chunks
    """
    total_duration = get_audio_duration(audio_path)
    num_chunks = math.ceil(total_duration / chunk_duration)

    print(f'Audio duration: {total_duration:.2f}s')
    print(f'Splitting into {num_chunks} chunks of ~{chunk_duration}s each')

    all_subtitles = []
    temp_chunks = []

    try:
        for i in range(num_chunks):
            start_time = i * chunk_duration

            # Last chunk might be shorter
            current_duration = min(chunk_duration, total_duration - start_time)

            print(f'Processing chunk {i+1}/{num_chunks} ({start_time:.2f}s - {start_time + current_duration:.2f}s)')

            # Create temporary chunk file (.m4a is supported by Whisper API)
            chunk_path = Path(audio_path).parent / f'chunk_{i}.m4a'
            temp_chunks.append(chunk_path)

            # Extract chunk
            split_audio_chunk(audio_path, start_time, current_duration, chunk_path)

            # Transcribe chunk
            with open(chunk_path, 'rb') as audio_file:
                transcription_options = {
                    'file': audio_file,
                    'model': 'whisper-1',
                    'response_format': 'verbose_json',
                    'timestamp_granularities': ['segment'],
                    **whisper_options
                }

                transcription = client.audio.transcriptions.create(**transcription_options)

                # Adjust timestamps to account for chunk offset
                for segment in transcription.segments:
                    all_subtitles.append({
                        'id': len(all_subtitles) + 1,
                        'start': segment.start + start_time,  # Add offset
                        'end': segment.end + start_time,      # Add offset
                        'text': segment.text.strip()
                    })

            print(f'Chunk {i+1} complete: {len(transcription.segments)} segments')

    finally:
        # Clean up temporary chunk files
        for chunk_path in temp_chunks:
            if chunk_path.exists():
                try:
                    chunk_path.unlink()
                except:
                    pass

    print(f'Total subtitles generated: {len(all_subtitles)}')
    return all_subtitles


def should_use_chunking(duration_seconds, threshold=600):
    """
    Determine if video should be processed in chunks.

    Args:
        duration_seconds: Video duration in seconds
        threshold: Threshold in seconds (default: 600 = 10 minutes)

    Returns:
        bool: True if chunking is recommended
    """
    return duration_seconds > threshold
