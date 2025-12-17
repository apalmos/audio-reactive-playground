import math
import random
from .base import VisualModule

class TunnelEffect(VisualModule):
    """
    A 3D "Warp Speed" tunnel effect.
    
    **Math**:
    - Uses perspective projection `scale = 1/z` to simulate depth.
    - `z` coordinate loops (modulo) to create infinite forward motion.
    
    **Audio Reactivity**:
    - **Speed**: Tunnel moves faster with audio energy.
    - **Brightness**: Rings flash on kicks.
    """
    def __init__(self, key=None, color=(100, 100, 255), speed=1.0, sides=4, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.speed = speed # TUNING: Default speed reduced in main (was 2.0) but here 1.0 is safer baseline
        self.sides = sides
        self.offset = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        # Move tunnel forward endlessly
        # TUNING: Damped energy influence 50 -> 30
        self.offset += (self.speed * 2) + (energy * 30)
        
        num_rings = 10
        spacing = 200
        
        for i in range(num_rings):
            # Calculate z based on offset phase
            # We want z to go from 1000 down to 10
            # (i * spacing) is fixed steps
            # (self.offset % spacing) creates the motion
            
            base_z = 1000.0 - (i * 100)
            # Apply movement
            z = base_z - (self.offset % 100) 
            
            # This is a bit simplistic loop logic, but works for effect
            if z <= 10: continue
            
            scale = 500 / z 
            r = min(w, h) * scale * 0.5
            
            if r > min(w, h) * 1.5 or r < 5: continue
            
            # Rotate with time
            rot_angle = t * 0.5 + (i * 0.1)
            
            points = []
            for v in range(self.sides):
                angle = rot_angle + (v * 2 * math.pi / self.sides)
                px = cx + math.cos(angle) * r
                py = cy + math.sin(angle) * r
                points.append((px, py))
            
            # Brightness fades with depth
            brightness = max(0, min(1.0, (1000 - z) / 1000))
            if z < 300 and energy > 0.8: brightness = 0.8 # Cap brightness
            
            c = tuple(int(x * brightness) for x in self.color)
            draw.polygon(points, outline=c, width=2)

class FlashEffect(VisualModule):
    """
    Global screen effects for high-intensity moments.
    
    **Visuals**:
    - Instead of full whiteouts (which are blinding), this draws thick glowing borders.
    
    **Audio Reactivity**:
    - **Trigger**: Only fires if energy > 0.8 (hard threshold).
    - **Intensity**: Border width and opacity scale with energy.
    """
    def __init__(self, key=None, color=(255, 255, 255), center=None, drift=None):
        super().__init__(key) # Global
        self.color = color
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        
        # TUNING: Raised threshold 0.8 -> 0.9 to make flashes rare events
        if energy > 0.9:
            border = int(60 * energy) # TUNING: Reduced max border width 100 -> 60
            for i in range(10):
                 inset = i * 2
                 alpha_sim = 0.6 - (i / 20.0) # TUNING: Reduced max opacity 1.0 -> 0.6
                 c = tuple(int(x * alpha_sim) for x in self.color)
                 draw.rectangle([inset, inset, w-inset, h-inset], outline=c, width=int(border/10))
        # TUNING: Removed the secondary "medium energy" flash completely for calmness


class ParticleBurst(VisualModule):
    """
    Simulates fireworks or sparks.
    
    **Behaviors**:
    - **Spawning**: Creates new particles only when energy > threshold (and increased since last frame).
    - **Physics**: Simple velocity `(vx, vy)` and decay (`life`).
    - **Rendering**: Draws fading circles based on particle life.
    """
    def __init__(self, key=None, color=(255, 255, 255), count=30, speed_min=5, speed_max=15, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.count = count
        self.speed_min = speed_min
        self.speed_max = speed_max
        self.particles = [] 
        self.last_energy = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        # Trigger spawn
        if energy > 0.6 and energy > self.last_energy + 0.1:
            for _ in range(self.count // 3): # Burst
                angle = random.random() * 2 * math.pi
                speed = random.uniform(self.speed_min, self.speed_max)
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                self.particles.append([cx, cy, vx, vy, 1.0])
                
        self.last_energy = energy
        
        new_particles = []
        for p in self.particles:
            x, y, vx, vy, life = p
            x += vx
            y += vy
            life -= 0.05
            
            if life > 0:
                c = tuple(int(x * life) for x in self.color)
                r = 3 * life
                draw.ellipse([x-r, y-r, x+r, y+r], fill=c)
                new_particles.append([x, y, vx, vy, life])
                
        self.particles = new_particles
