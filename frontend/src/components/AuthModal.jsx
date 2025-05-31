import React, { useState, useEffect } from 'react';
import Login from './Login';
import Register from './Register';
import './Auth.css';

const AuthModal = ({ isOpen, onClose, onAuthSuccess }) => {
  const [activeView, setActiveView] = useState('login');
  
  // Reset to login view when modal opens
  useEffect(() => {
    if (isOpen) {
      setActiveView('login');
    }
  }, [isOpen]);
  
  // Handle successful authentication
  const handleAuthSuccess = (data) => {
    if (onAuthSuccess) {
      onAuthSuccess(data);
    }
    
    if (onClose) {
      onClose();
    }
  };
  
  // Don't render if modal is not open
  if (!isOpen) return null;
  
  return (
    <div className="auth-modal">
      <div className="auth-modal-content">
        <button 
          className="auth-close" 
          onClick={onClose}
          aria-label="Close"
        >
          &times;
        </button>
        
        {activeView === 'login' ? (
          <Login 
            onSuccess={handleAuthSuccess}
            onRegisterClick={() => setActiveView('register')}
          />
        ) : (
          <Register 
            onSuccess={handleAuthSuccess}
            onLoginClick={() => setActiveView('login')}
          />
        )}
      </div>
    </div>
  );
};

export default AuthModal;
