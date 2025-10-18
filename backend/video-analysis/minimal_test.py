#!/usr/bin/env python3
"""
Minimal video context generator - optimized for free tier limits
Uses lowest quality settings to maximize quota usage
"""

import argparse
import json
import time
from geminicontextor.frames_api import analyze_video_framesapi

def main():
    ap = argparse.ArgumentParser(description="Minimal video context generator")
    ap.add_argument("--video", required=True, help="Path to video file")
    ap.add_argument("--out_json", default="minimal_results.jsonl", help="Output file")
    args = ap.parse_args()
    
    print("🎬 Starting minimal video analysis...")
    print("⚙️  Using ultra-conservative settings for free tier")
    
    try:
        # Ultra-conservative settings:
        # - 0.25 FPS = 1 frame every 4 seconds
        # - Batch size 1 = 1 request per API call
        # - Minimal processing
        data = analyze_video_framesapi(
            video_path=args.video,
            fps=0.25,  # 1 frame every 4 seconds
            batch_size=1,  # 1 frame per request
            model="gemini-2.5-flash"  # Fastest model
        )
        
        # Save results
        with open(args.out_json, "w", encoding="utf-8") as f:
            for row in data:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        
        print(f"✅ Success! Generated {len(data)} context entries")
        print(f"📄 Results saved to: {args.out_json}")
        
        # Show sample results
        if data:
            print("\n📊 Sample output:")
            sample = data[0]
            print(f"  Time: {sample.get('t_start', 'N/A')}s")
            print(f"  Labels: {sample.get('vision', {}).get('labels', [])}")
            print(f"  Description: {sample.get('vision', {}).get('description', 'N/A')}")
        
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            print("⏳ Quota limit reached. Please wait and try again later.")
            print("💡 Try again in 1-2 minutes, or upgrade to paid plan for higher limits.")
        else:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
