# Audio Reactive Playground

A Python-based audio visualization tool that generates artful, decentralized, and evolving geometry that reacts to your music.

## Features

*   **Audio Reactive**: Reacts to bass, mid, and high frequencies with specific visual triggers.
*   **Scene Evolution**: Visuals change every 8 seconds, ensuring a dynamic experience that never gets boring.
*   **Decentralized**: Shapes float, drift, and spawn across the entire screen, breaking away from traditional center-focused visualizers.
*   **Artful Modules**: includes `SuperShape` (organic blobs), `MoirePattern` (interference), `CrossHatch` (multiplying lines), `TunnelEffect` (infinite 3D tunnels), and more.
*   **Post-Processing**: Includes Glitch effects, Kaleidoscope mirroring, and video feedback trails.

## Installation

This project uses `uv` for dependency management.

1.  **Clone the repository**:
    ```bash
    git clone <repo-url>
    cd audio-reactive-playground
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

## Usage

Run the visualizer on your audio files using the `main.py` script.

### Basic Run
```bash
uv run src/audio_reactive_playground/main.py --audio "path/to/your/song.wav"
```

### Advanced Configuration

You can tune the visuals using various command-line arguments:

*   `--start <seconds>`: Start processing audio from this timestamp.
*   `--end <seconds>`: Stop processing at this timestamp.
*   `--kick_threshold <0.0-1.0>`: Sensitivity of the bass reaction. Higher (e.g., 0.7-0.9) means only strong kicks trigger effects. Lower (0.4) captures more bass.
*   `--speed <float>`: Global speed multiplier for movement and drift. Default is 1.0.
*   `--complexity <float>`: Multiplier for visual density (e.g., number of lines, particles). Default is 1.0.

### Comprehensive Example
Here is a command that uses **every possible customization option** available:

```bash
uv run src/audio_reactive_playground/main.py \
    --audio "my_track.mp3" \
    --start 60.0 \
    --end 90.0 \
    --output "final_render.mp4" \
    --kick_threshold 0.8 \
    --speed 0.5 \
    --complexity 0.8
```

This specific command will:
1.  Process `my_track.mp3` from **1:00 to 1:30**.
2.  Save the result to `final_render.mp4`.
3.  **Gate the audio reaction**: Only kicks louder than 80% volume will trigger effects (`--kick_threshold 0.8`).
4.  **Chill Mode**: Run at **half speed** (`--speed 0.5`) and **reduced density** (`--complexity 0.8`) for a cleaner, calmer look.

## Visual Modules

The `SceneController` randomly selects from a pool of modules:

*   **CirclePulse**: A classic pulsing circle reacting to bass.
*   **TunnelEffect**: An infinite 3D tunnel that speeds up on kicks.
*   **SuperShape**: Organic, morphing math-based shapes.
*   **MoirePattern**: Trippy interference patterns.
*   **CrossHatch**: Sketchy lines that multiply and cross on beat.
*   **RoamingGeometry**: "Meteor" shapes that fly across the screen.
*   **FlowField**: Particle systems driven by perlin-like noise.
