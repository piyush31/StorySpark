import React, { useState, useEffect, useRef } from 'react';
import './StoryTeller.css';

// Expressions for the storyteller
const EXPRESSIONS = {
  NEUTRAL: 'neutral',
  HAPPY: 'happy', 
  EXCITED: 'excited',
  THINKING: 'thinking',
  SPEAKING: 'speaking',
  SAD: 'sad',
  SCARED: 'scared',
  MYSTERIOUS: 'mysterious'
};

const StoryTeller = ({ 
  isActive, 
  mood = EXPRESSIONS.NEUTRAL,
  audioRef = null,
  storyText = '',
  name = 'Dadi Maa'
}) => {
  const [expression, setExpression] = useState(mood);
  const [blinking, setBlinking] = useState(false);
  const [currentMood, setCurrentMood] = useState(mood);
  const lastBlinkTime = useRef(Date.now());
  const lastExpressionChange = useRef(Date.now());
  
  // Effect for audio sync - detect audio playback and sync expressions
  useEffect(() => {
    if (!audioRef || !audioRef.current) return;
    
    const audio = audioRef.current;
    
    const syncWithAudio = () => {
      if (audio.paused) {
        setExpression(EXPRESSIONS.NEUTRAL);
        return;
      }
      
      // If we're playing, alternate between speaking and the current mood
      const now = Date.now();
      if (now - lastExpressionChange.current > 1500) {
        setExpression(prev => 
          prev === EXPRESSIONS.SPEAKING ? currentMood : EXPRESSIONS.SPEAKING
        );
        lastExpressionChange.current = now;
      }
    };
    
    const audioInterval = setInterval(syncWithAudio, 500);
    
    return () => {
      clearInterval(audioInterval);
    };
  }, [audioRef, currentMood]);
  
  // Change expressions randomly while active
  useEffect(() => {
    if (!isActive) {
      setExpression(EXPRESSIONS.NEUTRAL);
      return;
    }
    
    // Random expression changes when active
    const expressionInterval = setInterval(() => {
      if (Math.random() > 0.7) {
        // 30% chance to change expression
        // Pick emotion from text if available
        let newMood = detectMoodFromText(storyText) || mood;
        
        setCurrentMood(newMood);
        // Only change if we're not speaking
        if (expression !== EXPRESSIONS.SPEAKING) {
          setExpression(newMood);
        }
      }
    }, 4000);
    
    // Blinking effect
    const blinkInterval = setInterval(() => {
      const now = Date.now();
      if (now - lastBlinkTime.current > 3000) {
        setBlinking(true);
        setTimeout(() => setBlinking(false), 200);
        lastBlinkTime.current = now;
      }
    }, 200);
    
    return () => {
      clearInterval(expressionInterval);
      clearInterval(blinkInterval);
    };
  }, [isActive, expression, storyText, mood]);
  
  // Simple mood detection from text
  const detectMoodFromText = (text) => {
    if (!text) return null;
    
    const sampleText = text.slice(0, 500).toLowerCase();
    
    if (/happy|joy|laugh|smile|celebration/i.test(sampleText)) {
      return EXPRESSIONS.HAPPY;
    } else if (/scary|afraid|fear|dark|monster/i.test(sampleText)) {
      return EXPRESSIONS.SCARED;
    } else if (/sad|cry|tear|unhappy|sorry/i.test(sampleText)) {
      return EXPRESSIONS.SAD;
    } else if (/exciting|amazing|wow|incredible|adventure/i.test(sampleText)) {
      return EXPRESSIONS.EXCITED;
    } else if (/mysterious|secret|unknown|magic|wonder/i.test(sampleText)) {
      return EXPRESSIONS.MYSTERIOUS;
    }
    
    return EXPRESSIONS.NEUTRAL;
  };
  
  return (
    <div className={`storyteller ${isActive ? 'active' : ''}`}>
      <div className="storyteller-container">
        <div className={`storyteller-face expression-${expression} ${blinking ? 'blinking' : ''}`}>
          <div className="face-element hair"></div>
          <div className="face-element face"></div>
          <div className="face-element eyes"></div>
          <div className="face-element mouth"></div>
          <div className="face-element bindi"></div>
          <div className="face-element glasses"></div>
        </div>
      </div>
      <div className="storyteller-name">{name}</div>
    </div>
  );
};

export default StoryTeller;
export { EXPRESSIONS };
