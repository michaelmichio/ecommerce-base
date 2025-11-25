#!/bin/bash

set -e

echo "🚀 Starting Docker containers..."
docker compose --profile dev up --build

echo "⏳ Checking backend availability..."
until curl -s http://localhost:8000/docs >/dev/null; do
    echo "Waiting backend..."
    sleep 1
done

echo "⏳ Checking frontend availability..."
until curl -s http://localhost:3000 >/dev/null; do
    echo "Waiting frontend..."
    sleep 1
done

echo "🌐 Opening browser tabs..."

# UNIVERSAL WINDOWS DETECTION
if grep -qi microsoft /proc/version 2>/dev/null || [[ "$PWD" == *":\\"* ]]; then
    echo "🖥️ Windows/WSL detected — using PowerShell"
    powershell.exe -NoProfile -Command "Start-Process 'http://localhost:8000/docs'"
    powershell.exe -NoProfile -Command "Start-Process 'http://localhost:3000'"
    echo "✅ Browser opened via PowerShell"
    exit 0
fi

# macOS
if [[ "$(uname | tr '[:upper:]' '[:lower:]')" == "darwin" ]]; then
    echo "🍎 macOS detected"
    open "http://localhost:8000/docs"
    open "http://localhost:3000"
    exit 0
fi

# Linux Native
echo "🐧 Linux detected"
xdg-open "http://localhost:8000/docs" >/dev/null 2>&1
xdg-open "http://localhost:3000" >/dev/null 2>&1
