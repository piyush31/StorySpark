#!/usr/bin/env python3
"""
Test script to verify the complete audio flow in StorySpark
"""
import requests
import json
import sys

def test_story_generation():
    """Test story generation and verify audio path"""
    print("🧪 Testing story generation and audio flow...")
    
    # Test data
    story_params = {
        "theme": "friendship",
        "character_name": "Alex",
        "voice_id": "default",
        "story_length": "short",
        "age_group": "5-8"
    }
    
    try:
        # Test backend directly
        print("📡 Testing backend API directly...")
        backend_url = "http://localhost:5001/api/voice/generate-story"
        response = requests.post(backend_url, json=story_params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Backend API failed with status {response.status_code}")
            return False
            
        backend_data = response.json()
        if backend_data.get('status') != 'success':
            print(f"❌ Backend returned error: {backend_data.get('message', 'Unknown error')}")
            return False
            
        audio_path = backend_data['story']['audio_path']
        print(f"✅ Backend story generated successfully")
        print(f"📁 Audio path: {audio_path}")
        
        # Test frontend proxy
        print("🔄 Testing frontend proxy...")
        frontend_url = "http://localhost:5173/api/voice/generate-story"
        response = requests.post(frontend_url, json=story_params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Frontend proxy failed with status {response.status_code}")
            return False
            
        frontend_data = response.json()
        audio_path_frontend = frontend_data['story']['audio_path']
        print(f"✅ Frontend proxy working correctly")
        print(f"📁 Audio path from frontend: {audio_path_frontend}")
        
        # Test audio file accessibility
        print("🎵 Testing audio file accessibility...")
        
        # Test through backend
        backend_audio_url = f"http://localhost:5001{audio_path}"
        audio_response = requests.head(backend_audio_url, timeout=5)
        if audio_response.status_code == 200:
            print(f"✅ Audio accessible via backend: {backend_audio_url}")
            print(f"📊 Content-Type: {audio_response.headers.get('content-type', 'Unknown')}")
            print(f"📏 Content-Length: {audio_response.headers.get('content-length', 'Unknown')} bytes")
        else:
            print(f"❌ Audio not accessible via backend (status: {audio_response.status_code})")
            return False
        
        # Test through frontend proxy
        frontend_audio_url = f"http://localhost:5173{audio_path}"
        audio_response_frontend = requests.head(frontend_audio_url, timeout=5)
        if audio_response_frontend.status_code == 200:
            print(f"✅ Audio accessible via frontend proxy: {frontend_audio_url}")
        else:
            print(f"❌ Audio not accessible via frontend proxy (status: {audio_response_frontend.status_code})")
            return False
        
        print("\n🎉 All tests passed! Audio flow is working correctly.")
        print(f"📖 Story title: {backend_data['story']['title']}")
        print(f"🎭 Theme: {backend_data['story']['theme']}")
        print(f"⏱️  Duration: {backend_data['story']['duration']}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_story_generation()
    sys.exit(0 if success else 1)
