# Voice Service Documentation

## Overview

The StorySpark Voice Service provides functionality for text-to-speech conversion and sound effect management, specifically designed for generating narrated stories for children. The service is structured to support the voice-first approach outlined in the wireframe specifications.

## Key Components

### 1. Voice Service (`voice_service.py`)

The core voice processing service that handles:

- Text-to-speech conversion
- Sound effect management
- Audio sequencing and combining

#### Key Classes and Functions

- `SoundItem`: Represents a single audio component (speech or sound effect)
- `VoiceService`: Main service for voice processing
  - `text_to_speech()`: Converts text to spoken audio
  - `get_sound_effect()`: Retrieves sound effect files
  - `process_sound_sequence()`: Combines multiple audio elements

### 2. Story Generator (`story_generator.py`)

Service for generating and narrating stories, using the voice service:

- Generates story content based on parameters
- Creates structured audio sequences
- Estimates story duration

#### Key Functions

- `generate_story()`: Creates a new story based on theme, characters, etc.
- `narrate_existing_story()`: Generates audio for an existing story

### 3. Voice API (`voice_api.py`)

API endpoints for voice-related features:

- `/api/voice/generate-story`: Generates a new story
- `/api/voice/narrate-story/<story_id>`: Creates narration for existing story
- `/api/voice/available-voices`: Lists available voice profiles
- `/api/voice/available-sound-effects`: Lists available sound effects

## Data Structures

### Sound Item

```python
{
    "sound_type": "human" | "effect",  # Type of sound
    "content": str,  # Text to speak or name of sound effect
    "emotion": str,  # Emotional tone (for human voice)
    "pause_after": float,  # Seconds to pause after this item
    "volume": float  # Volume level (0.0 to 1.0)
}
```

### Story Data

```python
{
    "id": int,  # Unique story ID
    "title": str,  # Story title
    "text": str,  # Full story text
    "audio_path": str,  # Path to audio file
    "duration": str,  # Estimated duration (e.g., "5 minutes")
    "theme": str,  # Theme or moral of the story
    "age_group": str,  # Target age range
    "language": str,  # Primary language
    "created_by": str,  # Child's name if co-created
    "created_at": str,  # Timestamp
    "is_downloadable": bool  # Whether story can be downloaded
}
```

## Implementation Status

**IMPORTANT**: The voice service implementation is currently a placeholder. The following components need to be implemented:

1. **Text-to-Speech API Integration**:
   - The `text_to_speech()` method needs to be connected to a real TTS API service
   - Options include Google Cloud TTS, Amazon Polly, or Microsoft Azure

2. **Sound Effect Processing**:
   - The `process_sound_sequence()` method needs to be implemented
   - This requires audio file manipulation (combining, adjusting volume, adding pauses)
   - Consider using `pydub` or similar Python audio libraries

3. **Story Generation Integration**:
   - The story generation features need to be connected to an AI service
   - Options include OpenAI GPT, Google PaLM, or Anthropic Claude

## Usage Examples

### Generating a Story

```python
from services.voice_service import story_generator

# Generate a simple story
story = story_generator.generate_story(
    theme="kindness",
    setting="forest",
    duration="short",
    age_group="5-8"
)

# Access the generated audio
audio_path = story["audio_path"]
```

### Creating a Sound Sequence

```python
from services.voice_service import voice_service, SoundItem

# Create a sequence of sounds
sequence = [
    SoundItem(sound_type="effect", content="magic", volume=0.7),
    SoundItem(sound_type="human", content="Once upon a time...", emotion="calm"),
    SoundItem(sound_type="effect", content="forest", pause_after=1.0)
]

# Process the sequence into a single audio file
audio_path = voice_service.process_sound_sequence(sequence)
```
