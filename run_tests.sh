#!/bin/bash

# Run the unit tests for the StorySpark backend
echo "Running StorySpark backend unit tests..."

# Change to the backend directory
cd "$(dirname "$0")/backend"

# Run all tests in the tests directory
python -m unittest discover -s tests

# Check if the tests were successful
if [ $? -eq 0 ]; then
  echo "✅ All tests passed!"
else
  echo "❌ Some tests failed. See the output above for details."
  exit 1
fi
