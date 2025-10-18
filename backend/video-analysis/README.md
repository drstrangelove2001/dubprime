# 🎬 Video Analysis Backend

This directory contains the video context analysis engine that powers DubPrime's intelligent video understanding capabilities.

## 🚀 Features

- **AI-Powered Analysis**: Uses Google Gemini AI to extract rich contextual information from videos
- **Multiple Analysis Modes**: File API (per-second) and Frames API (custom FPS)
- **Custom Prompts**: Specialized analysis for different use cases
- **Preset Analysis Types**: Basic, detailed, emotional, technical, and narrative analysis
- **Quota Management**: Built-in retry logic for free tier limits
- **Rich Output**: Structured JSON with vision labels, descriptions, emotions, and more

## 📊 Integration with DubPrime

This video analysis engine provides the foundation for DubPrime's intelligent features:

- **Context-Aware Dubbing**: Understands scene context for better translation
- **Emotional Analysis**: Detects mood and emotions for appropriate voice tone
- **Scene Understanding**: Identifies settings, characters, and activities
- **Cultural Context**: Analyzes visual elements for cultural adaptation

## ⚙️ Quick Start

### 1. Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up API key
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 2. Basic Usage

```bash
# Analyze video with conservative settings
python quota_aware_test.py --video "sample.mp4" --fps 0.1

# Detailed emotional analysis
python enhanced_test.py --video "sample.mp4" --preset emotional --fps 0.25

# Custom analysis
python enhanced_test.py --video "sample.mp4" --prompt_file prompts/detailed_analysis.txt
```

## 📈 Output Format

The analysis generates structured JSON data:

```json
{
  "t_start": 0.0,
  "t_end": 0.0,
  "vision.labels": ["outdoor", "porch", "lake", "people", "Adirondack chairs"],
  "vision.time_of_day": "day",
  "vision.description": "A woman sits on a porch, smiling at a man, with a scenic lake and trees in the background.",
  "vision.mood": "peaceful",
  "vision.lighting": "natural",
  "vision.colors": ["blue", "green", "white", "brown"],
  "audio": []
}
```

## 🔧 API Integration

### For DubPrime Frontend

The video analysis can be integrated into DubPrime's React frontend:

```javascript
// Example API call to video analysis service
const analyzeVideo = async (videoFile) => {
  const formData = new FormData();
  formData.append('video', videoFile);
  
  const response = await fetch('/api/analyze-video', {
    method: 'POST',
    body: formData
  });
  
  return response.json();
};
```

### Backend Service

Create a Flask/FastAPI service to expose the video analysis:

```python
from flask import Flask, request, jsonify
from geminicontextor.frames_api import analyze_video_framesapi

app = Flask(__name__)

@app.route('/api/analyze-video', methods=['POST'])
def analyze_video():
    video_file = request.files['video']
    analysis_type = request.form.get('type', 'basic')
    
    # Save uploaded video temporarily
    video_path = f"temp_{video_file.filename}"
    video_file.save(video_path)
    
    try:
        # Analyze video based on type
        if analysis_type == 'emotional':
            results = analyze_video_framesapi(
                video_path, 
                fps=0.25, 
                custom_prompt=get_emotional_prompt()
            )
        else:
            results = analyze_video_framesapi(video_path, fps=0.1)
        
        return jsonify({
            'success': True,
            'analysis': results,
            'frames_analyzed': len(results)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
    finally:
        # Clean up temporary file
        os.remove(video_path)

if __name__ == '__main__':
    app.run(debug=True)
```

## 📁 File Structure

```
backend/video-analysis/
├── geminicontextor/          # Core analysis package
│   ├── __init__.py
│   ├── file_api.py           # File API implementation
│   ├── frames_api.py         # Frames API implementation
│   └── utils.py              # Utility functions
├── prompts/                  # Analysis prompt templates
│   ├── detailed_analysis.txt
│   ├── emotional_analysis.txt
│   └── narrative_analysis.txt
├── quota_aware_test.py       # Production-ready analysis script
├── enhanced_test.py          # Advanced analysis with custom prompts
├── minimal_test.py           # Minimal analysis for testing
└── requirements.txt          # Python dependencies
```

## 🎯 Use Cases in DubPrime

1. **Scene Context**: Understand setting and atmosphere for appropriate dubbing style
2. **Character Analysis**: Identify speakers and their emotional states
3. **Cultural Adaptation**: Analyze visual elements for cultural context
4. **Timing Optimization**: Use scene changes to optimize subtitle timing
5. **Quality Enhancement**: Provide context for better translation accuracy

## 🔧 Configuration

### Recommended Settings

- **Development**: `--fps 0.1 --batch_size 1`
- **Production**: `--fps 0.25 --batch_size 2`
- **High Quality**: `--fps 0.5 --batch_size 4`

### API Limits

- **Free Tier**: 10 requests/minute, 250 requests/day
- **Paid Tier**: Higher limits available

## 📞 Support

- Check the main DubPrime documentation
- Create issues for video analysis specific problems
- Refer to the original [GeminiContextor repository](https://github.com/chirdeep/geminicontextor) for detailed documentation

---

**Part of the DubPrime video dubbing platform** 🎬
