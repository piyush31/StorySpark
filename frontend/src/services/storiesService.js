// Service to handle story data and caching
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

  // Mark a story as downloaded for offline use
  markAsDownloaded(storyId) {
    const stories = this.getCachedStories();
    const updatedStories = stories.map(story => {
      if (story.id === storyId) {
        return { ...story, isDownloaded: true };
      }
      return story;
    });
    
    this.cacheStories(updatedStories);
    return updatedStories;
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
}

export default new StoriesService();
