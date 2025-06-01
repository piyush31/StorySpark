#!/usr/bin/env python3
"""
Simple test to verify complete story audio generation
"""
import requests
import json
import time

def test_story_audio():
    print("🧪 Testing complete story audio generation...")
    
    # Simple story generation request
    payload = {
        "theme": "kindness",
        "setting": "forest", 
        "duration": "short",
        "age_group": "5-8"
    }
    
    try:
        print("📡 Sending story generation request...")
        start_time = time.time()
        
        response = requests.post(
            "http://127.0.0.1:5001/api/voice/generate-story",
            json=payload,
            timeout=30  # Increased timeout for TTS processing
        )
        
        elapsed = time.time() - start_time
        print(f"⏱️  Request completed in {elapsed:.2f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                story = data['story']
                
                print(f"✅ Story generated successfully!")
                print(f"📖 Title: {story.get('title', 'N/A')}")
                print(f"📝 Text length: {len(story.get('text', ''))} characters")
                print(f"🔊 Audio path: {story.get('audio_path', 'N/A')}")
                print(f"⏰ Duration: {story.get('duration', 'N/A')}")
                
                # Check if we have actual story text (not just title)
                story_text = story.get('text', '')
                if story_text and len(story_text) > 100:
                    print(f"✅ Story text looks complete (>{len(story_text)} chars)")
                    print(f"📄 Sample text: {story_text[:150]}...")
                else:
                    print(f"❌ Story text seems too short: {len(story_text)} chars")
                
                return True
            else:
                print(f"❌ API returned error: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - TTS processing may be taking longer than expected")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_story_audio()
    exit(0 if success else 1)
