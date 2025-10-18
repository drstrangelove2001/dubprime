import { useState } from 'react'
import Header from './components/Header'
import VideoUpload from './components/VideoUpload'
import VideoPlayer from './components/VideoPlayer'
import SubtitleEditor from './components/SubtitleEditor'
import ContextPanel from './components/ContextPanel'

function App() {
  const [videoFile, setVideoFile] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [subtitles, setSubtitles] = useState([])
  const [currentTime, setCurrentTime] = useState(0)
  const [contextSettings, setContextSettings] = useState({
    targetLanguage: 'en',
    sourceLanguage: 'auto',
    culturalContext: '',
    tone: 'neutral',
    speakerDetection: true
  })

  const handleVideoUpload = (file) => {
    setVideoFile(file)
    const url = URL.createObjectURL(file)
    setVideoUrl(url)
  }

  const handleGenerateSubtitles = () => {
    // This will connect to your backend later
    console.log('Generating subtitles with context:', contextSettings)
    // Mock subtitles for now
    setSubtitles([
      { id: 1, start: 0, end: 3, text: 'Example subtitle 1' },
      { id: 2, start: 3, end: 6, text: 'Example subtitle 2' },
      { id: 3, start: 6, end: 9, text: 'Example subtitle 3' }
    ])
  }

  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {!videoUrl ? (
          <div className="animate-fade-in">
            <VideoUpload onUpload={handleVideoUpload} />
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-slide-up">
            {/* Left side - Video and Subtitles */}
            <div className="lg:col-span-2 space-y-6">
              <VideoPlayer 
                videoUrl={videoUrl} 
                subtitles={subtitles}
                currentTime={currentTime}
                onTimeUpdate={setCurrentTime}
              />
              <SubtitleEditor 
                subtitles={subtitles}
                setSubtitles={setSubtitles}
                currentTime={currentTime}
              />
            </div>

            {/* Right side - Context Panel */}
            <div className="lg:col-span-1">
              <ContextPanel 
                settings={contextSettings}
                setSettings={setContextSettings}
                onGenerate={handleGenerateSubtitles}
                videoFile={videoFile}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

