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
OUTPUT_FILE="test/output/helix_visuals.mp4" # replace with your output file

echo "Rendering 10s clip from $INPUT_FILE..."
$PYTHON_CMD -m audio_reactive_playground.main \
    --audio "$INPUT_FILE" \
    --start 240 \
    --end 270 \
    --output "$OUTPUT_FILE" \
    --kick_threshold 0.9

echo "Done! Output at $OUTPUT_FILE"
