import React, { useState, useEffect } from 'react';
import storiesService from './services/storiesService';
import './App.css';

function App() {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [activeView, setActiveView] = useState('all'); // 'all' or 'downloaded'

  // Network status detection
  useEffect(() => {
    function handleOnlineStatus() {
      setIsOnline(true);
    }

    function handleOfflineStatus() {
      setIsOnline(false);
    }

    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);

    return () => {
      window.removeEventListener('online', handleOnlineStatus);
      window.removeEventListener('offline', handleOfflineStatus);
    };
  }, []);

  // Fetch stories from API or cache
  useEffect(() => {
    async function fetchStories() {
      try {
        const data = await storiesService.fetchStories();
        setStories(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }

    fetchStories();
  }, []);

  // Toggle download status for a story
  const toggleDownload = (storyId) => {
    const story = stories.find(s => s.id === storyId);
    let updatedStories;
    
    if (story?.isDownloaded) {
      updatedStories = storiesService.removeDownload(storyId);
    } else {
      updatedStories = storiesService.markAsDownloaded(storyId);
    }
    
    setStories(updatedStories);
  };

  // Filter stories based on current view
  const displayedStories = activeView === 'downloaded' 
    ? stories.filter(story => story.isDownloaded)
    : stories;

  if (loading) {
    return <div className="loading">Loading stories...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>StorySpark</h1>
        {!isOnline && <div className="offline-indicator">You are offline</div>}
      </header>
      
      <main>
        <div className="view-toggle">
          <button 
            className={`toggle-btn ${activeView === 'all' ? 'active' : ''}`}
            onClick={() => setActiveView('all')}
          >
            All Stories
          </button>
          <button 
            className={`toggle-btn ${activeView === 'downloaded' ? 'active' : ''}`}
            onClick={() => setActiveView('downloaded')}
          >
            Downloaded Stories
          </button>
        </div>
        
        <h2>{activeView === 'downloaded' ? 'Downloaded Stories' : 'All Stories'}</h2>
        
        {activeView === 'downloaded' && displayedStories.length === 0 && (
          <div className="empty-state">
            <p>You haven't downloaded any stories yet.</p>
            <button 
              className="toggle-btn"
              onClick={() => setActiveView('all')}
            >
              Browse Stories
            </button>
          </div>
        )}
        
        <div className="stories-grid">
          {displayedStories.map(story => (
            <div className="story-card" key={story.id}>
              <h3>{story.title}</h3>
              <p>Duration: {story.duration}</p>
              <p>Theme: {story.theme}</p>
              
              <div className="card-actions">
                <button className="read-button">Read Story</button>
                <button 
                  className={`download-button ${story.isDownloaded ? 'downloaded' : ''}`}
                  onClick={() => toggleDownload(story.id)}
                  title={story.isDownloaded ? "Remove Download" : "Download for Offline Use"}
                >
                  {story.isDownloaded ? "Downloaded" : "Download"}
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
      
      <footer>
        <p>&copy; {new Date().getFullYear()} StorySpark</p>
      </footer>
    </div>
  );
}

export default App;
