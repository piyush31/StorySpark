// Service to handle story data and caching
import voiceService from './voiceService';
import { getToken, isLoggedIn } from './authService';
import { API_BASE_URL } from './config';

class StoriesService {
  constructor() {
    this.CACHE_KEY = 'storyspark_stories_cache';
    this.API_URL = '/api/stories';
  }

  // Fetch stories from API
  async fetchStories() {
    try {
      const response = await fetch(this.API_URL);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const stories = await response.json();
      
      // Cache the stories for offline use
      this.cacheStories(stories);
      
      return stories;
    } catch (error) {
      console.error('Error fetching stories:', error);
      
      // If fetch fails, try to get stories from cache
      return this.getCachedStories();
    }
  }

  // Save stories to local storage
  cacheStories(stories) {
    try {
      localStorage.setItem(this.CACHE_KEY, JSON.stringify(stories));
    } catch (error) {
      console.error('Error caching stories:', error);
    }
  }

  // Get stories from local storage
  getCachedStories() {
    try {
      const cachedStories = localStorage.getItem(this.CACHE_KEY);
      return cachedStories ? JSON.parse(cachedStories) : [];
    } catch (error) {
      console.error('Error reading cached stories:', error);
      return [];
    }
  }

  // Generate a new story
  async generateStory(storyParams) {
    try {
      // Use the voice service to generate the story
      const storyData = await voiceService.generateStory(storyParams);
      
      // Add the story to cache
      const stories = this.getCachedStories();
      stories.push(storyData);
      this.cacheStories(stories);
      
      return storyData;
    } catch (error) {
      console.error('Error generating story:', error);
      throw error;
    }
  }

  // Mark a story as downloaded for offline use
  async markAsDownloaded(storyId, audioUrl) {
    try {
      // Use the voice service to preload the audio
      if (audioUrl) {
        await voiceService.preloadAudio(audioUrl, storyId);
      }
      
      const stories = this.getCachedStories();
      const updatedStories = stories.map(story => {
        if (story.id === storyId) {
          return { ...story, isDownloaded: true };
        }
        return story;
      });
      
      this.cacheStories(updatedStories);
      return updatedStories;
    } catch (error) {
      console.error('Error marking story as downloaded:', error);
      throw error;
    }
  }

  // Remove a story from downloaded list
  removeDownload(storyId) {
    const stories = this.getCachedStories();
    const updatedStories = stories.map(story => {
      if (story.id === storyId) {
        return { ...story, isDownloaded: false };
      }
      return story;
    });
    
    this.cacheStories(updatedStories);
    return updatedStories;
  }

  // Get only downloaded stories
  getDownloadedStories() {
    const stories = this.getCachedStories();
    return stories.filter(story => story.isDownloaded);
  }

  // Get all stories for the logged-in user
  async getUserStories() {
    try {
      if (!isLoggedIn()) {
        throw new Error('User not authenticated');
      }
      
      const token = getToken();
      const response = await fetch(`${API_BASE_URL}/stories/my-stories`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to fetch stories');
      }
      
      const data = await response.json();
      return data.stories;
    } catch (error) {
      console.error('Error fetching user stories:', error);
      throw error;
    }
  }
  
  // Get a specific story by ID
  async getStoryById(storyId) {
    try {
      const token = getToken();
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      
      const response = await fetch(`${API_BASE_URL}/stories/${storyId}`, {
        method: 'GET',
        headers
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to fetch story');
      }
      
      const data = await response.json();
      return data.story;
    } catch (error) {
      console.error(`Error fetching story ${storyId}:`, error);
      throw error;
    }
  }
  
  // Delete a story by ID
  async deleteStory(storyId) {
    try {
      if (!isLoggedIn()) {
        throw new Error('User not authenticated');
      }
      
      const token = getToken();
      const response = await fetch(`${API_BASE_URL}/stories/${storyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to delete story');
      }
      
      return true;
    } catch (error) {
      console.error(`Error deleting story ${storyId}:`, error);
      throw error;
    }
  }
}

export default new StoriesService();
