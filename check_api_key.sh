#!/bin/zsh
# Check environment variables for Gemini API key

echo "Checking for GEMINI_API_KEY in environment variables..."

if [[ -n "${GEMINI_API_KEY}" ]]; then
  echo "GEMINI_API_KEY is set in the environment with length: ${#GEMINI_API_KEY}"
  
  # Check if it's a valid key format (basic check)
  if [[ "${GEMINI_API_KEY}" =~ ^AI[a-zA-Z0-9_-]{39}$ ]]; then
    echo "Key format appears valid (starts with 'AI' and has correct length)"
  else
    echo "Warning: Key format may not be valid. Check if it's a proper Gemini API key."
  fi
else
  echo "GEMINI_API_KEY is not set in the environment"
  
  # Check if it exists in .zshrc
  if grep -q "GEMINI_API_KEY" ~/.zshrc; then
    echo "GEMINI_API_KEY is defined in ~/.zshrc but not loaded in current shell"
    echo "Try running: source ~/.zshrc"
  else
    echo "GEMINI_API_KEY is not defined in ~/.zshrc"
  fi
fi

echo "Available environment variables starting with G:"
env | grep "^G" | sort
