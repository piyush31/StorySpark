import React, { useState } from 'react';
import { register } from '../services/authService';
import './Auth.css';

const Register = ({ onSuccess, onLoginClick }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Prepare registration data
      const userData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName || undefined,
        last_name: formData.lastName || undefined
      };
      
      const result = await register(userData);
      
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (error) {
      setError(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-form-container">
      <h2>Create Account</h2>
      <p className="auth-subtitle">Join StorySpark to create personalized stories</p>
      
      {error && <div className="auth-error">{error}</div>}
      
      <form onSubmit={handleSubmit} className="auth-form">
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="firstName">First Name</label>
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              autoComplete="given-name"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="lastName">Last Name</label>
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              autoComplete="family-name"
            />
          </div>
        </div>
        
        <div className="form-group">
          <label htmlFor="username">Username<span className="required">*</span></label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
            autoComplete="username"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email<span className="required">*</span></label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            autoComplete="email"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password<span className="required">*</span></label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            autoComplete="new-password"
            minLength="8"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password<span className="required">*</span></label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            autoComplete="new-password"
          />
        </div>
        
        <button 
          type="submit" 
          className="auth-button"
          disabled={isLoading}
        >
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>
      
      <div className="auth-footer">
        <p>
          Already have an account?{' '}
          <button 
            className="text-button"
            onClick={onLoginClick}
            type="button"
          >
            Sign In
          </button>
        </p>
      </div>
    </div>
  );
};

export default Register;
