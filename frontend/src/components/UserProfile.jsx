import React, { useState, useEffect } from 'react';
import { 
  getUserProfile, 
  updatePreferences, 
  changePassword,
  logout
} from '../services/authService';
import { LANGUAGES, STORYTELLERS, AGE_GROUPS } from '../services/config';
import './Auth.css';

const UserProfile = () => {
  const [userData, setUserData] = useState(null);
  const [preferences, setPreferences] = useState({});
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [activeTab, setActiveTab] = useState('preferences');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Fetch user data on component mount
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const result = await getUserProfile();
        setUserData(result.user);
        setPreferences(result.preferences || {});
      } catch (error) {
        setError('Failed to load profile data');
        console.error(error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUserData();
  }, []);
  
  // Handle preferences form changes
  const handlePreferencesChange = (e) => {
    const { name, value } = e.target;
    setPreferences({
      ...preferences,
      [name]: value
    });
  };
  
  // Handle password form changes
  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData({
      ...passwordData,
      [name]: value
    });
  };
  
  // Update user preferences
  const handlePreferencesSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    try {
      const result = await updatePreferences(preferences);
      setSuccess('Preferences updated successfully');
      setPreferences(result.preferences);
    } catch (error) {
      setError(error.message || 'Failed to update preferences');
    }
  };
  
  // Change user password
  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    // Validate passwords match
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('New passwords do not match');
      return;
    }
    
    try {
      await changePassword(passwordData.currentPassword, passwordData.newPassword);
      setSuccess('Password changed successfully');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (error) {
      setError(error.message || 'Failed to change password');
    }
  };
  
  // Handle logout
  const handleLogout = () => {
    logout();
  };
  
  if (isLoading) {
    return <div className="profile-container">Loading profile...</div>;
  }
  
  if (!userData) {
    return <div className="profile-container">User not found or not logged in</div>;
  }
  
  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar">
          {userData.first_name ? userData.first_name.charAt(0).toUpperCase() : userData.username.charAt(0).toUpperCase()}
        </div>
        <div className="profile-info">
          <h1>
            {userData.first_name 
              ? `${userData.first_name} ${userData.last_name || ''}`
              : userData.username}
          </h1>
          <p>{userData.email}</p>
        </div>
      </div>
      
      <div className="tab-container">
        <div className="tab-buttons">
          <button 
            className={`tab-button ${activeTab === 'preferences' ? 'active' : ''}`}
            onClick={() => setActiveTab('preferences')}
          >
            Preferences
          </button>
          <button 
            className={`tab-button ${activeTab === 'password' ? 'active' : ''}`}
            onClick={() => setActiveTab('password')}
          >
            Change Password
          </button>
          <button 
            className={`tab-button ${activeTab === 'stories' ? 'active' : ''}`}
            onClick={() => setActiveTab('stories')}
          >
            My Stories
          </button>
        </div>
        
        {/* Preferences Tab */}
        <div className={`tab-panel ${activeTab === 'preferences' ? 'active' : ''}`}>
          {error && <div className="auth-error">{error}</div>}
          {success && <div className="auth-success">{success}</div>}
          
          <form className="preferences-form" onSubmit={handlePreferencesSubmit}>
            <div className="form-group">
              <label htmlFor="preferred_language">Preferred Language</label>
              <select 
                id="preferred_language"
                name="preferred_language"
                value={preferences.preferred_language || ''}
                onChange={handlePreferencesChange}
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="preferred_storyteller">Preferred Storyteller</label>
              <select 
                id="preferred_storyteller"
                name="preferred_storyteller"
                value={preferences.preferred_storyteller || ''}
                onChange={handlePreferencesChange}
              >
                {STORYTELLERS.map(teller => (
                  <option key={teller.id} value={teller.name}>
                    {teller.name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="child_name">Child's Name</label>
              <input 
                type="text"
                id="child_name"
                name="child_name"
                value={preferences.child_name || ''}
                onChange={handlePreferencesChange}
                placeholder="Enter child's name"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="child_age">Child's Age</label>
              <select 
                id="child_age"
                name="child_age"
                value={preferences.child_age || ''}
                onChange={handlePreferencesChange}
              >
                <option value="">Select age group</option>
                {AGE_GROUPS.map(age => (
                  <option key={age.id} value={age.id}>
                    {age.name}
                  </option>
                ))}
              </select>
            </div>
            
            <button type="submit" className="auth-button">
              Save Preferences
            </button>
          </form>
        </div>
        
        {/* Password Change Tab */}
        <div className={`tab-panel ${activeTab === 'password' ? 'active' : ''}`}>
          {error && <div className="auth-error">{error}</div>}
          {success && <div className="auth-success">{success}</div>}
          
          <form className="password-form" onSubmit={handlePasswordSubmit}>
            <div className="form-group">
              <label htmlFor="currentPassword">Current Password</label>
              <input 
                type="password"
                id="currentPassword"
                name="currentPassword"
                value={passwordData.currentPassword}
                onChange={handlePasswordChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="newPassword">New Password</label>
              <input 
                type="password"
                id="newPassword"
                name="newPassword"
                value={passwordData.newPassword}
                onChange={handlePasswordChange}
                required
                minLength="8"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm New Password</label>
              <input 
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={passwordData.confirmPassword}
                onChange={handlePasswordChange}
                required
              />
            </div>
            
            <button type="submit" className="auth-button">
              Change Password
            </button>
          </form>
        </div>
        
        {/* Stories Tab */}
        <div className={`tab-panel ${activeTab === 'stories' ? 'active' : ''}`}>
          <h3>My Stories</h3>
          <p>Your saved stories will appear here.</p>
          {/* We'll implement the stories list in another component */}
        </div>
        
        <div className="profile-actions">
          <button 
            className="auth-button logout-button"
            onClick={handleLogout}
          >
            Log Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
