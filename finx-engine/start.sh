#!/bin/bash

echo "======================================"
echo "FinX Engine - Startup Script"
echo "======================================"
echo ""

show_help() {
    echo "Usage: ./start.sh [option]"
    echo ""
    echo "Options:"
    echo "  docker       Start with Docker Compose (recommended)"
    echo "  api          Start API server only"
    echo "  ui           Start Web UI only"
    echo "  dev          Start both API and UI in development mode"
    echo "  stop         Stop Docker Compose services"
    echo "  clean        Stop and remove all Docker containers and volumes"
    echo "  help         Show this help message"
    echo ""
}

start_docker() {
    echo "Starting FinX Engine with Docker Compose..."
    echo ""
    docker-compose up -d
    echo ""
    echo "✅ Services started!"
    echo ""
    echo "Access the application:"
    echo "  - Web UI:  http://localhost:3000"
    echo "  - API:     http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
    echo "Sample PostgreSQL database:"
    echo "  - Host: localhost"
    echo "  - Port: 5432"
    echo "  - Database: sample_db"
    echo "  - User: finx_user"
    echo "  - Password: finx_password"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: ./start.sh stop"
}

start_api() {
    echo "Starting API server..."
    echo ""
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed"
        exit 1
    fi
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    
    echo ""
    echo "✅ Starting API server on http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    
    python api/main.py
}

start_ui() {
    echo "Starting Web UI..."
    echo ""
    
    if ! command -v npm &> /dev/null; then
        echo "❌ Node.js/npm is not installed"
        exit 1
    fi
    
    cd web-ui
    
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    
    echo ""
    echo "✅ Starting Web UI on http://localhost:3000"
    echo ""
    
    npm run dev
}

start_dev() {
    echo "Starting development environment..."
    echo ""
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "❌ Node.js/npm is not installed"
        exit 1
    fi
    
    echo "Starting API server in background..."
    ./start.sh api &
    API_PID=$!
    
    sleep 3
    
    echo "Starting Web UI..."
    ./start.sh ui &
    UI_PID=$!
    
    echo ""
    echo "✅ Development environment started!"
    echo ""
    echo "  - API PID: $API_PID"
    echo "  - UI PID: $UI_PID"
    echo ""
    echo "Press Ctrl+C to stop both services"
    
    trap "kill $API_PID $UI_PID 2>/dev/null" EXIT
    
    wait
}

stop_docker() {
    echo "Stopping Docker Compose services..."
    docker-compose down
    echo "✅ Services stopped"
}

clean_docker() {
    echo "Stopping and cleaning Docker Compose services..."
    docker-compose down -v
    echo "✅ Services stopped and volumes removed"
}

case "$1" in
    docker)
        start_docker
        ;;
    api)
        start_api
        ;;
    ui)
        start_ui
        ;;
    dev)
        start_dev
        ;;
    stop)
        stop_docker
        ;;
    clean)
        clean_docker
        ;;
    help|--help|-h|"")
        show_help
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

