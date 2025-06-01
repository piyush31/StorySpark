import React, { useState, useEffect } from 'react';
import { themes, ageGroups, durations } from './data/themes';
import voiceService from './services/voiceService';
import { isLoggedIn, getCurrentUser, logout } from './services/authService';
import AudioPlayer from './components/AudioPlayer';
import StoryTeller, { EXPRESSIONS } from './components/StoryTeller';
import AuthModal from './components/AuthModal';
import UserProfile from './components/UserProfile';
import './App.css';

function App() {
  // State for story parameters
  const [selectedTheme, setSelectedTheme] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedAge, setSelectedAge] = useState(ageGroups[1].value); // Default to 5-8 years
  const [selectedDuration, setSelectedDuration] = useState(durations[1].value); // Default to medium
  const [childName, setChildName] = useState('');
  const [storyGenerating, setStoryGenerating] = useState(false);
  const [generatedStory, setGeneratedStory] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState('dadi'); // Default to Dadi Maa
  
  // Auth state
  const [user, setUser] = useState(getCurrentUser());
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  // Load available voices when component mounts
  useEffect(() => {
    const loadVoices = async () => {
      try {
        const voices = await voiceService.getAvailableVoices();
        setAvailableVoices(voices);
      } catch (error) {
        console.error('Failed to load voices:', error);
      }
    };
    
    loadVoices();
    
    // Check for user preferences if logged in
    if (user && user.preferences) {
      // Set child name from preferences if available
      if (user.preferences.child_name) {
        setChildName(user.preferences.child_name);
      }
      
      // Set voice from preferences if available
      if (user.preferences.preferred_storyteller) {
        setSelectedVoice(user.preferences.preferred_storyteller);
      }
    }
  }, [user]);
  
  // Handle theme category selection
  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    setSelectedTheme(''); // Reset selected theme when category changes
  };

  // Handle theme selection
  const handleThemeChange = (themeId) => {
    setSelectedTheme(themeId);
  };

  // Handle voice selection
  const handleVoiceChange = (voiceId) => {
    setSelectedVoice(voiceId);
  };
  
  // Handle auth modal events
  const handleAuthSuccess = (data) => {
    setUser(data.user);
    setAuthModalOpen(false);
    
    // Apply user preferences
    if (data.user.preferences) {
      if (data.user.preferences.child_name) {
        setChildName(data.user.preferences.child_name);
      }
      
      if (data.user.preferences.preferred_storyteller) {
        setSelectedVoice(data.user.preferences.preferred_storyteller);
      }
    }
  };
  
  // Handle logout
  const handleLogout = () => {
    logout();
    setUser(null);
    setShowProfile(false);
  };

  // Handle generating a story
  const handleGenerateStory = async () => {
    if (!selectedTheme) {
      alert('Please select a theme first');
      return;
    }
    
    setStoryGenerating(true);
    setGeneratedStory(null);
    
    try {
      // Get the theme information
      const themeInfo = Object.values(themes)
        .flat()
        .find(theme => theme.id === selectedTheme);
      
      // Prepare the story parameters
      const storyParams = {
        theme: themeInfo?.name || selectedTheme,
        age_group: selectedAge,
        duration: selectedDuration,
        child_name: childName || undefined,
        voice: selectedVoice,
        language: "en", // Default language
        // Save the story if the user is logged in
        save: isLoggedIn()
      };
      
      // If we have a selected category, add it
      if (selectedCategory) {
        storyParams.theme_category = selectedCategory;
      }
      
      // Call the backend API to generate the story
      const storyData = await voiceService.generateStory(storyParams);
      
      // Log the audio path for debugging
      console.log("Received audio path:", storyData.audio_path);
      
      // Make sure we have a valid audio path
      if (!storyData.audio_path || storyData.audio_path === '#') {
        console.warn("No valid audio path received, using placeholder");
        storyData.audio_path = process.env.NODE_ENV === 'production' 
          ? '/static/placeholders/story_audio.mp3'
          : 'http://localhost:5000/static/placeholders/story_audio.mp3';
      }
      
      // Update the story data in state
      setGeneratedStory(storyData);
    } catch (error) {
      console.error('Error generating story:', error);
      
      // Fallback to mock story if API fails
      const themeInfo = Object.values(themes)
        .flat()
        .find(theme => theme.id === selectedTheme);
        
      setGeneratedStory({
        id: Date.now(), // Use timestamp as ID
        title: `The Adventure of ${childName || 'the Little Hero'}`,
        text: `This is a placeholder for a story about ${themeInfo?.name || selectedTheme}. In a real implementation, this would be generated by the backend API using Google's Gemini 2.0-flash model for content and Chirp for voice synthesis.`,
        audio_path: '#',
        theme: themeInfo?.name || selectedTheme,
        duration: selectedDuration,
        age_group: selectedAge
      });
    } finally {
      setStoryGenerating(false);
    }
  };

  // Handle audio playback
  const handlePlayAudio = () => {
    setIsPlaying(true);
  };
  
  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  // Reset everything and start over
  const handleStartOver = () => {
    setGeneratedStory(null);
    setSelectedTheme('');
    setSelectedCategory('');
    setIsPlaying(false);
  };

  // Handle downloading a story for offline use
  const handleDownloadStory = async () => {
    if (!generatedStory || !generatedStory.audio_path) return;
    
    try {
      const success = await voiceService.preloadAudio(generatedStory.audio_path, generatedStory.id);
      
      if (success) {
        // Update the story object to mark it as downloaded
        setGeneratedStory({
          ...generatedStory,
          isDownloaded: true
        });
        
        alert('Story downloaded successfully for offline use!');
      } else {
        alert('Failed to download story for offline use.');
      }
    } catch (error) {
      console.error('Error downloading story:', error);
      alert('Error downloading story: ' + error.message);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1>StorySpark</h1>
            <p className="tagline">AI-powered stories for curious young minds</p>
          </div>
          <div className="auth-section">
            {user ? (
              <div className="auth-controls">
                <div className="user-greeting">Hello, {user.username}!</div>
                <button 
                  className="stories-button"
                  onClick={() => window.location.href = '/my-stories'}
                >
                  My Stories
                </button>
                <button 
                  className="profile-button" 
                  onClick={() => setShowProfile(!showProfile)}
                >
                  My Profile
                </button>
                <button 
                  className="logout-button" 
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            ) : (
              <button 
                className="login-button" 
                onClick={() => setAuthModalOpen(true)}
              >
                Login / Register
              </button>
            )}
          </div>
        </div>
      </header>
      
      <main>
        {!generatedStory ? (
          <div className="story-creator">
            <h2>Create a Story</h2>
            
            <div className="form-section">
              <label htmlFor="childName">Child's Name (optional):</label>
              <input 
                type="text" 
                id="childName" 
                value={childName} 
                onChange={(e) => setChildName(e.target.value)} 
                placeholder="Enter child's name"
              />
            </div>
            
            <div className="form-section">
              <label htmlFor="voiceSelect">Storyteller's Voice:</label>
              <div className="voice-options">
                {availableVoices.map(voice => (
                  <div 
                    key={voice.id}
                    className={`voice-option ${selectedVoice === voice.id ? 'selected' : ''}`}
                    onClick={() => handleVoiceChange(voice.id)}
                  >
                    <div className="voice-avatar">
                      <span role="img" aria-label={voice.name}>
                        {voice.gender === 'female' 
                          ? (voice.age === 'elderly' ? '👵' : '👩') 
                          : (voice.age === 'elderly' ? '👴' : '👨')}
                      </span>
                    </div>
                    <div className="voice-name">{voice.name}</div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="form-section">
              <h3>Select a Theme Category:</h3>
              <div className="category-buttons">
                {Object.keys(themes).map((category) => (
                  <button
                    key={category}
                    className={`category-button ${selectedCategory === category ? 'active' : ''}`}
                    onClick={() => handleCategoryChange(category)}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>
            
            {selectedCategory && (
              <div className="form-section">
                <h3>Select a Theme:</h3>
                <div className="theme-cards">
                  {themes[selectedCategory].map((theme) => (
                    <div 
                      key={theme.id}
                      className={`theme-card ${selectedTheme === theme.id ? 'selected' : ''}`}
                      onClick={() => handleThemeChange(theme.id)}
                    >
                      <h4>{theme.name}</h4>
                      <p>{theme.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="form-section sliders">
              <div className="slider-container">
                <h3>Age Group:</h3>
                <div className="slider-labels">
                  {ageGroups.map(age => (
                    <label key={age.value} className={selectedAge === age.value ? 'active' : ''}>
                      <input
                        type="radio"
                        name="age"
                        value={age.value}
                        checked={selectedAge === age.value}
                        onChange={() => setSelectedAge(age.value)}
                      />
                      {age.label}
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="slider-container">
                <h3>Story Duration:</h3>
                <div className="slider-labels">
                  {durations.map(duration => (
                    <label key={duration.value} className={selectedDuration === duration.value ? 'active' : ''}>
                      <input
                        type="radio"
                        name="duration"
                        value={duration.value}
                        checked={selectedDuration === duration.value}
                        onChange={() => setSelectedDuration(duration.value)}
                      />
                      {duration.label}
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="form-section">
              <button 
                className="generate-button" 
                onClick={handleGenerateStory}
                disabled={!selectedTheme || storyGenerating}
              >
                {storyGenerating ? 'Creating your story...' : 'Generate Story'}
              </button>
            </div>
          </div>
        ) : (
          <div className="story-viewer">
            <div className="story-header">
              <h2>{generatedStory.title}</h2>
              <div className="story-meta">
                <span>Theme: {generatedStory.theme}</span>
                <span>Age: {generatedStory.age_group}</span>
                <span>Duration: {generatedStory.duration}</span>
              </div>
            </div>
            
            <div className="storyteller-section">
              <StoryTeller isActive={isPlaying} mood={isPlaying ? EXPRESSIONS.SPEAKING : EXPRESSIONS.NEUTRAL} />
            </div>
            
            <div className="story-content">
              <p>{generatedStory.text}</p>
            </div>
            
            <AudioPlayer 
              audioUrl={generatedStory.audio_path || ''} 
              title={generatedStory.title}
              onEnded={handleAudioEnded}
            />
            
            {generatedStory.audio_path ? (
              <div className="story-actions">
                <button 
                  className={`download-button ${generatedStory.isDownloaded ? 'downloaded' : ''}`}
                  onClick={handleDownloadStory}
                  disabled={generatedStory.isDownloaded}
                >
                  <span role="img" aria-label="Download">⬇️</span> 
                  {generatedStory.isDownloaded ? 'Downloaded' : 'Save for Offline'}
                </button>
                <button className="new-story-button" onClick={handleStartOver}>
                  Create Another Story
                </button>
              </div>
            ) : (
              <div className="story-actions">
                <button className="new-story-button" onClick={handleStartOver}>
                  Create Another Story
                </button>
              </div>
            )}
          </div>
        )}
      </main>
      
      <footer>
        <p>&copy; {new Date().getFullYear()} StorySpark</p>
      </footer>
      
      {/* Auth Modal */}
      <AuthModal 
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />
      
      {/* User Profile Modal */}
      {showProfile && (
        <UserProfile 
          user={user}
          onClose={() => setShowProfile(false)}
          onUpdate={handleAuthSuccess}
        />
      )}
    </div>
  );
}

export default App;
