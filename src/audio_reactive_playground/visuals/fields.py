import math
import random
from .base import VisualModule

class VoronoiEffect(VisualModule):
    """
    Simulates a biological cell structure or network.
    
    **Visuals**:
    - Dots moving randomly.
    - Lines drawn between dots ONLY if they are close enough.
    
    **Audio Reactivity**:
    - **Velocity**: Points move faster on bass.
    - **Connections**: Line thickness pulses with energy.
    """
    def __init__(self, key=None, color=(0, 255, 0), count=15, center=None, drift=None):
        # Ignores center/drift mostly, fills screen
        # TUNING: Reduced default count from 20 -> 15 for less clutter
        super().__init__(key)
        self.color = color
        self.count = count
        self.points = []
        self.velocities = []
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        e_bass = energy_levels.get("bass", 0) ** 2
        
        if not self.points:
            for _ in range(self.count):
                self.points.append([random.random() * w, random.random() * h])
                self.velocities.append([random.uniform(-2, 2), random.uniform(-2, 2)])
                
        # Move points
        for i in range(self.count):
            self.points[i][0] += self.velocities[i][0] * (1 + e_bass * 5)
            self.points[i][1] += self.velocities[i][1] * (1 + e_bass * 5)
            
            # Bounce
            if self.points[i][0] < 0 or self.points[i][0] > w: self.velocities[i][0] *= -1
            if self.points[i][1] < 0 or self.points[i][1] > h: self.velocities[i][1] *= -1
            
        # Draw connectivity (Net)
        for i in range(self.count):
            for j in range(i + 1, self.count):
                x1, y1 = self.points[i]
                x2, y2 = self.points[j]
                
                dist = math.hypot(x2-x1, y2-y1)
                # TUNING: Reduced connection distance from 300 -> 200 to reduce spiderweb mess
                if dist < 200:
                    alpha = int(255 * (1 - dist/200) * (0.5 + energy))
                    if alpha > 10:
                        wid = int((1 - dist/200) * 8 * energy)
                        draw.line([x1, y1, x2, y2], fill=self.color, width=wid)
                        
        for x, y in self.points:
             r = 5 + int(energy * 15)
             draw.ellipse([x-r, y-r, x+r, y+r], fill=self.color)

class FlowField(VisualModule):
    """
    Simulates fluid or wind dynamics.
    
    **Math**:
    - uses a noise-like lookup (Perlin noise approximation) to determine angle/direction at any point `(x,y)`.
    
    **Visuals**:
    - Thousands of short trailing lines that trace the hidden flow field.
    
    **Audio Reactivity**:
    - **Chaos**: Music energy shifts the noise offset, making the flow chaotic/turbulent.
    - **Speed**: Particles move faster on beat.
    """
    def __init__(self, key=None, color=(0, 255, 255), count=30, center=None, drift=None):
        # TUNING: Reduced default count 50 -> 30
        super().__init__(key) # Full screen
        self.color = color
        self.count = count
        self.particles = []
        self.noise_offset = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        e_bass = energy_levels.get("bass", 0) ** 3.0
        e_mid = energy_levels.get("mid", 0)
        
        if not self.particles:
            for _ in range(self.count):
                self.particles.append([random.random() * w, random.random() * h, random.uniform(0.5, 1.5)])
                
        self.noise_offset += 0.01 + e_mid * 0.05
        scale = 0.005 
        
        new_particles = []
        for p in self.particles:
            x, y, s = p
            
            angle = (x * scale) + (y * scale) + self.noise_offset * 5
            angle += math.sin(y * 0.01 + t) 
            
            # TUNING: Reduced bass speed influence 40 -> 20
            speed = 2 * s + (e_bass * 20)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            x += vx
            y += vy
            x %= w
            y %= h
            
            draw.line([x-vx, y-vy, x, y], fill=self.color, width=2)
            new_particles.append([x, y, s])
        self.particles = new_particles

class CrossHatch(VisualModule):
    """
    Geometric "Sketchy" effect with multiplying lines.
    
    **Visuals**:
    - Lines travelling straight across the screen.
    - When they hit a beat, they split/spawn new lines perpendicular to themselves.
    
    **Complexity**:
    - Limits total lines to 20 to maintain performance.
    """
    def __init__(self, key=None, color=(255, 255, 255), count=10, center=None, drift=None):
        super().__init__(key) # Full screen
        self.color = color
        self.base_count = count
        self.lines = [] # {x, y, angle, length, speed}
        self.spawn_trigger = 0.0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        
        # Spawn initial lines
        if len(self.lines) < self.base_count:
            self.lines.append({
                'x': random.randint(0, w),
                'y': random.randint(0, h),
                'angle': random.choice([0, math.pi/2, math.pi/4, -math.pi/4]),
                'length': random.randint(100, 500),
                # TUNING: Reduced speed range (2, 5) -> (1, 3)
                'speed': random.uniform(1, 3) * random.choice([1, -1])
            })
            
        # Multiply on bass hit
        # TUNING: Reduced probability 0.2 -> 0.1
        if energy > 0.75 and random.random() < 0.1:
            # Pick a random line and spawn a perpendicular one
            if self.lines:
                parent = random.choice(self.lines)
                self.lines.append({
                    'x': parent['x'],
                    'y': parent['y'],
                    'angle': parent['angle'] + math.pi/2,
                    'length': parent['length'] * 0.8,
                    'speed': parent['speed'] * 1.5
                })
        
        # Limit total lines to avoid lag and visual clutter
        # TUNING: Hard cap at 10 lines
        if len(self.lines) > 10:
            self.lines = self.lines[-10:]
            
        active_lines = []
        for l in self.lines:
            # Move along angle
            l['x'] += math.cos(l['angle']) * l['speed'] * (1 + energy)
            l['y'] += math.sin(l['angle']) * l['speed'] * (1 + energy)
            
            # Draw
            x1 = l['x'] - math.cos(l['angle']) * l['length']/2
            y1 = l['y'] - math.sin(l['angle']) * l['length']/2
            x2 = l['x'] + math.cos(l['angle']) * l['length']/2
            y2 = l['y'] + math.sin(l['angle']) * l['length']/2
            
            draw.line([x1, y1, x2, y2], fill=self.color, width=2)
            
            # Screen bounds check
            margin = 500
            if -margin < l['x'] < w + margin and -margin < l['y'] < h + margin:
                active_lines.append(l)
                
        self.lines = active_lines
