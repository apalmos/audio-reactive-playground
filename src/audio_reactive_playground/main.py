import argparse
import os
import numpy as np
from moviepy import VideoClip, AudioFileClip
import soundfile as sf
import random
import colorsys

from audio_reactive_playground.audio import AudioAnalyzer
from audio_reactive_playground.visuals import Renderer, CirclePulse, PolyrhythmShapes, WaveformSpiral, ParticleBurst, LissajousCurve, TunnelEffect, FlashEffect, FlowField, VoronoiEffect, SuperShape, MoirePattern, RoamingGeometry, CrossHatch, FractalGrowth, Metaballs, SpectrumHorizon, DifferentialLine, StrangeAttractor, HexGrid, TruchetTiles, SacredGeometry, PlatonicSolids, EqualizerRing, BinaryRain, DNAStrand, SonarRadar, CyberPlane, WaveTerrain, GodRays, RippleSystem, ScanLines, ParticleDust

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
    
    # 1. Background / Deep Layer (Tunnel, Pulse, Waves, Rays, Grid, Ripples, ScanLines, Dust)
    # 8 Options = ~12% chance each.
    bg_roll = random.random()
    if bg_roll < 0.125:
        # Tunnel
        color = to_byte(get_color())
        key = "bass"
        sides = random.randint(3, 8) 
        modules.append(TunnelEffect(key=key, color=color, speed=random.uniform(0.5, 2.0), sides=sides))
        print(f"  + Added TunnelEffect ({key}) [sides={sides}]")
    elif bg_roll < 0.25:
        # Pulse
        color = to_byte(get_color())
        modules.append(CirclePulse(key="bass", color=color, max_radius_ratio=0.8))
        print(f"  + Added CirclePulse (bass)")
    elif bg_roll < 0.375:
        # WaveTerrain (Random Zoom)
        color = to_byte(get_color())
        zoom = random.uniform(0.8, 2.0)
        modules.append(WaveTerrain(key="bass", color=color, count=25, zoom=zoom))
        print(f"  + Added WaveTerrain (bass) [zoom={zoom:.2f}]")
    elif bg_roll < 0.50:
        # GodRays
        color = to_byte(get_color())
        modules.append(GodRays(key="bass", color=color, count=random.randint(5, 12)))
        print(f"  + Added GodRays (bass)")
    elif bg_roll < 0.625:
        # CyberPlane
        color = to_byte(get_color())
        modules.append(CyberPlane(key="bass", color=color))
        print(f"  + Added CyberPlane (bass)")
    elif bg_roll < 0.75:
        # RippleSystem
        color = to_byte(get_color())
        modules.append(RippleSystem(key="high", color=color))
        print(f"  + Added RippleSystem (high)")
    elif bg_roll < 0.875:
        # ScanLines
        color = to_byte(get_color())
        modules.append(ScanLines(key="mid", color=color))
        print(f"  + Added ScanLines (mid)")
    else:
        # ParticleDust (Very minimal)
        color = to_byte(get_color())
        modules.append(ParticleDust(key="mid", color=color))
        print(f"  + Added ParticleDust (mid)")

    # =========================================================================
    # SLOT-BASED SELECTION (Max ~3 active modules to prevent clutter)
    # =========================================================================
    
    # Pool of "Hero" modules (Main focus)
    hero_pool = []
    hero_pool.append(lambda: LissajousCurve(key=random.choice(["mid", "high"]), color=to_byte(get_color()), speed=0.3, complexity=random.randint(2, 5)))
    hero_pool.append(lambda: PolyrhythmShapes(key=random.choice(["mid", "high"]), base_speed=random.uniform(0.2, 0.6), colors=[to_byte(get_color()) for _ in range(3)], shape_types=[random.randint(3, 6) for _ in range(2)]))
    hero_pool.append(lambda: WaveformSpiral(key="high", color=to_byte(get_color()), speed=0.5, b_growth=0.15, distortion=2.0))
    hero_pool.append(lambda: SuperShape(key="mid", color=to_byte(get_color()), m=random.randint(3,8)))
    hero_pool.append(lambda: StrangeAttractor(key="mid", color=to_byte(get_color())))
    hero_pool.append(lambda: PlatonicSolids(key="bass", color=to_byte(get_color()), speed=random.uniform(0.5, 1.5)))
    hero_pool.append(lambda: DNAStrand(key="mid", color=to_byte(get_color())))
    hero_pool.append(lambda: SacredGeometry(key="bass", color=to_byte(get_color())))
    
    # Pool of "Texture/Overlay" modules (Subtle additions)
    texture_pool = []
    texture_pool.append(lambda: DifferentialLine(key="bass", color=to_byte(get_color()), max_nodes=200))
    texture_pool.append(lambda: FlowField(key="mid", color=to_byte(get_color()), count=200))
    texture_pool.append(lambda: VoronoiEffect(key="mid", color=to_byte(get_color()), count=25))
    texture_pool.append(lambda: MoirePattern(key="high", color=to_byte(get_color())))
    texture_pool.append(lambda: HexGrid(key="bass", color=to_byte(get_color())))
    texture_pool.append(lambda: TruchetTiles(key="mid", color=to_byte(get_color()), count=random.randint(6, 12)))
    texture_pool.append(lambda: EqualizerRing(key="mid", color=to_byte(get_color())))
    texture_pool.append(lambda: BinaryRain(key="high", color=to_byte(get_color())))
    texture_pool.append(lambda: SonarRadar(key="high", color=to_byte(get_color())))

    # SELECT: 1 Hero (60% chance)
    if random.random() < 0.60:
        hero_mod = random.choice(hero_pool)()
        modules.append(hero_mod)
        print(f"  + Added Hero: {type(hero_mod).__name__}")
        
    # SELECT: 1 Texture (40% chance, or 70% if no Hero)
    # If we have a hero, we want less chance of texture to avoid clash.
    has_hero = len(modules) > 1 # Background is 0
    chance_texture = 0.3 if has_hero else 0.7
    
    if random.random() < chance_texture:
        tex_mod = random.choice(texture_pool)()
        modules.append(tex_mod)
        print(f"  + Added Texture: {type(tex_mod).__name__}")
        
    # 4. Flash / Energy (Always independent, low chance)
    if random.random() > 0.7:
        color = to_byte(get_color())
        modules.append(FlashEffect(key="bass", color=color))
        print(f"  + Added FlashEffect")
        
    # CyberPlane Promoted to Background layer
    # if random.random() > 0.6:
    #     color = to_byte(get_color())
    #     modules.append(CyberPlane(key="bass", color=color))
    #     print(f"  + Added CyberPlane")

    # 4. Flash / Energy

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
    parser.add_argument("--speed", type=float, default=0.3, help="Global speed multiplier")
    parser.add_argument("--complexity", type=float, default=0.3, help="Global complexity/density multiplier")
    
    parser.add_argument("--bars", type=int, default=8, help="Number of bars between scene changes (default: 8)")
    
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
        # Always center focused as requested
        return (0.5, 0.5)
        
    def get_drift():
        # No drift, stay grounded
        return (0.0, 0.0)

    module_pool_factories = [
        # Scaled counts/speeds based on global args
        lambda: CirclePulse(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        # Less shapes on low complexity
        lambda: PolyrhythmShapes(colors=[to_byte(get_color()) for _ in range(3)], shape_types=[random.randint(3, 6) for _ in range(max(1, int(3 * args.complexity)))], center=get_pos(), drift=get_drift()), 
        lambda: WaveformSpiral(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: ParticleBurst(color=to_byte(get_color()), count=max(10, int(50 * args.complexity))), 
        lambda: LissajousCurve(color=to_byte(get_color()), center=get_pos(), drift=get_drift(), speed=0.3 * args.speed, complexity=max(2, int(6 * args.complexity))),
        # Tunnel sides 3-8 or 3-4 if simple
        lambda: TunnelEffect(color=to_byte(get_color()), sides=random.randint(3, max(4, int(8 * args.complexity))), center=get_pos(), drift=get_drift(), speed=1.0 * args.speed),
        lambda: FlowField(color=to_byte(get_color()), count=max(20, int(80 * args.complexity))), 
        lambda: VoronoiEffect(color=to_byte(get_color()), count=max(10, int(30 * args.complexity))), 
        # SuperShape m=low is simple blob, m=high is spikey
        lambda: SuperShape(color=to_byte(get_color()), m=random.uniform(2, max(4, 10 * args.complexity)), n1=random.uniform(0.2, 2.0), center=get_pos(), drift=get_drift()),
        lambda: MoirePattern(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: RoamingGeometry(color=to_byte(get_color())), 
        lambda: CrossHatch(color=to_byte(get_color()), count=max(6, int(15 * args.complexity))),
        # Nature Modules
        lambda: FractalGrowth(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: Metaballs(color=to_byte(get_color()), count=max(5, int(15 * args.complexity)), center=get_pos(), drift=get_drift()),
        lambda: DifferentialLine(color=to_byte(get_color()), max_nodes=max(100, int(300 * args.complexity)), center=get_pos(), drift=get_drift()),
        # Math Art Modules
        lambda: StrangeAttractor(color=to_byte(get_color()), complexity=args.complexity, center=get_pos(), drift=get_drift()),
        lambda: HexGrid(color=to_byte(get_color()), complexity=args.complexity, center=get_pos(), drift=get_drift()),
        # Geometric Modules
        lambda: TruchetTiles(color=to_byte(get_color()), count=max(4, int(12 * args.complexity)), center=get_pos(), drift=get_drift()),
        lambda: SacredGeometry(color=to_byte(get_color()), center=get_pos(), drift=get_drift(), complexity=args.complexity), # Sacred doesn't take complexity yet -> Now it does
        # Club Modules
        lambda: PlatonicSolids(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: EqualizerRing(color=to_byte(get_color()), bars=max(20, int(80 * args.complexity)), center=get_pos(), drift=get_drift()),
        lambda: BinaryRain(color=to_byte(get_color()), count=max(10, int(50 * args.complexity))),
        # NEW Slick Modules
        lambda: DNAStrand(color=to_byte(get_color()), count=max(10, int(40 * args.complexity)), center=get_pos(), drift=get_drift()),
        lambda: SonarRadar(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: CyberPlane(color=to_byte(get_color()), grid_cols=max(6, int(20 * args.complexity))),
        # NEW Minimalist Modules
        lambda: WaveTerrain(color=to_byte(get_color()), count=max(8, int(20 * args.complexity)), center=get_pos(), drift=get_drift(), zoom=random.uniform(0.5, 1.8)),
        lambda: GodRays(color=to_byte(get_color()), count=random.randint(5, 12), center=get_pos(), drift=get_drift()),
        lambda: RippleSystem(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: ScanLines(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
        lambda: ParticleDust(color=to_byte(get_color()), center=get_pos(), drift=get_drift()),
    ]

    renderer = Renderer(analyzer, modules, fps=24, feedback=use_feedback, glitch=use_glitch, kaleidoscope=use_kaleidoscope, kick_threshold=args.kick_threshold)
    
    # Enable Evolution
    # Add all standard modules to the pool (FlashEffect removed to reduce spam)
    full_pool = module_pool_factories 
    renderer.set_module_pool(full_pool)
    renderer.set_bars(args.bars)
    
    print("Rendering video...")
    
    # Create video clip
    clip = VideoClip(renderer.make_frame, duration=duration)
    
    # Add audio
    # Load original audio, subclip it, and set it
    original_audio = AudioFileClip(audio_path)
    # Clip audio to the window
    clip = clip.with_audio(original_audio.subclipped(args.start, args.end))
    
    clip.write_videofile(args.output, fps=24, audio_codec="aac")
    print(f"Done! Saved to {args.output}")

if __name__ == "__main__":
    main()
