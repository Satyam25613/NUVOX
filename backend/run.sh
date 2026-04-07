#!/bin/bash
# Start script for NUVOX Backend

cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "Starting NUVOX Server on http://localhost:8000"
echo "➔ UI is available at: http://localhost:8000/index.html"
echo ""

# Run uvicorn server
uvicorn main:app --port 8000
