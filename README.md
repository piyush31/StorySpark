# StorySpark

StorySpark is a full-stack Progressive Web App (PWA) for interactive storytelling. It features a Python Flask backend API and a React frontend with offline capabilities.

## Features

- **Voice-Enabled Storytelling**: Uses Google's Chirp text-to-speech technology for natural-sounding narration
- **AI-Powered Stories**: Generates unique stories using Google's Gemini 2.0-flash model
- **Child-Friendly Interface**: Designed specifically for children with appropriate UI elements
- **Offline Capabilities**: Stories can be saved for offline use
- **PWA Support**: Can be installed on devices as a Progressive Web App
- **Voice Characters**: Features different storyteller voices like "Dadi Maa" for an authentic experience
- **Indian Cultural Elements**: Incorporates Indian values and cultural references
- **Advanced Audio Processing**: Combines multiple audio clips with emotion-appropriate narration
- **Interactive Storyteller Animation**: Visual storyteller character with expressions that sync to audio
- **Waveform Visualization**: Audio visualizations to enhance the listening experience
- **User Authentication**: Register, login, and user profile management
- **Story Management**: Save, view, and manage user-generated stories

## Latest Updates

- **User Authentication System**: Implemented JWT-based authentication with refresh tokens
- **User Profile Management**: Create and edit user preferences
- **Story Saving**: Save generated stories to your account
- **My Stories View**: View and manage your previously generated stories
- **Enhanced Audio Processing**: Improved audio handling with fade effects and duration calculation
- **Unit Tests**: Added unit tests for AI integration

## Project Structure

```
StorySpark/
├── backend/           # Flask API
│   ├── app.py         # Main Flask application
│   ├── requirements.txt
│   ├── credentials/   # Google Cloud credentials
│   ├── models/        # Database models
│   ├── routes/        # API routes
│   ├── services/      # Business logic services
│   │   └── voice_service/ # Voice and story generation services
│   │       ├── voice_service.py # TTS with Google Cloud
│   │       ├── story_generator.py # Story generation with Gemini
│   │       └── audio_processor.py # Audio processing utilities
│   └── static/        # Static files and generated audio
│       ├── effects/   # Sound effects
│       ├── generated/ # Generated audio files
│       └── placeholders/ # Placeholder audio files
├── frontend/          # React PWA
│   ├── public/        # Static assets
│   ├── src/           # React components
│   │   ├── components/# UI components
│   │   │   ├── AudioPlayer.jsx # Enhanced audio player with waveform
│   │   │   └── StoryTeller.jsx # Animated storyteller character
│   │   ├── data/      # Theme data
│   │   └── services/  # API services
│   ├── index.html     # HTML entry point
│   └── vite.config.js # Vite configuration
├── .env               # Environment variables
├── dev.sh             # Development script
├── setup_sound_effects.py # Script to set up sound effects
└── test_audio_processing.py # Test script for audio processing
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- Google Gemini API key
- Google Cloud service account with TTS permissions

### API Keys Setup

1. Create a `.env` file in the root directory with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_CLOUD_PROJECT=your_google_cloud_project_id
   ```

2. Place your Google Cloud service account credentials in:
   ```
   backend/credentials/google_cloud_credentials.json
   ```

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the Flask app:
   ```
   python app.py
   ```
   The API will be available at http://localhost:5000

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```
   The app will be available at http://localhost:3000

### Setup Sound Effects

1. Run the sound effects setup script:
   ```
   python setup_sound_effects.py
   ```

   This will create synthetic sound effects for development. To recreate all effects:
   ```
   python setup_sound_effects.py --force
   ```

### Testing Audio Processing

1. Run the audio processing test script:
   ```
   python test_audio_processing.py
   ```

   This will test the audio combination and processing functionality.

## Running the Tests

To run the unit tests for the backend:

```bash
./run_tests.sh
```

## Pending Tasks

1. **Multi-language Support**: Add support for additional languages beyond English
2. **Parent Dashboard**: Create analytics dashboard for parents to track story usage
3. **Cultural and Language Options**: Add more cultural themes and language variations
4. **Enhanced Story Customization**: Allow more parameters for story customization
5. **Mobile Optimizations**: Further improve the mobile experience
6. **Story Sharing**: Allow users to share stories with others
7. **Voice Selection Improvements**: Add preview for different voices
8. **Pronunciation Improvements**: Add custom pronunciation dictionaries for proper names

## Development Workflow

1. Start the development environment using the dev script:
   ```
   ./dev.sh
   ```

   This will start both the backend and frontend servers.

2. To run just the backend:
   ```
   cd backend
   python app.py
   ```

3. To run just the frontend:
   ```
   cd frontend
   npm start
   ```

## PWA Features

- Offline access to previously loaded stories
- Installable on supported devices
- Responsive design for mobile and desktop

## Audio Processing Features

The StorySpark app includes advanced audio processing capabilities:

- **Multiple Audio Clips**: Combines narration with sound effects
- **Emotion-Based Narration**: Adjusts speech patterns based on story emotion
- **Audio Visualization**: Displays audio waveforms during playback
- **Synchronized Animation**: Storyteller character animates in sync with audio
- **Dynamic Volume Control**: Adjust volume levels for different audio elements
- **Fade Effects**: Smooth audio transitions between segments
- **Paragraph-Level Processing**: Each paragraph can have its own emotion and sound effects

## API Endpoints

- `GET /api/stories`: Get all available stories
- `POST /api/voice/generate-story`: Generate a new story with voice narration
- `GET /api/voice/available-voices`: Get list of available voice profiles
- `GET /api/voice/available-sound-effects`: Get list of available sound effects

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: React, Vite
- **PWA**: Workbox, Vite PWA Plugin
- **Audio Processing**: pydub
- **TTS**: Google Cloud Text-to-Speech (Chirp)
- **AI**: Google Gemini 2.0-flash
