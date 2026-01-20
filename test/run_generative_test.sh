#!/bin/bash
# Run from repository root
# Usage: ./test/run_test.sh

# Ensure .venv is active or use the python path directly
PYTHON_CMD="./.venv/bin/python"

if [ ! -f "$PYTHON_CMD" ]; then
    echo "Virtual environment python not found at $PYTHON_CMD"
    exit 1
fi

INPUT_FILE="test/input/Palmos - Helix.wav" # replace with your audio file
OUTPUT_FILE="test/output/test.mp4" # replace with your output file

# Visual Settings
BARS=4 # Change this to 4, 16, 32 etc. to change how often the scene evolves
KICK_THRESHOLD=0.9
COMPLEXITY=0.5
SPEED=0.5
CONTOUR_MODE="shatter"

echo "Rendering 10s clip from $INPUT_FILE..."
$PYTHON_CMD -m audio_reactive_playground.main \
    --audio "$INPUT_FILE" \
    --start 90 \
    --end 120 \
    --output "$OUTPUT_FILE" \
    --kick_threshold $KICK_THRESHOLD \
    --complexity $COMPLEXITY \
    --bars $BARS \
    --speed $SPEED \
    --contour_mode $CONTOUR_MODE

echo "Done! Output at $OUTPUT_FILE"
