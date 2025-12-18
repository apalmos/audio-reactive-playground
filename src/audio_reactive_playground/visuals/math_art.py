import random
import math
import numpy as np
from PIL import ImageDraw
from .base import VisualModule

class StrangeAttractor(VisualModule):
    """
    Renders a 'Strange Attractor' (Clifford or De Jong) particle cloud.
    Visualize pure mathematical chaos.
    """
    def __init__(self, key="mid", color=(255, 255, 255), speed=1.0, complexity=0.5, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.speed = speed
        self.complexity = complexity
        self.num_points = int(2000 + 4000 * complexity) # 2000-6000 points
        
        # Base parameters for Clifford Attractor
        # Good seed: a=1.5, b=-1.8, c=1.6, d=0.9
        self.a = random.uniform(1.2, 2.0) * random.choice([1, -1])
        self.b = random.uniform(1.2, 2.0) * random.choice([1, -1])
        self.c = random.uniform(0.5, 1.5) * random.choice([1, -1])
        self.d = random.uniform(0.5, 1.5) * random.choice([1, -1])
        
        self.points_cache = None
        self.last_update = 0
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        cx, cy = self.get_coords(w, h) # Removed t from get_coords as base doesn't use it for random walking anymore? 
        # Actually base.VisualModule.get_coords(w, h) calls update_center()
        
        level = energy_levels.get(self.key, 0)
        accent = energy_levels.get("accent", 0)
        
        # Audio Reactivity:
        # Slowly mutate the coefficients based on bass/time
        # This causes the shape to morph
        dt = t * 0.1 * self.speed
        
        # Slight jitter on heavy bass to shake the structure 
        jitter = level * 0.05
        
        cur_a = self.a + math.sin(dt) * 0.1
        cur_b = self.b + math.cos(dt * 0.7) * 0.1
        cur_c = self.c + jitter
        cur_d = self.d 
        
        # Python loop optimization
        # We'll just generate them fresh.
        
        pts = []
        x, y = 0.1, 0.1
        
        scale = 300  # Scale of the attractor
        
        # Pre-calc constants to speed up loop
        sin = math.sin
        cos = math.cos
        
        # Limit points for performance based on system load
        limit = self.num_points
        
        for _ in range(limit):
            # Clifford Attractor Equations
            # x_n+1 = sin(a y_n) + c cos(a x_n)
            # y_n+1 = sin(b x_n) + d cos(b y_n)
            nx = sin(cur_a * y) + cur_c * cos(cur_a * x)
            ny = sin(cur_b * x) + cur_d * cos(cur_b * y)
            x, y = nx, ny
            
            # Map to screen
            sx = cx + x * scale
            sy = cy + y * scale
            pts.append((sx, sy))
            
        # Draw points
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             
        # Draw as point cloud (tiny rectangles)
        for px, py in pts:
            # Check bounds simply
            if 0 < px < w and 0 < py < h:
                draw.point((px, py), fill=c)

class HexGrid(VisualModule):
    """
    Renders a honeycomb grid of hexagons that pulse with audio.
    Design / Club aesthetic.
    
    **Updates**:
    - **Calmer**: Larger hexes.
    - **Morphing**: Hexagons rotate and breathe organically.
    """
    def __init__(self, key="mid", color=(255, 255, 255), speed=1.0, complexity=0.5, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.speed = speed
        self.complexity = complexity
        # TUNING: Larger base size (50 -> 70) for calmer look
        self.hex_size = 70 - (20 * complexity) 
        self.spacing = self.hex_size * 1.8 
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        base_cx, base_cy = self.get_coords(w, h)
        level = energy_levels.get(self.key, 0)
        accent = energy_levels.get("accent", 0)
        
        # Grid dimensions coverage
        cols = int(w / self.spacing) + 2
        rows = int(h / (self.hex_size * 1.5)) + 2
        
        start_x = (w - cols * self.spacing) / 2
        start_y = (h - rows * self.hex_size * 1.5) / 2
        
        c = self.color
        
        for r in range(rows):
            for c_idx in range(cols):
                # Calculate grid position
                x = start_x + c_idx * self.spacing
                y = start_y + r * (self.hex_size * 1.5)
                
                # Odd row offset
                if r % 2 == 1:
                    x += self.spacing / 2
                
                # Center offset
                x += (base_cx - w/2)
                y += (base_cy - h/2)
                
                dx = x - base_cx
                dy = y - base_cy
                dist = math.sqrt(dx*dx + dy*dy)
                
                # Wave / Breathing
                # Slower wave speed (4 -> 1)
                wave_phase = dist * 0.005 - t * 1.0 * self.speed
                wave_val = (math.sin(wave_phase) + 1) / 2 
                
                activation = (wave_val * 0.3) + (level * 0.5)
                
                current_size = self.hex_size * (0.4 + 0.6 * activation)
                
                # MORPHING: Rotation
                # Rotate based on distance and time.
                # Bass hits snap the rotation.
                rot = (dist * 0.002) + (t * 0.2) + (level * 1.0)
                
                # Opacity
                alpha = opacity
                if dist > w * 0.6:
                    alpha *= max(0, 1.0 - (dist - w*0.6)/200)
                
                if alpha <= 0.01: continue
                
                final_color = c
                if alpha < 1.0:
                    final_color = (int(c[0]*alpha), int(c[1]*alpha), int(c[2]*alpha))

                # Draw
                self._draw_hex(draw, x, y, current_size, final_color, rot)

    def _draw_hex(self, draw, cx, cy, radius, color, rotation=0):
        points = []
        for i in range(6):
            angle = math.radians(60 * i) + rotation
            px = cx + radius * math.cos(angle)
            py = cy + radius * math.sin(angle)
            points.append((px, py))
        
        draw.polygon(points, outline=color, width=2)
