import math
import random
from .base import VisualModule

class WaveTerrain(VisualModule):
    """
    Simulates the iconic 'Unknown Pleasures' (Joy Division) style waveform landscape.
    """
    def __init__(self, key=None, color=(255, 255, 255), count=20, center=None, drift=None, zoom=1.0):
        center = center or (0.5, 0.5)
        drift = drift or (0.0, 0.0)
        super().__init__(key, center, drift)
        self.color = color
        self.count = count
        self.zoom = zoom 
        self.points = 50 
        self.y_offsets = [0] * self.count
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        
        # Area: Dynamic based on zoom
        fill_ratio = 0.6 + (0.35 * (self.zoom - 0.5)) 
        fill_ratio = max(0.4, min(1.0, fill_ratio))
        
        margin_size = (1.0 - fill_ratio) / 2.0
        margin_top = h * margin_size
        margin_bottom = h * (1.0 - margin_size)
        
        total_h = margin_bottom - margin_top
        step_y = total_h / max(1, self.count - 1)
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             
        # Center X and Spread
        cx = w / 2
        width_spread = w * 0.8 * self.zoom 
        
        for i in range(self.count):
            base_y = margin_top + i * step_y
            points = []
            for j in range(self.points + 1):
                norm_x = (j / self.points) * 2 - 1 
                envelope = math.exp(-3 * (norm_x**2))
                wave = math.sin(norm_x * 4 + t + i*0.4) * 0.3
                wave += math.sin(norm_x * 10 + t * 2) * 0.1
                audio_bump = energy * envelope * 2.5 
                distortion = (wave + audio_bump) * (h * 0.15 * self.zoom) 
                distortion += math.sin(i * 0.9 + t) * (10 * self.zoom)
                
                px = cx + norm_x * (width_spread * 0.5)
                py = base_y - distortion
                points.append((px, py))
            draw.line(points, fill=c, width=2)


class StarField(VisualModule):
    # REMOVED per user request
    pass

class GodRays(VisualModule):
    """
    Rotating beams of light emanating from the center.
    """
    def __init__(self, key=None, color=(255, 255, 255), count=8, center=None, drift=None):
        center = center or (0.5, 0.5)
        drift = drift or (0.0, 0.0)
        super().__init__(key, center, drift)
        self.color = color
        self.count = max(5, count)
        self.angle_offset = 0
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = w/2, h/2
        self.angle_offset += 0.005 + (energy * 0.02)
        radius = math.hypot(w, h) * 0.8
        base_width = (2 * math.pi / self.count) * 0.3 
        width_mod = base_width * (1.0 + energy * 0.5)
        
        c = self.color
        # Tone down alpha
        alpha = 80 * opacity * (0.5 + 0.5*energy) # Max ~80-120/255
        c = (c[0], c[1], c[2], int(alpha))
            
        for i in range(self.count):
            angle_center = self.angle_offset + (i * 2 * math.pi / self.count)
            p1 = (cx, cy)
            a1 = angle_center - width_mod/2
            a2 = angle_center + width_mod/2
            p2 = (cx + math.cos(a1) * radius, cy + math.sin(a1) * radius)
            p3 = (cx + math.cos(a2) * radius, cy + math.sin(a2) * radius)
            draw.polygon([p1, p2, p3], fill=c)

class RippleSystem(VisualModule):
    """
    Minimalist random raindrops/ripples appearing on screen.
    """
    def __init__(self, key=None, color=(255, 255, 255), count=5, center=None, drift=None):
        center = center or (0.5, 0.5)
        drift = drift or (0.0, 0.0)
        super().__init__(key, center, drift)
        self.color = color
        self.ripples = [] 
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        
        # Spawn logic (Energy based but with base chance)
        spawn_chance = 0.05 + (energy * 0.4)
        if random.random() < spawn_chance:
            self.ripples.append({
                'x': random.randint(0, w),
                'y': random.randint(0, h),
                'r': 1,
                'life': 1.0,
                'max_r': random.uniform(50, 200)
            })
            
        # Update and draw
        for r in self.ripples[:]:
            r['r'] += (2 + energy * 8) # Speed up on beat
            r['life'] -= 0.015
            
            if r['life'] <= 0 or r['r'] > r['max_r']:
                self.ripples.remove(r)
                continue
            
            curr_opacity = r['life'] * opacity
            c = self.color
            if len(c) == 3: c = list(c) + [255]
            
            final_c = (c[0], c[1], c[2], int(c[3] * curr_opacity))
            
            draw.ellipse([r['x']-r['r'], r['y']-r['r'], r['x']+r['r'], r['y']+r['r']], outline=final_c, width=2)


class ScanLines(VisualModule):
    """
    CRT Monitor style scanning lines.
    """
    def __init__(self, key=None, color=(255, 255, 255), center=None, drift=None):
        center = center or (0.5, 0.5)
        drift = drift or (0.0, 0.0)
        super().__init__(key, center, drift)
        self.color = color
        self.y_pos = 0
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        
        speed = h * 0.02 * (1 + energy)
        self.y_pos = (self.y_pos + speed) % h
        
        c = self.color
        
        # Faint grid lines first
        grid_alpha = int(30 * opacity)
        grid_c = (c[0], c[1], c[2], grid_alpha)
        
        # Grid jumps on beat
        grid_offset = 0
        if energy > 0.6:
            grid_offset = random.randint(-5, 5)
            
        for i in range(0, h, 30):
             y = i + grid_offset
             draw.line([0, y, w, y], fill=grid_c, width=1)
             
        # Moving Scan Bar
        bar_alpha = int(80 * opacity)
        bar_c = (c[0], c[1], c[2], bar_alpha)
        # Bar height grows with energy
        h_bar = 10 + energy * 40
        draw.rectangle([0, self.y_pos, w, self.y_pos + h_bar], fill=bar_c)

class ParticleDust(VisualModule):
    """
    Subtle ambient dust particles.
    """
    def __init__(self, key=None, color=(255, 255, 255), count=50, center=None, drift=None):
        center = center or (0.5, 0.5)
        drift = drift or (0.0, 0.0)
        super().__init__(key, center, drift)
        self.color = color
        self.particles = [{'x': random.uniform(0, 1), 'y': random.uniform(0, 1), 's': random.uniform(0.5, 2)} for _ in range(count)]
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             
        for p in self.particles:
            # Drift slowly
            p['y'] -= 0.001 * (1 + energy)
            if p['y'] < 0: p['y'] = 1.0
            
            # Wiggle
            x_off = math.sin(t*2 + p['y']*10) * 0.01
            
            px = (p['x'] + x_off) % 1.0 * w
            py = p['y'] * h
            
            s = p['s'] * (1 + energy * 0.5)
            draw.rectangle([px, py, px+s, py+s], fill=c)
