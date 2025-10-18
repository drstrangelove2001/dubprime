import os, json
from typing import List, Dict, Any
from dotenv import load_dotenv

def _client():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Set GEMINI_API_KEY in environment or .env")
    from google import genai
    return genai.Client(api_key=api_key)

DEFAULT_SYSTEM_PROMPT = (
"You are a video context extractor. For each second of the video, return concise JSON with:\n"
"- vision.labels: up to 5 scene/object tags (e.g., 'indoor','outdoor','city street','cafe','rain','ocean','forest','night','day','car','crowd','police','music stage').\n"
"- vision.time_of_day: day|night|dusk|dawn (best guess).\n"
"- vision.description: one short sentence about the visuals.\n"
"- audio.events: up to 3 notable sounds ('rain','wind','piano','sirens','crowd murmur').\n"
"- audio.loudness: quiet|moderate|loud.\n"
"Return an array of entries, one per second, with fields t_start and t_end. JSON only."
)

def analyze_video_fileapi(video_path: str, model: str = "gemini-2.0-pro-exp-02-05") -> List[Dict[str, Any]]:
    client = _client()
    uploaded = client.files.upload(file=video_path)
    content = [
        {"role":"user","parts":[
            {"file_data": {"mime_type": uploaded.mime_type, "file_uri": uploaded.uri}},
            {"text": DEFAULT_SYSTEM_PROMPT}
        ]}
    ]
    resp = client.models.generate_content(
        model=model,
        contents=content,
        config={"response_mime_type":"application/json"}
    )
    data = resp.parsed if hasattr(resp, "parsed") else resp.text
    if isinstance(data, str):
        data = json.loads(data)
    return data
