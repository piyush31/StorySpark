import React, { useState, useRef, useEffect } from 'react';
import './AudioPlayer.css';

const AudioPlayer = ({ audioUrl, title, onEnded }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [volume, setVolume] = useState(0.8);
  const [waveformData, setWaveformData] = useState([]);
  
  const audioRef = useRef(null);
  const canvasRef = useRef(null);
  
  // Initialize audio player when component mounts
  useEffect(() => {
    const audio = audioRef.current;
    
    if (!audio) return;
    
    // Event listeners
    const setAudioData = () => {
      setDuration(audio.duration);
      setLoading(false);
      setError(null);
      console.log("Audio loaded successfully:", audioUrl);
      
      // Generate a simulated waveform
      generateSimulatedWaveform();
    };
    
    const setAudioTime = () => setCurrentTime(audio.currentTime);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
      if (onEnded) onEnded();
    };
    
    const handleError = (e) => {
      console.error("Audio error:", e, "URL:", audioUrl);
      setError(`Error loading audio. Please try again. (${audioUrl})`);
      setLoading(false);
    };
    
    // Add event listeners
    audio.addEventListener('loadeddata', setAudioData);
    audio.addEventListener('timeupdate', setAudioTime);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    
    // Set audio source
    if (audioUrl) {
      console.log("Loading audio from URL:", audioUrl);
      try {
        // Validate the URL - handle both absolute and relative URLs
        if (audioUrl.startsWith('http') || audioUrl.startsWith('//')) {
          new URL(audioUrl); // Validate absolute URLs
        } else if (audioUrl.startsWith('/')) {
          // Relative URLs are valid, no validation needed
        } else {
          throw new Error("Invalid URL format");
        }
        audio.src = audioUrl;
        audio.load();
      } catch (urlError) {
        console.error("Invalid audio URL:", urlError, audioUrl);
        setError(`Invalid audio URL format: ${audioUrl}`);
        setLoading(false);
      }
    } else {
      setError("No audio URL provided");
      setLoading(false);
    }
    
    // Cleanup on unmount
    return () => {
      audio.removeEventListener('loadeddata', setAudioData);
      audio.removeEventListener('timeupdate', setAudioTime);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, [audioUrl, onEnded]);
  
  // Generate a simulated waveform since we can't analyze the actual audio
  const generateSimulatedWaveform = () => {
    const waveformLength = 100;
    const waveformArray = [];
    
    // Generate a random but somewhat natural-looking waveform
    let prevValue = 0.5;
    for (let i = 0; i < waveformLength; i++) {
      // Ensure the waveform varies smoothly
      const change = (Math.random() - 0.5) * 0.2;
      let newValue = prevValue + change;
      
      // Keep values between 0.1 and 0.9
      newValue = Math.max(0.1, Math.min(0.9, newValue));
      
      waveformArray.push(newValue);
      prevValue = newValue;
    }
    
    setWaveformData(waveformArray);
  };
  
  // Draw waveform
  useEffect(() => {
    if (waveformData.length === 0 || !canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const { width, height } = canvas;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Calculate current progress
    const progress = duration > 0 ? currentTime / duration : 0;
    const progressPixel = width * progress;
    
    // Bar width with small gap
    const barWidth = width / waveformData.length - 1;
    
    // Draw waveform bars
    waveformData.forEach((amplitude, index) => {
      const x = index * (barWidth + 1);
      const barHeight = height * amplitude;
      
      // Determine if this bar is before or after the current playback position
      const played = x < progressPixel;
      
      // Set colors
      ctx.fillStyle = played ? '#4285f4' : '#e0e0e0';
      
      // Draw the bar
      const y = height - barHeight;
      ctx.fillRect(x, y, barWidth, barHeight);
    });
    
  }, [waveformData, currentTime, duration]);
  
  // Toggle play/pause
  const togglePlay = () => {
    const audio = audioRef.current;
    
    if (!audio) return;
    
    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      // Try to play and handle any errors
      audio.play().catch(err => {
        console.error("Error playing audio:", err);
        setError(`Error playing audio: ${err.message}. Try reloading the page.`);
        setIsPlaying(false);
      });
      setIsPlaying(true);
    }
  };
  
  // Handle seeking
  const handleSeek = (e) => {
    const audio = audioRef.current;
    
    if (!audio) return;
    
    const seekTime = (e.target.value / 100) * duration;
    audio.currentTime = seekTime;
    setCurrentTime(seekTime);
  };
  
  // Handle volume change
  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  };
  
  // Format time in mm:ss
  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };
  
  return (
    <div className="audio-player">
      <audio ref={audioRef} preload="metadata" />
      
      <div className="audio-title">
        <span role="img" aria-label="Music">🎵</span> {title || "Story Audio"}
      </div>
      
      {loading ? (
        <div className="audio-loading">
          <div className="loading-spinner"></div>
          <span>Loading audio...</span>
        </div>
      ) : error ? (
        <div className="audio-error">{error}</div>
      ) : (
        <>
          <div className="waveform-container">
            <canvas 
              ref={canvasRef} 
              className="audio-waveform" 
              width="300" 
              height="60"
              onClick={(e) => {
                const canvas = canvasRef.current;
                if (!canvas || !audioRef.current) return;
                
                const rect = canvas.getBoundingClientRect();
                const clickX = e.clientX - rect.left;
                const seekPercentage = clickX / rect.width;
                
                audioRef.current.currentTime = seekPercentage * duration;
              }}
            />
          </div>
          
          <div className="player-controls">
            <button className="play-button" onClick={togglePlay}>
              {isPlaying ? (
                <span role="img" aria-label="Pause">⏸️</span>
              ) : (
                <span role="img" aria-label="Play">▶️</span>
              )}
            </button>
            
            <div className="time-display">{formatTime(currentTime)}</div>
            
            <input
              type="range"
              className="seek-slider"
              min="0"
              max="100"
              value={(currentTime / duration) * 100 || 0}
              onChange={handleSeek}
            />
            
            <div className="time-display">{formatTime(duration)}</div>
          </div>
          
          <div className="player-buttons">
            <button className="player-button" onClick={() => {
              const audio = audioRef.current;
              if (audio) {
                audio.currentTime = Math.max(0, audio.currentTime - 10);
              }
            }}>
              <span role="img" aria-label="Rewind">⏪</span> 10s
            </button>
            
            <div className="volume-control">
              <span role="img" aria-label="Volume">🔊</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={volume}
                onChange={handleVolumeChange}
                className="volume-slider"
              />
            </div>
            
            <button className="player-button" onClick={() => {
              const audio = audioRef.current;
              if (audio) {
                audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
              }
            }}>
              10s <span role="img" aria-label="Forward">⏩</span>
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default AudioPlayer;
