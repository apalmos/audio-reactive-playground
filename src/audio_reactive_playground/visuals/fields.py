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
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
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
                    # Global Opacity
                    alpha = int(alpha * opacity)
                    if alpha > 10:
                        wid = int((1 - dist/200) * 8 * energy)
                        draw.line([x1, y1, x2, y2], fill=self.color, width=wid)
                        
        for x, y in self.points:
             r = 5 + int(energy * 15)
             c = self.color
             if opacity < 1.0:
                 c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             draw.ellipse([x-r, y-r, x+r, y+r], fill=c)

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
        # TUNING: Reduced default count 50 -> 20 (User req: fewer lines)
        super().__init__(key) 
        self.color = color
        self.count = count # Note: main.py passes override, we should tune main.py too
        self.particles = []
        self.noise_offset = 0

    # ... inside draw ...

    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        e_bass = energy_levels.get("bass", 0) ** 3.0
        e_mid = energy_levels.get("mid", 0)
        
        if not self.particles:
            for _ in range(self.count):
                # [x, y, speed_mod, life, max_life]
                self.particles.append([
                    random.random() * w, 
                    random.random() * h, 
                    random.uniform(0.5, 1.5),
                    random.uniform(0, 1.0), # Current life
                    random.uniform(0.5, 2.0) # Decay rate (lower = longer)
                ])
                
        self.noise_offset += 0.005 + e_mid * 0.02 # Slower noise evolution
        scale = 0.005 
        
        new_particles = []
        for p in self.particles:
            x, y, s, life, decay_rate = p
            
            # Life Cycle
            life -= 0.02 * decay_rate
            if life <= 0:
                # Reset
                x = random.random() * w
                y = random.random() * h
                life = 1.0
                
            angle = (x * scale) + (y * scale) + self.noise_offset * 5
            angle += math.sin(y * 0.01 + t) 
            
            # TUNING: Drastically reduced speed for "Calmer" feel
            speed = 1.0 * s + (e_bass * 8)
            
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            x += vx
            y += vy
            x %= w
            y %= h
            
            # Draw with fading alpha
            # Fade in/out sine curve based on life
            alpha_mod = math.sin(life * math.pi) 
            # Make trails fainter overall
            alpha_mod *= 0.7 
            
            c = self.color
            final_alpha = opacity * alpha_mod
            
            if final_alpha < 1.0:
                 c = (int(c[0]*final_alpha), int(c[1]*final_alpha), int(c[2]*final_alpha))
            
            # Only draw if visible
            if final_alpha > 0.05:
                draw.line([x-vx*2, y-vy*2, x, y], fill=c, width=2)
            
            new_particles.append([x, y, s, life, decay_rate])
        self.particles = new_particles

class CrossHatch(VisualModule):
    # ...
    def __init__(self, key=None, color=(255, 255, 255), count=10, center=None, drift=None):
        super().__init__(key)
        self.color = color
        self.base_count = count
        # lines now have 'life'
        self.lines = [] # {x, y, angle, length, speed, life, max_life}
        self.spawn_trigger = 0.0
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        
        # Spawn initial
        if len(self.lines) < self.base_count:
            self.lines.append({
                'x': random.randint(0, w),
                'y': random.randint(0, h),
                'angle': random.choice([0, math.pi/2, math.pi/4, -math.pi/4]),
                'length': random.randint(100, 500),
                'speed': random.uniform(1, 3) * random.choice([1, -1]),
                'life': 0.0,
                'state': 'in' # in, sustain, out
            })
            
        # Multiply logic...
        # ...
        
        # Update lines
        if len(self.lines) > 8: # TUNING: Hard cap reduced 10 -> 8
             self.lines = self.lines[-8:]
             
        active_lines = []
        for l in self.lines:
            # Lifecycle
            if l['state'] == 'in':
                l['life'] += 0.05
                if l['life'] >= 1.0: l['state'] = 'sustain'
            elif l['state'] == 'sustain':
                # Random decay trigger? Or sustain for a bit
                if random.random() < 0.01: l['state'] = 'out'
            elif l['state'] == 'out':
                 l['life'] -= 0.05
            
            if l['life'] <= 0 and l['state'] == 'out':
                continue # Die
                
            active_lines.append(l)
            
            # Move...
            l['x'] += math.cos(l['angle']) * l['speed'] * (1 + energy)
            l['y'] += math.sin(l['angle']) * l['speed'] * (1 + energy)
            
            # Draw with Alpha
            alpha = max(0.0, min(1.0, l.get('life', 1.0)))
            c = self.color
            if opacity < 1.0: alpha *= opacity
            
            if alpha < 1.0:
                 c = (int(c[0]*alpha), int(c[1]*alpha), int(c[2]*alpha))
                 
            x1 = l['x'] - math.cos(l['angle']) * l['length']/2
            y1 = l['y'] - math.sin(l['angle']) * l['length']/2
            x2 = l['x'] + math.cos(l['angle']) * l['length']/2
            y2 = l['y'] + math.sin(l['angle']) * l['length']/2
            
            draw.line([x1, y1, x2, y2], fill=c, width=2)
            
        self.lines = active_lines
