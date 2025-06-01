import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get("GEMINI_API_KEY")
print(f"API key found: {bool(api_key)}")
if not api_key:
    print("No Gemini API key found in environment")
    exit(1)

# Configure Gemini
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Test generation
    response = model.generate_content("Write a very short children's story about kindness")
    print("Success! Generated content:")
    print(response.text)
except Exception as e:
    print(f"Error: {str(e)}")