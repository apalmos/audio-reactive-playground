import math
import random
from .base import VisualModule

class CirclePulse(VisualModule):
    """
    A classic audio-visual element: A circle that pumps size with the beat.
    
    **Visual Concept**:
    - A solid or outlined circle expanding from a center point.
    - Concentric rings usually added for depth.
    
    **Audio Reactivity**:
    - **Radius**: Directly mapped to audio energy.
    - **Exponential Curve**: Uses `energy ** 2.0` to make "kicks" punchier while ignoring low-level noise.
    """
    def __init__(self, key=None, color=(255, 50, 50), max_radius_ratio=0.5, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.max_radius_ratio = max_radius_ratio
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        # KICK CURVE: Exponential response for punchy kicks
        energy = energy ** 2.0 
        
        cx, cy = self.get_coords(w, h)
        
        # Base pulsing circle
        radius = int(min(w, h) * self.max_radius_ratio * energy)
        radius = max(10, radius)
        
        # Draw concentric rings for more detail
        for i in range(3):
            r = radius * (1.0 - i * 0.2)
            if r > 0:
                # Fade alpha for outer/inner rings simulation
                c = tuple(int(x * (1.0 - i*0.3)) for x in self.color)
                
                x0, y0 = cx - r, cy - r
                x1, y1 = cx + r, cy + r
                draw.ellipse([x0, y0, x1, y1], outline=c, width=3)

class PolyrhythmShapes(VisualModule):
    """
    Rotating geometric polygons (Triangle, Square, Pentagon...).
    
    **Math/Logic**:
    - Uses polar coordinates `(r, theta)` to draw vertices.
    - `sides` parameter determines shape (3=Triangle, 4=Square).
    
    **Audio Reactivity**:
    - **Rotation Speed**: Increases with audio energy integration.
    - **Size ("Breath")**: Shapes pulse slightly with the beat.
    - **Wobble**: Vertices distort slightly based on `sin(t)` and energy.
    """
    def __init__(self, key=None, base_speed=1.0, colors=None, shape_types=None, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.colors = colors if colors else [(0, 255, 255), (255, 0, 255), (255, 255, 0)]
        self.base_speed = base_speed
        self.shape_types = shape_types if shape_types else [3, 4, 5]
        self.param_smooth = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        base_r = min(w, h) * 0.35
        
        # Smooth accumulation for rotation
        self.param_smooth += (self.base_speed * 0.05) + (energy * 0.1)
        
        for i, sides in enumerate(self.shape_types):
            speed = (i + 1) * 0.5
            angle_offset = self.param_smooth * speed 
            
            color = self.colors[i % len(self.colors)]
            
            breath = math.sin(t * 2 + i) * 0.05 
            size_mod = 1.0 + breath + (energy * 0.3)
            
            points = []
            curr_r = base_r * (0.8 + i * 0.3) * size_mod
            
            for v in range(sides):
                angle = angle_offset + (v * 2 * math.pi / sides)
                wobble = math.sin(t * 5 + v) * 10 * energy
                px = cx + math.cos(angle) * (curr_r + wobble)
                py = cy + math.sin(angle) * (curr_r + wobble)
                points.append((px, py))
            
            if len(points) > 1:
                draw.polygon(points, outline=color, width=4)

class SuperShape(VisualModule):
    """
    Gielis Superformula implementation.
    
    **Math**:
    - A generalization of the ellipse equation that can produce stars, flowers, rounded squares, and complex blobs.
    - Equation: `r(phi) = ...` (complex trigonometric function).
    
    **Audio Reactivity**:
    - **Shape Morphing**: The parameters `n1`, `n2`, `n3` change with audio energy, causing the blob to spike or smooth out.
    """
    def __init__(self, key=None, color=(255, 100, 255), n1=1, n2=1, n3=1, m=6, speed=0.5, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.n1 = n1; self.n2 = n2; self.n3 = n3; self.m = m
        self.speed = speed
        self.params_drift = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        self.params_drift += 0.01 * self.speed
        
        curr_m = self.m + math.sin(self.params_drift) * 2
        curr_n1 = self.n1 + math.cos(self.params_drift * 0.5) * 0.5
        curr_n2 = self.n2 + energy
        curr_n3 = self.n3 + energy
        
        scale = min(w, h) * 0.3 * (1 + energy * 0.2)
        
        points = []
        num_points = 300
        for i in range(num_points + 1):
            phi = (i / num_points) * 2 * math.pi
            a = 1; b = 1
            t1 = abs(math.cos(curr_m * phi / 4) / a) ** curr_n2
            t2 = abs(math.sin(curr_m * phi / 4) / b) ** curr_n3
            try:
                r = 1 / ((t1 + t2) ** (1 / curr_n1))
            except:
                r = 0
            r *= scale
            rot_phi = phi + t * 0.2
            x = cx + r * math.cos(rot_phi)
            y = cy + r * math.sin(rot_phi)
            points.append((x, y))
            
        draw.polygon(points, outline=self.color, width=3)
        draw.polygon([(x,y) for x,y in points], outline=tuple(c//2 for c in self.color), width=1)

class RoamingGeometry(VisualModule):
    """
    Spawns random geometric shapes that traverse the screen.
    
    **Concept**:
    - Decentralized action. Things coming from off-screen.
    
    **Behavior**:
    - **Spawning**: Randomly creates rects, lines, or circles at screen edges.
    - **Movement**: Linear velocity.
    - **Reactivity**: Audio energy boosts their speed and rotation interactively.
    """
    def __init__(self, key=None, color=(255, 255, 255), center=None, drift=None):
        super().__init__(key) # Own position logic
        self.color = color
        self.objects = []
        self.spawn_timer = 0
        
    def draw(self, draw, w, h, t, energy_levels):
        energy = energy_levels.get(self.key, 0)
        self.spawn_timer += 1
        if self.spawn_timer > 20: 
            self.spawn_timer = 0
            if random.random() < 0.5 + (energy * 0.5): 
                side = random.choice(['top', 'bottom', 'left', 'right'])
                # ... (Spawn logic similar to before, summarized)
                # TUNING: Reduced launch velocities (2, 8) -> (1, 4)
                vx = random.uniform(1, 4) if side == 'left' else random.uniform(-4, -1)
                vy = random.uniform(1, 4) if side == 'top' else random.uniform(-4, -1)
                if side in ['bottom', 'right']: vy *= -1; vx *= -1 # Simpler logic
                
                # Randomized spawn bounds
                if side == 'top': x, y = random.randint(0, w), -50; vx=random.uniform(-3,3); vy=random.uniform(1,4)
                elif side == 'bottom': x, y = random.randint(0, w), h+50; vx=random.uniform(-3,3); vy=random.uniform(-4,-1)
                elif side == 'left': x, y = -50, random.randint(0, h); vx=random.uniform(1,4); vy=random.uniform(-3,3)
                else: x, y = w+50, random.randint(0, h); vx=random.uniform(-4,-1); vy=random.uniform(-3,3)

                self.objects.append({
                    'x': x, 'y': y, 'vx': vx, 'vy': vy,
                    'size': random.randint(20, 100),
                    'type': random.choice(['rect', 'line', 'circle']),
                    'rot': random.uniform(0, math.pi*2),
                    'rot_vel': random.uniform(-0.1, 0.1)
                })

        active_objects = []
        for obj in self.objects:
            obj['x'] += obj['vx'] + (obj['vx'] * energy * 2)
            obj['y'] += obj['vy'] + (obj['vy'] * energy * 2)
            obj['rot'] += obj['rot_vel']
            
            cx, cy = obj['x'], obj['y']
            s = obj['size'] * (1 + energy * 0.5)
            c = self.color
            
            if obj['type'] == 'rect':
                 angle = obj['rot']
                 points = []
                 for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                     rx = dx * s/2; ry = dy * s/2
                     rot_x = rx * math.cos(angle) - ry * math.sin(angle)
                     rot_y = rx * math.sin(angle) + ry * math.cos(angle)
                     points.append((cx + rot_x, cy + rot_y))
                 draw.polygon(points, outline=c, width=2)
            elif obj['type'] == 'circle':
                draw.ellipse([cx - s/2, cy - s/2, cx + s/2, cy + s/2], outline=c, width=2)
            elif obj['type'] == 'line':
                 angle = obj['rot']
                 l = s * 2
                 x1 = cx + math.cos(angle) * l/2
                 y1 = cy + math.sin(angle) * l/2
                 x2 = cx - math.cos(angle) * l/2
                 y2 = cy - math.sin(angle) * l/2
                 draw.line([x1, y1, x2, y2], fill=c, width=2)

            margin = 200
            if -margin < obj['x'] < w + margin and -margin < obj['y'] < h + margin:
                active_objects.append(obj)
        self.objects = active_objects
