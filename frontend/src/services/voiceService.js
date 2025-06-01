// Voice service for handling text-to-speech and story narration
import axios from 'axios';
import { getToken } from './authService';
import { API_BASE_URL, STATIC_BASE_URL } from './config';

class VoiceService {
  constructor() {
    this.API_URL = `${API_BASE_URL}/voice`;
    this.AUDIO_CACHE_PREFIX = 'storyspark_audio_';
  }

  /**
   * Get the headers for API requests, including auth token if available
   * @returns {Object} - Headers object
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json'
    };
    
    const token = getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  /**
   * Generate a story with voice narration
   * @param {Object} storyParams - Story generation parameters
   * @returns {Promise<Object>} - The generated story with audio data
   */
  async generateStory(storyParams) {
    try {
      console.log('Generating story with parameters:', storyParams);
      
      // Add timestamp for caching prevention
      const timestamp = Date.now();
      
      const response = await axios.post(
        `${this.API_URL}/generate-story?t=${timestamp}`, 
        storyParams,
        { headers: this.getHeaders() }
      );
      
      if (response.status !== 200) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      // Check if the request was successful
      if (response.data.status !== 'success') {
        throw new Error(response.data.message || 'Failed to generate story');
      }
      
      console.log('Story generated successfully:', response.data.story);
      
      // Get the story data and ensure it has all required fields
      const storyData = response.data.story;
      
      // The backend now returns properly formatted paths starting with '/'
      // No additional processing needed for paths starting with '/'
      if (storyData.audio_path) {
        console.log('Audio path from backend:', storyData.audio_path);
      }
      
      // Return the story data
      return storyData;
    } catch (error) {
      console.error('Error generating story:', error);
      throw error;
    }
  }

  /**
   * Get available voice profiles
   * @returns {Promise<Array>} - List of available voice profiles
   */
  async getAvailableVoices() {
    try {
      const response = await axios.get(`${this.API_URL}/available-voices`, {
        headers: this.getHeaders()
      });
      
      if (response.status !== 200 || response.data.status !== 'success') {
        throw new Error('Failed to fetch voice profiles');
      }
      
      return response.data.voices;
    } catch (error) {
      console.error('Error fetching voice profiles:', error);
      
      // Return default voices if API call fails
      return [
        { id: "dadi", name: "Dadi Maa", gender: "female", age: "elderly", language: "hindi-en" },
        { id: "default", name: "Storyteller", gender: "female", age: "middle", language: "en" }
      ];
    }
  }

  /**
   * Get available sound effects
   * @returns {Promise<Array>} - List of available sound effects
   */
  async getAvailableSoundEffects() {
    try {
      const response = await axios.get(`${this.API_URL}/available-sound-effects`, {
        headers: this.getHeaders()
      });
      
      if (response.status !== 200 || response.data.status !== 'success') {
        throw new Error('Failed to fetch sound effects');
      }
      
      return response.data.effects;
    } catch (error) {
      console.error('Error fetching sound effects:', error);
      return []; // Return empty list if API call fails
    }
  }

  /**
   * Preload and cache audio for offline playback
   * @param {string} audioUrl - URL of the audio to preload
   * @param {string} storyId - ID of the associated story
   * @returns {Promise<boolean>} - Whether the preload was successful
   */
  async preloadAudio(audioUrl, storyId) {
    try {
      // Fetch the audio file
      const response = await fetch(audioUrl);
      const audioBlob = await response.blob();
      
      // Store in IndexedDB or localStorage
      localStorage.setItem(`${this.AUDIO_CACHE_PREFIX}${storyId}`, URL.createObjectURL(audioBlob));
      
      return true;
    } catch (error) {
      console.error('Error preloading audio:', error);
      return false;
    }
  }

  /**
   * Get cached audio URL for a story
   * @param {string} storyId - ID of the story
   * @returns {string|null} - Cached audio URL or null if not cached
   */
  getCachedAudioUrl(storyId) {
    return localStorage.getItem(`${this.AUDIO_CACHE_PREFIX}${storyId}`);
  }
}

export default new VoiceService();
