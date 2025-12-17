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
        self.available_module_factories = [] 
        self.fps = fps
        self.feedback = feedback
        self.glitch = glitch
        self.kaleidoscope = kaleidoscope
        self.kick_threshold = kick_threshold
        self.prev_image = None
        
        self.last_swap_time = 0
        self.swap_interval = 8.0 
        
    def set_module_pool(self, factories):
        self.available_module_factories = factories
        
    def draw_scene_evolution(self, t):
        if t - self.last_swap_time > self.swap_interval and self.available_module_factories:
            self.last_swap_time = t
            print(f"  [SceneController] Evolving visuals at {t:.1f}s...")
            
            if len(self.active_modules) > 2:
                self.active_modules.pop(random.randint(0, len(self.active_modules)-1))
                
            for _ in range(random.randint(1, 2)):
                if len(self.active_modules) < 6: # Increased max modules
                    factory = random.choice(self.available_module_factories)
                    new_mod = factory()
                    self.active_modules.append(new_mod)
                    
            if random.random() > 0.8:
                self.kaleidoscope = not self.kaleidoscope
                print(f"    > Kaleidoscope flipped to {self.kaleidoscope}")
                
    def make_frame(self, t):
        w, h = 1080, 1920
        
        self.draw_scene_evolution(t)
        
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
        
        for module in self.active_modules:
            module.draw(draw, w, h, t, levels)
            
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
             # TUNING: Raised threshold 0.8 -> 0.9, Reduced offset 30 -> 15
             if e_high > 0.9: 
                 r, g, b = image.split()
                 offset = int(e_high * 15)
                 r = ImageChops.offset(r, offset, 0)
                 b = ImageChops.offset(b, -offset, 0)
                 image = Image.merge("RGB", (r, g, b))
        
        self.prev_image = image.copy()
        return np.array(image)
