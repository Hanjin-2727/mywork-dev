#!/usr/bin/env bash
# ==============================================================================
# [우리단지 ON] PWA Web App Launcher
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

PORT=8080

# Check if port is already in use
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port $PORT is already in use. Opening browser..."
else
    echo "🚀 Starting PWA Server on http://localhost:$PORT ..."
    python3 "$DIR/server.py" &
    SERVER_PID=$!
    sleep 1
fi

# Open Chrome in App mode or standard mode
if command -v google-chrome &> /dev/null; then
    google-chrome --app="http://localhost:$PORT" &
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:$PORT" &
fi

echo "✅ 우리단지 ON PWA가 성공적으로 실행되었습니다."
