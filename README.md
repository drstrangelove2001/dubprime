# DubPrime - Intelligent Video Dubbing Platform

A sleek, dark-themed frontend platform for adding AI-powered, context-aware subtitles and dub to videos.

## Features

- 🎥 **Drag & Drop Video Upload** - Easy video file upload with drag-and-drop support
- 🎬 **Video Player** - Custom video player with subtitle overlay display
- ✏️ **Subtitle Editor** - Timeline-based subtitle editor with real-time preview
- 🌍 **Cultural Context** - Configure cultural context and language settings
- 🗣️ **Speaker Detection** - Identify and differentiate between speakers
- 🎨 **Tone Adaptation** - Adjust subtitle tone and style (formal, casual, humorous, etc.)
- 📥 **Export Options** - Download subtitles in SRT, VTT formats or burn into video

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Technology Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon library

## Project Structure

```
subtitle-ai-platform/
├── src/
│   ├── components/
│   │   ├── Header.jsx          # App header with branding
│   │   ├── VideoUpload.jsx     # Video upload interface
│   │   ├── VideoPlayer.jsx     # Video player with controls
│   │   ├── SubtitleEditor.jsx  # Subtitle timeline editor
│   │   └── ContextPanel.jsx    # AI settings and context panel
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # Entry point
│   └── index.css               # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## Future Backend Integration

This frontend is designed to integrate with an AI backend that will:

- Parse video frames to understand atmosphere and context
- Analyze audio for tone and speaker identification
- Generate culturally-aware subtitles using LLM APIs
- Support multiple languages and cultural contexts

## Design Philosophy

- **Dark Theme** - Easy on the eyes for long editing sessions
- **Modern UI** - Sleek, professional interface with smooth animations
- **Responsive** - Works seamlessly on desktop and tablet devices
- **Intuitive** - User-friendly workflow from upload to export

## License

MIT

