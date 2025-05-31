import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import storiesService from '../services/storiesService';
import { isLoggedIn } from '../services/authService';
import './UserStories.css';

const UserStories = () => {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  useEffect(() => {
    // Check if user is logged in
    if (!isLoggedIn()) {
      setError("Please log in to view your stories");
      setLoading(false);
      return;
    }
    
    const fetchStories = async () => {
      try {
        // Get user's stories from the service
        const userStories = await storiesService.getUserStories();
        setStories(userStories);
      } catch (err) {
        console.error('Error fetching stories:', err);
        setError('Failed to load your stories. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchStories();
  }, []);

  const handleDeleteStory = async (storyId) => {
    if (window.confirm('Are you sure you want to delete this story?')) {
      try {
        await storiesService.deleteStory(storyId);
        // Remove the deleted story from state
        setStories(stories.filter(story => story.id !== storyId));
      } catch (err) {
        console.error('Error deleting story:', err);
        alert('Failed to delete story. Please try again.');
      }
    }
  };

  const handleToggleView = () => {
    setViewMode(viewMode === 'grid' ? 'list' : 'grid');
  };

  if (loading) {
    return <div className="loading">Loading your stories...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (stories.length === 0) {
    return (
      <div className="empty-state">
        <h2>No Stories Yet</h2>
        <p>You haven't created any stories yet. Generate your first story now!</p>
        <button className="primary-button" onClick={() => window.location.href = '/'}>
          Create a Story
        </button>
      </div>
    );
  }

  return (
    <div className="user-stories-container">
      <div className="stories-header">
        <h2>My Stories</h2>
        <div className="view-toggle">
          <button 
            className={`toggle-btn ${viewMode === 'grid' ? 'active' : ''}`} 
            onClick={handleToggleView}
          >
            Grid View
          </button>
          <button 
            className={`toggle-btn ${viewMode === 'list' ? 'active' : ''}`} 
            onClick={handleToggleView}
          >
            List View
          </button>
        </div>
      </div>

      <div className={`stories-container ${viewMode}`}>
        {stories.map(story => (
          <div className="story-card" key={story.id}>
            <div className="story-info">
              <h3>{story.title}</h3>
              <div className="story-metadata">
                <span>Theme: {story.theme}</span>
                <span>Age: {story.age_group}</span>
                <span>Duration: {story.duration}</span>
                <span>Created: {new Date(story.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            
            <div className="card-actions">
              <button 
                className="read-button" 
                onClick={() => window.location.href = `/story/${story.id}`}
              >
                Read Story
              </button>
              <button 
                className={`download-button ${story.isDownloaded ? 'downloaded' : ''}`}
                onClick={() => storiesService.markAsDownloaded(story.id, story.audio_path)}
                disabled={story.isDownloaded}
              >
                {story.isDownloaded ? 'Downloaded' : 'Save for Offline'}
              </button>
              <button 
                className="delete-button" 
                onClick={() => handleDeleteStory(story.id)}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UserStories;
