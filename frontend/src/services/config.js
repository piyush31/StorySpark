/**
 * Configuration for StorySpark services
 */

// API base URL - automatically detects development vs production
// Can be overridden with VITE_API_BASE_URL environment variable for ngrok usage
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (
  process.env.NODE_ENV === 'production' 
    ? '/api' 
    : '/api'  // Use relative path for both environments since we're using Vite proxy
);

// Static assets URL - for accessing audio files and other static content
// Can be overridden with VITE_STATIC_BASE_URL environment variable for ngrok usage
export const STATIC_BASE_URL = import.meta.env.VITE_STATIC_BASE_URL || (
  process.env.NODE_ENV === 'production'
    ? '/static'
    : '/static'  // Use relative path for both environments since we're using Vite proxy
);

// Default storyteller options
export const STORYTELLERS = [
  {
    id: 'dadi-maa',
    name: 'Dadi Maa',
    description: 'Traditional Indian grandmother with a warm, comforting voice',
    language: 'en'
  },
  {
    id: 'adventurer',
    name: 'The Adventurer',
    description: 'Enthusiastic explorer with an exciting tone',
    language: 'en'
  },
  {
    id: 'nature-guide',
    name: 'Nature Guide',
    description: 'Calm and educational nature enthusiast',
    language: 'en'
  }
];

// Available languages
export const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'Hindi' },
  { code: 'es', name: 'Spanish' },
  { code: 'fr', name: 'French' }
];

// Age groups
export const AGE_GROUPS = [
  { id: '3-5', name: '3-5 years' },
  { id: '6-8', name: '6-8 years' },
  { id: '9-12', name: '9-12 years' }
];

// Story durations
export const DURATIONS = [
  { id: 'short', name: 'Short (2-3 mins)' },
  { id: 'medium', name: 'Medium (5-7 mins)' },
  { id: 'long', name: 'Long (10-12 mins)' }
];
