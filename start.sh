#!/bin/bash

echo "🏎️  F1 G-Force Sculpture Gallery"
echo "================================"
echo ""

# Start the backend
echo "Starting FastAPI backend on port 8000..."
cd backend
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start the frontend
echo "Starting frontend server on port 3000..."
cd ../frontend
python -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "✅ Both servers are running!"
echo ""
echo "Backend API: http://localhost:8000"
echo "Frontend:    http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT

wait
