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
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationError, setGenerationError] = useState(null)
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

  const handleGenerateSubtitles = async () => {
    if (!videoFile) {
      setGenerationError('No video file selected')
      return
    }

    setIsGenerating(true)
    setGenerationError(null)
    setSubtitles([]) // Clear existing subtitles

    try {
      // Create FormData to send video file and settings
      const formData = new FormData()
      formData.append('video', videoFile)
      formData.append('targetLanguage', contextSettings.targetLanguage)
      formData.append('sourceLanguage', contextSettings.sourceLanguage)
      formData.append('culturalContext', contextSettings.culturalContext)
      formData.append('tone', contextSettings.tone)

      console.log('Sending video to backend for transcription...')

      // Call backend API
      const response = await fetch('http://localhost:3001/api/transcribe', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to generate subtitles')
      }

      const data = await response.json()

      console.log('Transcription successful:', data.metadata)
      setSubtitles(data.subtitles)

    } catch (error) {
      console.error('Error generating subtitles:', error)
      setGenerationError(error.message || 'Failed to generate subtitles. Please try again.')
    } finally {
      setIsGenerating(false)
    }
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
                isGenerating={isGenerating}
                generationError={generationError}
              />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App

