# Simple Flask server for testing story generation
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    logger.info("Environment variables available: " + ", ".join([k for k in os.environ.keys() if not k.startswith("_")]))
else:
    logger.info(f"GEMINI_API_KEY found with length: {len(GEMINI_API_KEY)}")
    
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
else:
    logger.warning("Skipping Gemini API configuration due to missing API key")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Gemini model
try:
    gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    logger.info("Gemini model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")
    gemini_model = None

def build_story_prompt(
    theme=None,
    characters=None,
    setting=None,
    duration_minutes="5-10",
    age_group="5-8",
    language="en",
    child_name=None
) -> str:
    """Build a prompt for the Gemini model to generate a story"""
    # Base prompt
    prompt = f"""Write a children's story for age group {age_group} years that would take about {duration_minutes} minutes to read aloud.
    """
    
    # Add theme if provided
    if theme:
        prompt += f"The story should be about {theme} and teach the value of {theme}. "
    
    # Add setting if provided
    if setting:
        prompt += f"The story should take place in a {setting}. "
    
    # Add characters if provided
    if characters and len(characters) > 0:
        chars_str = ', '.join(characters)
        prompt += f"Include these characters: {chars_str}. "
    
    # Add child name for personalization if provided
    if child_name:
        prompt += f"Make {child_name} the main character or mention {child_name} in the story. "
    
    # Add formatting instructions
    prompt += """
    Make the story engaging, age-appropriate, and with a clear beginning, middle, and end.
    Use simple language that children can understand.
    Divide the story into paragraphs for better readability.
    Start with a title on the first line prefixed with "Title: ".
    
    The story should convey positive values and end with a meaningful lesson.
    """
    
    return prompt

def parse_story_content(content, theme=None, setting=None):
    """Parse the generated content into title and story text"""
    # Default fallback values
    default_title = f"The Adventure of {theme or 'Kindness'}"
    if setting:
        default_title += f" in the {setting}"
        
    try:
        # Check if content starts with "Title: " format
        if "Title:" in content and content.index("Title:") < 20:
            parts = content.split("\n", 1)
            title = parts[0].replace("Title:", "").strip()
            story_text = parts[1].strip() if len(parts) > 1 else ""
        else:
            # Try to find a logical title from the first line
            lines = content.split("\n")
            if len(lines[0]) < 100 and not lines[0].startswith("Once upon"):
                title = lines[0].strip()
                story_text = "\n".join(lines[1:]).strip()
            else:
                # Couldn't find a clear title
                title = default_title
                story_text = content
                
        # If either is empty, use defaults
        if not title:
            title = default_title
        if not story_text:
            story_text = f"Once upon a time, in a {setting or 'magical land'}, there lived..."
            
        return title, story_text
        
    except Exception as e:
        logger.error(f"Error parsing story content: {str(e)}")
        return default_title, content

@app.route('/api/test-gemini', methods=['GET'])
def test_gemini():
    """Simple endpoint to test if Gemini API is working"""
    try:
        if not gemini_model:
            return jsonify({
                'status': 'error', 
                'message': 'Gemini model not initialized'
            }), 500
            
        response = gemini_model.generate_content("Write a very short greeting")
        return jsonify({
            'status': 'success',
            'message': 'Gemini API is working',
            'response': response.text
        })
    except Exception as e:
        logger.error(f"Error testing Gemini API: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/voice/generate-story', methods=['POST'])
def generate_story():
    """Generate a story based on given parameters"""
    try:
        # Get request data
        data = request.json or {}
        
        # Convert duration to minutes
        duration = data.get('duration', 'medium')
        duration_minutes = {"short": "3-5", "medium": "5-10", "long": "10-15"}.get(duration, "5-10")
        
        # Log request parameters
        logger.info(f"Generating story with theme: {data.get('theme')}, age: {data.get('age_group')}")
        
        if not gemini_model:
            logger.warning("Using placeholder story due to Gemini API not being available")
            # Generate a placeholder story for testing purposes
            theme = data.get('theme', 'kindness')
            setting = data.get('setting', 'magical forest')
            age_group = data.get('age_group', '5-8')
            child_name = data.get('child_name', 'Alex')
            
            if child_name:
                story_title = f"{child_name}'s Adventure in the {setting.title()}"
                story_text = f"""Once upon a time, there was a child named {child_name} who lived near a {setting}. 
                
{child_name} was known for their {theme}. Every day, {child_name} would help the animals in the forest.

One day, {child_name} met a wise old owl who said, "Your {theme} is a gift. Use it wisely."

{child_name} learned that being {theme} made everyone happy, including themselves.

And they all lived happily ever after."""
            else:
                story_title = f"The Power of {theme.title()} in the {setting.title()}"
                story_text = f"""Once upon a time, in a beautiful {setting}, there lived many creatures who learned about {theme}.

They discovered that {theme} made their lives better in many ways.

The wise old owl taught everyone that {theme} was the most important value of all.

And from that day forward, {theme} filled the {setting} with joy and happiness.

The end."""
                
            # Create a test story response
            story_data = {
                "id": 12345,
                "title": story_title,
                "text": story_text,
                "audio_path": "/static/placeholders/story_audio.mp3",
                "duration": f"{duration_minutes} minutes",
                "theme": theme,
                "age_group": age_group,
                "language": data.get('language', 'en'),
                "created_at": "2023-01-01T00:00:00Z"
            }
            
            return jsonify({
                'status': 'success',
                'story': story_data
            })
            
        # If we have a valid Gemini model, continue with real generation
        logger.info("Using Gemini API for story generation")
        
        # Build the prompt
        prompt = build_story_prompt(
            theme=data.get('theme'),
            characters=data.get('characters'),
            setting=data.get('setting'),
            duration_minutes=duration_minutes,
            age_group=data.get('age_group', '5-8'),
            language=data.get('language', 'en'),
            child_name=data.get('child_name')
        )
        
        logger.info(f"Sending prompt to Gemini: {prompt[:100]}...")
        
        try:
            # Generate story using Gemini
            story_response = gemini_model.generate_content(prompt)
            story_content = story_response.text
            
            logger.info(f"Received response from Gemini: {len(story_content)} characters")
            
            # Extract title and text
            story_title, story_text = parse_story_content(
                story_content, 
                theme=data.get('theme'), 
                setting=data.get('setting')
            )
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            logger.warning("Falling back to placeholder story")
            
            # Generate a placeholder story for testing purposes
            theme = data.get('theme', 'kindness')
            setting = data.get('setting', 'magical forest')
            child_name = data.get('child_name', 'Alex')
            
            if child_name:
                story_title = f"{child_name}'s Adventure in the {setting.title()}"
                story_text = f"""Once upon a time, there was a child named {child_name} who lived near a {setting}. 
                
{child_name} was known for their {theme}. Every day, {child_name} would help the animals in the forest.

One day, {child_name} met a wise old owl who said, "Your {theme} is a gift. Use it wisely."

{child_name} learned that being {theme} made everyone happy, including themselves.

And they all lived happily ever after."""
            else:
                story_title = f"The Power of {theme.title()} in the {setting.title()}"
                story_text = f"""Once upon a time, in a beautiful {setting}, there lived many creatures who learned about {theme}.

They discovered that {theme} made their lives better in many ways.

The wise old owl taught everyone that {theme} was the most important value of all.

And from that day forward, {theme} filled the {setting} with joy and happiness.

The end."""
        
        # Create response data
        story_data = {
            "id": 12345,  # Dummy ID
            "title": story_title,
            "text": story_text,
            "audio_path": "/static/dummy_audio.mp3",  # Dummy path
            "duration": f"{duration_minutes} minutes",
            "theme": data.get('theme'),
            "age_group": data.get('age_group', '5-8'),
            "language": data.get('language', 'en'),
            "created_at": "2023-01-01T00:00:00Z"  # Dummy timestamp
        }
        
        return jsonify({
            'status': 'success',
            'story': story_data
        })
        
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5003)
