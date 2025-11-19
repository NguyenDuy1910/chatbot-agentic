#!/bin/bash

# Development Mode Starter Script
# This script starts the application with authentication disabled for easy development

echo "🚀 Starting application in DEVELOPMENT MODE (Auth Disabled)"
echo "⚠️  WARNING: This should only be used in local development!"
echo ""

# Set the environment variable
export DISABLE_AUTH=true

# Navigate to the service directory
cd finx-ai-service

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "✓ Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠  No virtual environment found. Using system Python."
fi

# Display configuration
echo ""
echo "Configuration:"
echo "  DISABLE_AUTH=true"
echo "  Mock User: dev@example.com (Admin)"
echo ""
echo "Starting server..."
echo ""

# Start the application
python run.py
