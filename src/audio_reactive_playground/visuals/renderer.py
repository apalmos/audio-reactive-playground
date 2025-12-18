import random
from PIL import Image, ImageDraw, ImageChops
import numpy as np

class Renderer:
    """
    The Master Scene Controller.
    
    Responsibilities:
    1.  **Orchestration**: Decides which modules are active.
    2.  **Evolution**: Periodically (every ~8s) swaps old modules for new ones (The "AI VJ").
    3.  **Post-Processing**: Applies global effects like Feedback trails, Kaleidoscope mirroring, and Glitch.
    4.  **Audio Gating**: Processes threshold logic (ignoring low volume bass).
    """
    def __init__(self, audio_analyzer, modules, fps=24, feedback=True, glitch=True, kaleidoscope=False, kick_threshold=0.6):
        self.audio = audio_analyzer
        self.active_modules = modules 
        
        # Ensure we start with exactly 2 modules for the "Gallery" feel
        # If main passed more, trim soundly. If less, we'll add later.
        if len(self.active_modules) > 2:
            self.active_modules = self.active_modules[:2]
            
        # Track when each module was added to calculate fade-in
        # dictionary: module -> start_time
        # Fix: Start at -100 so initial modules don't fade in from black (User request)
        self.module_start_times = {m: -100.0 for m in self.active_modules}
        
        self.available_module_factories = [] 
        self.fps = fps
        self.feedback = feedback
        self.glitch = glitch
        self.kaleidoscope = kaleidoscope
        self.kick_threshold = kick_threshold
        self.prev_image = None
        
        # Transition State
        # Transition State
        self.last_swap_beat = 0 
        self.bars_per_scene = 8 # Default, can be overridden
        self.transition_duration = 3.0 # Slower fade for artful feel
        
        # Glitch State
        self.last_glitch_beat = 0 
        self.next_glitch_wait_bars = random.choice([8, 16]) # Glitch only every 8 or 16 bars
        
        # List of tuple (module, fade_start_time)
        self.fading_out_modules = []
        
    def set_module_pool(self, factories):
        self.available_module_factories = factories

    def set_bars(self, bars):
        self.bars_per_scene = bars
        if bars < 1: self.bars_per_scene = 1
        
    def check_scene_evolution(self, t):
        # Trigger swap based on BARS (1 bar = 4 beats)
        current_beat = self.audio.get_beat_index(t)
        beats_per_swap = self.bars_per_scene * 4
        
        if (current_beat - self.last_swap_beat) >= beats_per_swap and self.available_module_factories:
            self.last_swap_beat = current_beat
            print(f"  [SceneController] Evolving visuals at {t:.1f}s (Beat {current_beat})...")
            
            # 1. Pick ONE module to replace
            # If we don't have enough modules, just add one.
            if len(self.active_modules) < 2:
                 # Add new
                 factory = random.choice(self.available_module_factories)
                 new_mod = factory()
                 self.active_modules.append(new_mod)
                 self.module_start_times[new_mod] = t
                 print(f"    + Added {new_mod.__class__.__name__} (Filling slot)")
            else:
                 # Replace random one
                 remove_idx = random.randint(0, len(self.active_modules)-1)
                 old_mod = self.active_modules.pop(remove_idx)
                 
                 # Move to fading out list
                 self.fading_out_modules.append((old_mod, t))
                 
                 # Add new replacement
                 factory = random.choice(self.available_module_factories)
                 new_mod = factory()
                 # Insert at same index to preserve layer order (Back/Front)
                 self.active_modules.insert(remove_idx, new_mod)
                 self.module_start_times[new_mod] = t
                 print(f"    ~ Swapped {old_mod.__class__.__name__} -> {new_mod.__class__.__name__}")

            if random.random() > 0.85:
                self.kaleidoscope = not self.kaleidoscope
                print(f"    > Kaleidoscope flipped to {self.kaleidoscope}")
                
    def make_frame(self, t):
        w, h = 1080, 1920
        
        self.check_scene_evolution(t)
        
        if self.feedback and self.prev_image:
             decay = Image.new("RGB", (w, h), (0, 0, 0))
             image = Image.blend(self.prev_image, decay, 0.08)
        else:
             image = Image.new("RGB", (w, h), (0, 0, 0))
             
        draw = ImageDraw.Draw(image)
        levels = self.audio.get_energy_at_time(t)
        
        raw_bass = levels.get("bass", 0)
        if raw_bass < self.kick_threshold:
            levels["bass"] = 0.0
        else:
            range_width = 1.0 - self.kick_threshold
            if range_width > 0:
                levels["bass"] = (raw_bass - self.kick_threshold) / range_width
        
        # DRAWING LOGIC: PARTIAL EVOLUTION
        
        # 1. Draw Fading Out Modules
        # Filter dead ones
        active_fades = []
        for mod, start_t in self.fading_out_modules:
            progress = (t - start_t) / self.transition_duration
            if progress < 1.0:
                alpha = 1.0 - progress
                mod.draw(draw, w, h, t, levels, opacity=alpha)
                active_fades.append((mod, start_t))
        self.fading_out_modules = active_fades
        
        # 2. Draw Active Modules
        for mod in self.active_modules:
            # Check if it's new and fading in
            start_t = self.module_start_times.get(mod, 0)
            progress = (t - start_t) / self.transition_duration
            
            alpha = 1.0
            if progress < 1.0:
                alpha = progress # Fade in 0 -> 1
                
            mod.draw(draw, w, h, t, levels, opacity=alpha)
            
        if self.kaleidoscope:
            quad_w, quad_h = w // 2, h // 2
            source = image.crop((0, 0, quad_w, quad_h))
            row = Image.new("RGB", (w, quad_h))
            row.paste(source, (0, 0))
            row.paste(source.transpose(Image.FLIP_LEFT_RIGHT), (quad_w, 0))
            full = Image.new("RGB", (w, h))
            full.paste(row, (0, 0))
            full.paste(row.transpose(Image.FLIP_TOP_BOTTOM), (0, quad_h))
            image = full
 
        if self.glitch:
             e_high = levels.get("high", 0)
             accent = levels.get("accent", 0)
             
             # TUNING: "Rarely" means every 8 or 16 bars (randomized).
             # And only on strong hits.
             current_beat = self.audio.get_beat_index(t)
             beats_since_glitch = current_beat - self.last_glitch_beat
             wait_beats = self.next_glitch_wait_bars * 4
             
             # TUNING: More frequent glitches (Accents)
             # Threshold lowered 0.85 -> 0.7 to catch more snares
             is_accent = accent > 0.7
             ready = beats_since_glitch >= wait_beats
             
             if is_accent and ready: 
                 self.last_glitch_beat = current_beat
                 # Reset timer to 2-4 bars (was 8-16) for "occasional" feel
                 self.next_glitch_wait_bars = random.choice([2, 4, 8])
                 
                 r, g, b = image.split()
                 
                 # Dynamic offset: Accents hit HARDER but much subtler now
                 base_offset = 12 
                     
                 offset = int((e_high + accent) * 0.5 * base_offset)
                 
                 r = ImageChops.offset(r, offset, 0)
                 b = ImageChops.offset(b, -offset, 0)
                 image = Image.merge("RGB", (r, g, b))
                 
                 # Optional: White Flash Overlay for very strong accents
                 if accent > 0.95:
                     flash = Image.new("RGB", (w, h), (255, 255, 255))
                     image = Image.blend(image, flash, 0.05)
        
             # SCREEN WOBBLE (Accent Only - User Requested)
             # Triggers on SHARP transients (Snares/Claps), independent of the rare RGB glitch
             # Threshold 0.8 ensures we don't shake on minor noise, only hits.
             if accent > 0.8:
                 # Shake amount depends on how strong the accent is
                 shake_amt = int(8 + (accent * 8)) # Range ~10-16px
                 dx = random.randint(-shake_amt, shake_amt)
                 dy = random.randint(-shake_amt, shake_amt)
                 image = ImageChops.offset(image, dx, dy)

        self.prev_image = image.copy()
        return np.array(image)
