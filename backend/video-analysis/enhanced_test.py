#!/usr/bin/env python3
"""
Enhanced video context generator with custom prompts
Allows you to specify detailed prompts for more comprehensive analysis
"""

import argparse
import json
import time
import re
from geminicontextor.frames_api import analyze_video_framesapi

def extract_retry_delay(error_message):
    """Extract retry delay from quota error message"""
    match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_message)
    if match:
        return float(match.group(1))
    return 60  # Default 1 minute

def analyze_with_retry(video_path, fps=0.1, batch_size=1, model="gemini-2.5-flash", custom_prompt=None, max_retries=5):
    """Analyze video with automatic retry on quota errors"""
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}")
            print(f"⚙️  Settings: {fps} FPS, batch size {batch_size}")
            if custom_prompt:
                print(f"📝 Using custom prompt: {custom_prompt[:100]}...")
            
            data = analyze_video_framesapi(
                video_path=video_path,
                fps=fps,
                batch_size=batch_size,
                model=model,
                custom_prompt=custom_prompt
            )
            
            print(f"✅ Success! Generated {len(data)} context entries")
            return data
            
        except Exception as e:
            error_str = str(e)
            
            if "429" in error_str or "quota" in error_str.lower():
                retry_delay = extract_retry_delay(error_str)
                print(f"⏳ Quota limit reached. Waiting {retry_delay:.1f} seconds...")
                
                if attempt < max_retries - 1:
                    print(f"🔄 Will retry in {retry_delay:.1f} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("❌ Max retries reached. Please try again later or upgrade to paid plan.")
                    raise
            else:
                print(f"❌ Non-quota error: {e}")
                raise
    
    return []

def main():
    ap = argparse.ArgumentParser(description="Enhanced video context generator with custom prompts")
    ap.add_argument("--video", required=True, help="Path to video file")
    ap.add_argument("--fps", type=float, default=0.1, help="Frames per second (lower = fewer requests)")
    ap.add_argument("--batch_size", type=int, default=1, help="Batch size (1 = most conservative)")
    ap.add_argument("--model", default="gemini-2.5-flash", help="Model to use")
    ap.add_argument("--out_json", default="enhanced_results.jsonl", help="Output file")
    ap.add_argument("--max_retries", type=int, default=5, help="Maximum retry attempts")
    ap.add_argument("--prompt", help="Custom prompt for analysis")
    ap.add_argument("--prompt_file", help="File containing custom prompt")
    ap.add_argument("--preset", choices=["basic", "detailed", "emotional", "technical", "narrative"], 
                   help="Use a preset prompt")
    args = ap.parse_args()
    
    # Load custom prompt
    custom_prompt = None
    if args.prompt_file:
        with open(args.prompt_file, 'r') as f:
            custom_prompt = f.read().strip()
    elif args.prompt:
        custom_prompt = args.prompt
    elif args.preset:
        custom_prompt = get_preset_prompt(args.preset)
    
    print("🎬 Starting enhanced video analysis...")
    print(f"📹 Video: {args.video}")
    print(f"⚙️  Settings: {args.fps} FPS, batch size {args.batch_size}")
    print(f"🤖 Model: {args.model}")
    
    if custom_prompt:
        print(f"📝 Custom prompt enabled")
    else:
        print("📝 Using default prompt")
    
    try:
        data = analyze_with_retry(
            video_path=args.video,
            fps=args.fps,
            batch_size=args.batch_size,
            model=args.model,
            custom_prompt=custom_prompt,
            max_retries=args.max_retries
        )
        
        # Save results
        with open(args.out_json, "w", encoding="utf-8") as f:
            for row in data:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        
        print(f"📄 Results saved to: {args.out_json}")
        
        # Show sample results
        if data:
            print("\n📊 Sample outputs:")
            for i, sample in enumerate(data[:3]):  # Show first 3 results
                print(f"  {i+1}. Time: {sample.get('t_start', 'N/A')}s")
                print(f"     Labels: {sample.get('vision', {}).get('labels', [])}")
                print(f"     Description: {sample.get('vision', {}).get('description', 'N/A')}")
                print()
        
    except Exception as e:
        print(f"❌ Final error: {e}")
        print("\n💡 Suggestions:")
        print("  - Wait 1-2 minutes and try again")
        print("  - Use even lower FPS (e.g., --fps 0.05)")
        print("  - Upgrade to paid plan for higher limits")

def get_preset_prompt(preset):
    """Get preset prompts for different analysis types"""
    prompts = {
        "basic": """You are a scene context extractor for still frames. For EACH input image, respond with a compact JSON array of same length, where each element corresponds to the respective image, with the following fields:
- vision.labels: up to 5 tags (indoor/outdoor, scene, notable objects).
- vision.time_of_day: day|night|dusk|dawn.
- vision.description: 1 short sentence.
- audio: leave empty array ([]).
Do NOT include any prose; return JSON only.""",

        "detailed": """You are an advanced scene analyzer for video frames. For EACH input image, provide a comprehensive JSON array with detailed analysis:
- vision.labels: up to 8 descriptive tags (location, objects, people, activities, mood, lighting, weather, etc.)
- vision.time_of_day: day|night|dusk|dawn|sunset|sunrise
- vision.description: 2-3 detailed sentences describing the scene, people, objects, and activities
- vision.mood: emotional tone (happy|sad|tense|peaceful|energetic|melancholy|etc.)
- vision.lighting: lighting conditions (bright|dim|natural|artificial|dramatic|soft|etc.)
- vision.weather: weather conditions if visible (sunny|cloudy|rainy|foggy|etc.)
- audio: leave empty array ([])
Return JSON only, no additional text.""",

        "emotional": """You are an emotional context analyzer for video frames. For EACH input image, focus on emotional and psychological aspects:
- vision.labels: emotional and psychological tags (facial expressions, body language, mood indicators)
- vision.time_of_day: day|night|dusk|dawn
- vision.description: detailed description focusing on emotions, expressions, and interpersonal dynamics
- vision.emotions: primary emotions visible (joy|sadness|anger|fear|surprise|disgust|contempt|etc.)
- vision.body_language: description of body language and gestures
- vision.interaction: how people are interacting (talking|arguing|embracing|avoiding|etc.)
- audio: leave empty array ([])
Return JSON only.""",

        "technical": """You are a technical scene analyzer for video frames. For EACH input image, provide technical and compositional analysis:
- vision.labels: technical and compositional tags (camera angle, composition, lighting setup, etc.)
- vision.time_of_day: day|night|dusk|dawn
- vision.description: technical description of the shot composition, lighting, and visual elements
- vision.composition: compositional analysis (rule of thirds, leading lines, symmetry, etc.)
- vision.lighting: technical lighting description (key light, fill light, backlight, etc.)
- vision.camera_angle: camera perspective (close-up|medium|wide|bird's eye|worm's eye|etc.)
- audio: leave empty array ([])
Return JSON only.""",

        "narrative": """You are a narrative context analyzer for video frames. For EACH input image, focus on storytelling elements:
- vision.labels: narrative and storytelling tags (characters, setting, plot elements, etc.)
- vision.time_of_day: day|night|dusk|dawn
- vision.description: narrative description focusing on characters, setting, and potential story elements
- vision.characters: description of people and their roles in the scene
- vision.setting: detailed description of the location and environment
- vision.story_elements: potential plot points, conflicts, or story developments visible
- vision.atmosphere: overall atmosphere and tone of the scene
- audio: leave empty array ([])
Return JSON only."""
    }
    return prompts.get(preset, prompts["basic"])

if __name__ == "__main__":
    main()
