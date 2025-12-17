import math
import random
from .base import VisualModule

class WaveformSpiral(VisualModule):
    """
    A logarithmic spiral that acts as a circular waveform oscilloscope.
    
    **Math/Logic**:
    - Logarithmic spiral equation: `r = a * e^(b * theta)`.
    
    **Audio Reactivity**:
    - **Expansion**: The spiral unwinds/expands with energy.
    - **Distortion (The "Waveform")**: High energy adds a high-frequency sine wave jitter to the line, simulating an audio waveform wrapping around the spiral.
    """
    def __init__(self, key=None, color=(100, 100, 255), speed=2.0, b_growth=0.15, distortion=1.0, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.speed = speed
        self.b = b_growth # how loose the spiral is
        self.distortion = distortion
        self.rotation_accum = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        self.rotation_accum += (self.speed * 0.02) + (energy * 0.05)
        
        num_points = 100
        points = []
        
        for i in range(num_points):
            theta = i * 0.2 + self.rotation_accum
            base_r = 5 * math.exp(self.b * i * 0.2) 
            
            expansion = 1.0 + (energy * 0.5 * math.sin(i * 0.1 + t))
            r = base_r * expansion
            
            wobble_x = math.sin(t * 10 + i * 0.5) * 10 * energy * self.distortion
            wobble_y = math.cos(t * 9 + i * 0.5) * 10 * energy * self.distortion
            
            x = cx + math.cos(theta) * r + wobble_x
            y = cy + math.sin(theta) * r + wobble_y
            points.append((x, y))
            
        draw.line(points, fill=self.color, width=2)
        
        # Mirror symmetry
        points_mirror = []
        for p in points:
             dx, dy = p[0] - cx, p[1] - cy
             points_mirror.append((cx - dx, cy - dy))
        draw.line(points_mirror, fill=self.color, width=2)

class LissajousCurve(VisualModule):
    """
    Draws Lissajous figures (complex harmonic motion).
    
    **Math**:
    - `x = A * sin(a*t + delta)`
    - `y = B * sin(b*t)`
    - The ratio `a/b` determines the knot complexity.
    
    **Audio Reactivity**:
    - **Delta (Phase)**: Audio energy speeds up the phase shift, making the knot rotate/morph faster.
    - **Jitter**: High energy adds noise to the phase, making the lines vibrate.
    """
    def __init__(self, key=None, color=(255, 255, 255), speed=0.5, complexity=3, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.speed = speed
        self.complexity = complexity
        self.a = random.randint(1, 5)
        self.b = random.randint(1, 5)
        self.delta = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        scale = min(w, h) * 0.4
        
        self.delta += self.speed * 0.01 + (energy * 0.05)
        phase_jitter = energy * 0.5
        
        points = []
        steps = 200 
        for i in range(steps + 1):
            T = (i / steps) * 2 * math.pi
            
            curr_a = self.a + math.sin(t * 0.1) * 0.5
            curr_b = self.b + math.cos(t * 0.1) * 0.5
            
            x = cx + scale * math.sin(curr_a * T + self.delta + phase_jitter)
            y = cy + scale * math.sin(curr_b * T)
            
            points.append((x, y))
            
        # Draw multiple echoing lines
        for offset in [0, 2, 4]:
             if offset == 0:
                 c = self.color
                 wid = 3
             else:
                 c = tuple(max(0, val - 100) for val in self.color)
                 wid = 1
             draw.line(points, fill=c, width=wid)

class MoirePattern(VisualModule):
    """
    Creates interference patterns (Moiré) by overlapping two similar grids/shapes.
    
    **Visuals**:
    - Two sets of concentric rings.
    
    **Audio Reactivity**:
    - **Offset**: One set of rings moves/jiggles relative to the other based on audio. This small movement creates huge, rippling interference visual artifacts.
    """
    def __init__(self, key=None, color=(255, 255, 255), center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.rotation = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        max_r = min(w, h) * 0.6
        # TUNING: Increased step 15 -> 40 to reduce ring count (less lines)
        step = 40
        
        offset_x = math.sin(t) * 10 + (energy * 20)
        offset_y = math.cos(t) * 10
        self.rotation += 0.01 + energy * 0.05
        
        for r in range(10, int(max_r), step):
            # Ring 1
            x0, y0 = cx - r, cy - r
            x1, y1 = cx + r, cy + r
            draw.ellipse([x0, y0, x1, y1], outline=self.color, width=1)
            
            # Ring 2 (Modified)
            r2 = r * (1.0 + math.sin(t * 0.5) * 0.05)
            x0b, y0b = cx + offset_x - r2, cy + offset_y - r2
            x1b, y1b = cx + offset_x + r2, cy + offset_y + r2
            c2 = (self.color[0], self.color[1], 255) 
            draw.ellipse([x0b, y0b, x1b, y1b], outline=c2, width=1)
