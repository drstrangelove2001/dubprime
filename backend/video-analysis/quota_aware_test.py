#!/usr/bin/env python3
"""
Quota-aware video context generator with automatic retry
Handles rate limits gracefully and waits for quota reset
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

def analyze_with_retry(video_path, fps=0.25, batch_size=1, model="gemini-2.5-flash", max_retries=5):
    """Analyze video with automatic retry on quota errors"""
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}")
            print(f"⚙️  Settings: {fps} FPS, batch size {batch_size}")
            
            data = analyze_video_framesapi(
                video_path=video_path,
                fps=fps,
                batch_size=batch_size,
                model=model
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
    ap = argparse.ArgumentParser(description="Quota-aware video context generator")
    ap.add_argument("--video", required=True, help="Path to video file")
    ap.add_argument("--fps", type=float, default=0.25, help="Frames per second (lower = fewer requests)")
    ap.add_argument("--batch_size", type=int, default=1, help="Batch size (1 = most conservative)")
    ap.add_argument("--model", default="gemini-2.5-flash", help="Model to use")
    ap.add_argument("--out_json", default="quota_aware_results.jsonl", help="Output file")
    ap.add_argument("--max_retries", type=int, default=5, help="Maximum retry attempts")
    args = ap.parse_args()
    
    print("🎬 Starting quota-aware video analysis...")
    print(f"📹 Video: {args.video}")
    print(f"⚙️  Settings: {args.fps} FPS, batch size {args.batch_size}")
    print(f"🤖 Model: {args.model}")
    
    try:
        data = analyze_with_retry(
            video_path=args.video,
            fps=args.fps,
            batch_size=args.batch_size,
            model=args.model,
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
        print("  - Use even lower FPS (e.g., --fps 0.1)")
        print("  - Upgrade to paid plan for higher limits")

if __name__ == "__main__":
    main()
