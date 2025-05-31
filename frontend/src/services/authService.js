/**
 * Authentication service for StorySpark
 * 
 * Handles user registration, login, and token management
 */
import { API_BASE_URL } from './config';

// Local storage keys
const TOKEN_KEY = 'storyspark_token';
const REFRESH_TOKEN_KEY = 'storyspark_refresh_token';
const USER_KEY = 'storyspark_user';

/**
 * Register a new user
 * @param {Object} userData User registration data
 * @returns {Promise} Promise with registration result
 */
export const register = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Registration failed');
    }

    // Store auth data
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));

    return data;
  } catch (error) {
    console.error('Registration error:', error);
    throw error;
  }
};

/**
 * Log in a user
 * @param {string} usernameOrEmail Username or email
 * @param {string} password User password
 * @returns {Promise} Promise with login result
 */
export const login = async (usernameOrEmail, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username_or_email: usernameOrEmail,
        password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Login failed');
    }

    // Store auth data
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));

    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

/**
 * Log out the current user
 */
export const logout = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  
  // Reload the page to clear state
  window.location.href = '/';
};

/**
 * Get the current user from local storage
 * @returns {Object|null} User object or null if not logged in
 */
export const getCurrentUser = () => {
  const userStr = localStorage.getItem(USER_KEY);
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Check if user is logged in
 * @returns {boolean} True if user is logged in
 */
export const isLoggedIn = () => {
  return !!localStorage.getItem(TOKEN_KEY);
};

/**
 * Get the authentication token
 * @returns {string|null} JWT token or null
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Refresh the access token
 * @returns {Promise} Promise with new access token
 */
export const refreshToken = async () => {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`,
        'Content-Type': 'application/json',
      }
    });

    const data = await response.json();

    if (!response.ok) {
      // If refresh fails, log out
      logout();
      throw new Error(data.message || 'Token refresh failed');
    }

    // Update token in storage
    localStorage.setItem(TOKEN_KEY, data.access_token);
    
    return data.access_token;
  } catch (error) {
    console.error('Token refresh error:', error);
    throw error;
  }
};

/**
 * Get the current user's profile from the API
 * @returns {Promise} Promise with user profile data
 */
export const getUserProfile = async () => {
  try {
    const token = getToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Failed to get user profile');
    }

    // Update local user data
    localStorage.setItem(USER_KEY, JSON.stringify(data.user));
    
    return data;
  } catch (error) {
    console.error('Get profile error:', error);
    throw error;
  }
};

/**
 * Update user preferences
 * @param {Object} preferences User preferences
 * @returns {Promise} Promise with updated preferences
 */
export const updatePreferences = async (preferences) => {
  try {
    const token = getToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/auth/me/preferences`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(preferences),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Failed to update preferences');
    }
    
    return data;
  } catch (error) {
    console.error('Update preferences error:', error);
    throw error;
  }
};

/**
 * Change user password
 * @param {string} currentPassword Current password
 * @param {string} newPassword New password
 * @returns {Promise} Promise with result
 */
export const changePassword = async (currentPassword, newPassword) => {
  try {
    const token = getToken();
    
    if (!token) {
      throw new Error('Not authenticated');
    }
    
    const response = await fetch(`${API_BASE_URL}/auth/me/password`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Failed to change password');
    }
    
    return data;
  } catch (error) {
    console.error('Password change error:', error);
    throw error;
  }
};
