import math
import random
from .base import VisualModule

class WaveformSpiral(VisualModule):
    """
    A logarithmic spiral that acts as a circular waveform oscilloscope.
    
    **Math/Logic**:
    - Logarithmic spiral equation: `r = a * e^(b * theta)`.
    
    **Audio Reactivity**:
    - **NO SPIN**: The spiral structure is fixed.
    - **Unwinding**: The `b` parameter (looseness) reacts to energy, making the spiral "unwind" like a spring on kicks.
    - **Distortion**: High energy adds a sine wave ripple.
    """
    def __init__(self, key=None, color=(100, 100, 255), speed=2.0, b_growth=0.15, distortion=1.0, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.speed = speed
        self.b = b_growth 
        self.distortion = distortion
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        # Dynamic Spiral Tightness
        # Kicks make it unwind (lower b value effectively checks radius growth, 
        # but here we can modulate 'expansion' factor)
        
        num_points = 120
        points = []
        
        for i in range(num_points):
            # Static Theta (No Rotation)
            # We add a tiny offset based on time to make the waves travel OUTWARDS
            theta = i * 0.2 
            
            base_r = 5 * math.exp(self.b * i * 0.2) 
            
            # Expansion: Energy pushes lines out radially
            expansion = 1.0 + (energy * 0.3 * math.sin(i * 0.2))
            r = base_r * expansion
            
            # Waveform jitter travels along the line
            travel = t * 10 * self.speed_factor
            wobble_x = math.sin(travel + i * 0.5) * 15 * energy * self.distortion
            wobble_y = math.cos(travel * 0.9 + i * 0.5) * 15 * energy * self.distortion
            
            x = cx + math.cos(theta) * r + wobble_x
            y = cy + math.sin(theta) * r + wobble_y
            points.append((x, y))
            
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
        draw.line(points, fill=c, width=2)
        
        # Mirror symmetry
        points_mirror = []
        for p in points:
             dx, dy = p[0] - cx, p[1] - cy
             points_mirror.append((cx - dx, cy - dy))
        draw.line(points_mirror, fill=c, width=2)

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
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        scale = min(w, h) * 0.4
        
        # Slow evolution
        self.delta += self.speed * 0.01 + (energy * 0.02)
        
        # Jitter on high energy
        phase_jitter = energy * 0.3
        
        points = []
        steps = 200 
        for i in range(steps + 1):
            T = (i / steps) * 2 * math.pi
            
            # Morph the A/B parameters slightly with time
            curr_a = self.a + math.sin(t * 0.2) * 0.2
            curr_b = self.b + math.cos(t * 0.23) * 0.2
            
            x = cx + scale * math.sin(curr_a * T + self.delta + phase_jitter)
            y = cy + scale * math.sin(curr_b * T)
            
            points.append((x, y))
            
        # Draw multiple echoing lines
        for offset in [0, 2, 4]:
             if offset == 0:
                 c = self.color
                 if opacity < 1.0:
                     c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
                 wid = 3
             else:
                 c = tuple(max(0, val - 100) for val in self.color)
                 if opacity < 1.0:
                     c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
                 wid = 1
             draw.line(points, fill=c, width=wid)

class MoirePattern(VisualModule):
    """
    Creates interference patterns (Moiré) by overlapping two similar grids/shapes.
    
    **Visuals**:
    - Two sets of concentric rings.
    
    **Audio Reactivity**:
    - **NO SPIN**: Purely translational interference.
    - **Offset**: One set of rings moves/jiggles relative to the other based on audio. This small movement creates huge, rippling interference visual artifacts.
    """
    def __init__(self, key=None, color=(255, 255, 255), center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        max_r = min(w, h) * 0.6
        step = 40
        
        # Offset X/Y driven by Sine time + Energy Kinds
        offset_x = math.sin(t * 0.5) * 30 + (energy * 40)
        offset_y = math.cos(t * 0.4) * 30
        
        # Rings 1: Static-ish centered
        for r in range(10, int(max_r), step):
            c1 = self.color
            if opacity < 1.0:
                c1 = (int(c1[0]*opacity), int(c1[1]*opacity), int(c1[2]*opacity))
            
            # Breathing radius
            r_breath = r + math.sin(t + r) * 5
            
            x0, y0 = cx - r_breath, cy - r_breath
            x1, y1 = cx + r_breath, cy + r_breath
            draw.ellipse([x0, y0, x1, y1], outline=c1, width=1)
            
            # Rings 2: Offset to create Moiré
            # We scale r2 slightly differently
            r2 = r_breath * 1.02
            x0b, y0b = cx + offset_x - r2, cy + offset_y - r2
            x1b, y1b = cx + offset_x + r2, cy + offset_y + r2
            c2 = (self.color[0], self.color[1], 255) 
            if opacity < 1.0:
                c2 = (int(c2[0]*opacity), int(c2[1]*opacity), int(c2[2]*opacity))
            draw.ellipse([x0b, y0b, x1b, y1b], outline=c2, width=1)
