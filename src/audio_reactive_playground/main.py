import argparse
import os
import numpy as np
from moviepy import VideoClip, AudioFileClip
import soundfile as sf
import random
import colorsys

from audio_reactive_playground.audio import AudioAnalyzer
from audio_reactive_playground.visuals import Renderer, CirclePulse, PolyrhythmShapes, WaveformSpiral, ParticleBurst, LissajousCurve, TunnelEffect, FlashEffect, FlowField, VoronoiEffect, SuperShape, MoirePattern, RoamingGeometry, CrossHatch

def generate_test_audio(filename="test_audio.mp3", duration=30):
    """Generates a synthetic audio file with bass kicks and high tones."""
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    # Bass: 50Hz sine wave, pulsing every 0.5s
    bass = np.sin(2 * np.pi * 50 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 2 * t))
    
    # High: 5000Hz bursts
    high = np.sin(2 * np.pi * 5000 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 4 * t)) * 0.3
    
    # Mid: 500Hz constant
    mid = np.sin(2 * np.pi * 500 * t) * 0.2
    
    audio = bass + high + mid
    sf.write(filename.replace(".mp3", ".wav"), audio, sr)
    return filename.replace(".mp3", ".wav")

def get_random_neon_color():
    """Generates a random bright neon color."""
    h = random.random()
    s = random.uniform(0.7, 1.0)
    v = 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def to_byte(c): 
    return (int(c[0]*255), int(c[1]*255), int(c[2]*255))

def get_palette_color(palette_type):
    if palette_type == "cyberpunk":
        # high saturation, hue around 0.8 (magenta) or 0.5 (cyan)
        h = random.choice([random.uniform(0.75, 0.95), random.uniform(0.45, 0.55)])
        return colorsys.hsv_to_rgb(h, 1.0, 1.0)
    elif palette_type == "acid":
        # lime (0.3), yellow (0.15), magenta (0.8)
        h = random.choice([0.3, 0.15, 0.85, 0.0]) # 0.0 red too
        return colorsys.hsv_to_rgb(h, 1.0, 1.0)
    elif palette_type == "ice":
         h = random.uniform(0.5, 0.65)
         return colorsys.hsv_to_rgb(h, random.uniform(0.2, 1.0), 1.0)
    else: # fire
         h = random.uniform(0.0, 0.15)
         return colorsys.hsv_to_rgb(h, 1.0, 1.0)

def generate_random_modules(palette_type):
    """Randomly constructs a list of visual modules with wild parameters."""
    print("Time to roll the dice! Generating ARTISTIC visuals...")
    modules = []
    
    print(f"  > Palette: {palette_type}")
    
    # helper lambda to bind palette
    get_color = lambda: get_palette_color(palette_type)
    
    # 1. Background / Deep Layer (Tunnel or Pulse)
    if random.choice([True, False]):
        # Tunnel
        color = to_byte(get_color())
        key = "bass"
        sides = random.randint(3, 8) # diverse geometry
        modules.append(TunnelEffect(key=key, color=color, speed=random.uniform(0.5, 2.0), sides=sides))
        print(f"  + Added TunnelEffect ({key}) [sides={sides}]")
    else:
        # Pulse
        color = to_byte(get_color())
        modules.append(CirclePulse(key="bass", color=color, max_radius_ratio=0.8))
        print(f"  + Added CirclePulse (bass)")

    # 2. Hero Layer (Lissajous or Shapes)
    if random.random() > 0.4:
        # Lissajous Art
        color = to_byte(get_color())
        key = random.choice(["mid", "high"])
        modules.append(LissajousCurve(key=key, color=color, speed=0.3, complexity=random.randint(2, 5)))
        print(f"  + Added LissajousCurve ({key})")
    
    # Add Shapes regardless sometimes for layering?
    if random.random() > 0.3:
        key = random.choice(["mid", "high"])
        num_shapes = random.randint(1, 3)
        shape_types = [random.randint(3, 6) for _ in range(num_shapes)]
        colors = [to_byte(get_color()) for _ in range(3)]
        modules.append(PolyrhythmShapes(key=key, base_speed=random.uniform(0.2, 0.6), colors=colors, shape_types=shape_types))
        print(f"  + Added PolyrhythmShapes ({key})")

    # 3. Spiral / Texture
    if random.random() > 0.5:
        color = to_byte(get_color())
        modules.append(WaveformSpiral(key="high", color=color, speed=0.5, b_growth=0.15, distortion=2.0))
        print(f"  + Added WaveformSpiral (high)")

    # NEW: Flow Field
    if random.random() > 0.6:
        color = to_byte(get_color())
        modules.append(FlowField(key="mid", color=color, count=300))
        print(f"  + Added FlowField")
        
    # NEW: Voronoi / Network
    if random.random() > 0.6:
        color = to_byte(get_color())
        modules.append(VoronoiEffect(key="mid", color=color, count=25))
        print(f"  + Added VoronoiEffect")
        
    # NEW: SuperShape
    if random.random() > 0.6:
        color = to_byte(get_color())
        modules.append(SuperShape(key="mid", color=color, m=random.randint(3,8)))
        print(f"  + Added SuperShape")

    # NEW: MoirePattern
    if random.random() > 0.6:
        color = to_byte(get_color())
        modules.append(MoirePattern(key="high", color=color))
        print(f"  + Added MoirePattern")

    # 4. Flash / Energy
    if random.random() > 0.3:
        color = to_byte(get_color())
        modules.append(FlashEffect(key="bass", color=color))
        print(f"  + Added FlashEffect")
        
    return modules

def main():
    parser = argparse.ArgumentParser(description="Audio Reactive Visuals")
    parser.add_argument("--audio", type=str, help="Path to input audio file")
    parser.add_argument("--start", type=float, default=0, help="Start time in seconds")
    parser.add_argument("--end", type=float, default=10, help="End time in seconds")
    parser.add_argument("--output", type=str, default="output.mp4", help="Output video path")
    parser.add_argument("--kick_threshold", type=float, default=0.6, help="Bass threshold (0.0-1.0). Bass below this is ignored.")
    parser.add_argument("--speed", type=float, default=1.0, help="Global speed multiplier")
    parser.add_argument("--complexity", type=float, default=1.0, help="Global complexity/density multiplier")
    
    args = parser.parse_args()
    
    # Global Tuners
    G_SPEED = args.speed
    G_COMPLEX = args.complexity

    audio_path = args.audio

    
    if not audio_path or not os.path.exists(audio_path):
        print("No audio provided or found. Generating test audio...")
        audio_path = generate_test_audio()
        print(f"Generated {audio_path}")
        
    duration = args.end - args.start
    
    print(f"Analyzing audio: {audio_path} [{args.start}-{args.end}s]")
    analyzer = AudioAnalyzer(audio_path, start_time=args.start, end_time=args.end)
    
    # Pick a palette globally
    palette_type = random.choice(["cyberpunk", "acid", "ice", "fire"])
    # Helper to get color from current palette
    get_color = lambda: get_palette_color(palette_type)
    
    modules = generate_random_modules(palette_type)
    
    # Artistic configuration
    use_feedback = random.choice([True, False]) 
    use_glitch = True 
    # NEW: Kaleidoscope mode
    use_kaleidoscope = random.random() > 0.7 # 30% chance for pure geometric madness
    
    print(f"  > Feedback Mode: {use_feedback}")
    print(f"  > Glitch FX: {use_glitch}")
    print(f"  > Kaleidoscope: {use_kaleidoscope}")
    print(f"  > Kick Threshold: {args.kick_threshold}")

    # Create a pool of factories for specific modules so Renderer can spawn them
    # We use lambdas to create fresh instances with random params
    
    def get_pos():
        # 50% chance of center, 50% chance of random position
        if random.random() > 0.5:
             return (0.5, 0.5)
        return (random.uniform(0.1, 0.9), random.uniform(0.1, 0.9))
        
    def get_drift():
        # 30% chance of drift
        if random.random() > 0.7:
            return (random.uniform(-0.002, 0.002), random.uniform(-0.002, 0.002))
        return (0.0, 0.0)

    module_pool_factories = [
        lambda: CirclePulse(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: PolyrhythmShapes(colors=[to_byte(get_color()) for _ in range(3)], center=get_pos(), drift=get_drift()),
        lambda: WaveformSpiral(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: ParticleBurst(color=to_byte(get_color())), 
        lambda: LissajousCurve(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: TunnelEffect(color=to_byte(get_color()), sides=random.randint(3, 8), center=get_pos(), drift=get_drift()),
        lambda: FlowField(color=to_byte(get_color())), 
        lambda: VoronoiEffect(color=to_byte(get_color())), 
        lambda: SuperShape(color=to_byte(get_color()), m=random.randint(3, 10), n1=random.uniform(0.2, 2.0), center=get_pos(), drift=get_drift()),
        lambda: MoirePattern(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: RoamingGeometry(color=to_byte(get_color())),
        lambda: CrossHatch(color=to_byte(get_color()), count=int(10 * args.complexity)),
    ]

    # Flash effect separate
    flash_factory = lambda: FlashEffect(key="bass", color=to_byte(get_color()))

    renderer = Renderer(analyzer, modules, fps=24, feedback=use_feedback, glitch=use_glitch, kaleidoscope=use_kaleidoscope, kick_threshold=args.kick_threshold)
    
    # Enable Evolution
    # Add all standard modules + flash to the pool
    full_pool = module_pool_factories + [flash_factory]
    renderer.set_module_pool(full_pool)
    
    print("Rendering video...")
    
    # Create video clip
    clip = VideoClip(renderer.make_frame, duration=duration)
    
    # Add audio
    # Load original audio, subclip it, and set it
    original_audio = AudioFileClip(audio_path)
    # Clip audio to the window
    clip = clip.with_audio(original_audio.subclipped(args.start, args.end))
    
    clip.write_videofile(args.output, fps=24)
    print(f"Done! Saved to {args.output}")

if __name__ == "__main__":
    main()
