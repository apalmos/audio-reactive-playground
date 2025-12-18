# Audio Reactive Playground

A Python-based audio visualization tool that generates artful, decentralized, and evolving geometry that reacts to your music.

## Features

*   **Audio Reactive**: Reacts to bass, mid, and high frequencies with specific visual triggers.
*   **Scene Evolution**: Visuals change every 8 seconds, ensuring a dynamic experience that never gets boring.
*   **Minimalist & Slick**: Shapes are curated to avoid clutter. A smart "Slot System" ensures meaningful layering (Background + Hero + Texture) without visual chaos.
*   **Artful Modules**: includes `WaveTerrain` (Joy Division style), `GodRays` (Volumetric Light), `RippleSystem` (Rain), `SuperShape` (Organic), and more.
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
*   `--speed <float>`: Global speed multiplier. Default is 0.3 (Slower/Chill).
*   `--complexity <float>`: Multiplier for visual density. Default is 0.3 (Minimal).
*   `--bars <int>`: Number of musical bars (4 beats) between visual scene swaps. Default is 8.

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
    --complexity 0.4 \
    --bars 16
```

## Visual Modules

The `SceneController` randomly selects a composition of **1-3** modules to keep it clean:

**Atmosphere & Backgrounds**:
*   **WaveTerrain**: Rolling landscape lines (Joy Division style) with random zoom.
*   **GodRays**: Subtle volumetric light beams rotating in the background.
*   **RippleSystem**: Minimalist rain-like ripples.
*   **ScanLines**: Retro CRT monitor overlay.
*   **ParticleDust**: Floating ambient dust.
*   **TunnelEffect**: Infinite 3D wireframe tunnel.

**Hero Geometry**:
*   **SuperShape**: Organic, morphing math-based blobs.
*   **LissajousCurve**: Complex parametric curves.
*   **PlatonicSolids**: Rotating 3D shapes (Icosahedron, Cube).
*   **DNAStrand**: Twisting double helix.
*   **PolyrhythmShapes**: Orbiting geometric shapes.
*   **Strange Attractor**: Chaos theory particle clouds.

**Texture & Patterns**:
*   **FlowField**: Particle systems driven by noise.
*   **HexGrid**: Pulsing honeycomb interface.
*   **TruchetTiles**: Retro geometric tiling patterns.
*   **MoirePattern**: Trippy interference patterns.
*   **DifferentialLine**: Organic coral growth simulation.
