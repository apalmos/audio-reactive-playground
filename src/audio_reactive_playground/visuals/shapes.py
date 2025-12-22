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
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        # KICK CURVE
        energy = energy ** 2.0 
        
        cx, cy = self.get_coords(w, h)
        
        # IDLE: Breathe
        idle_breath = 0.15 + 0.05 * math.sin(t * 1.5)
        
        active_ratio = self.max_radius_ratio * energy 
        target_ratio = max(idle_breath, active_ratio)
        
        radius = int(min(w, h) * target_ratio)
        if radius < 5: radius = 5
        
        # Draw concentric rings expansion (Always moving)
        # Phase shift based on time so they "flow" outwards constantly
        points = 5
        for i in range(points):
            # Constant outward flow: (t + offset) % 1.0
            phase = (t * 0.4 + i / points) % 1.0
            
            # Radius grows with phase
            r = radius + (min(w, h) * 0.45) * phase
            
            # Opacity fades as it goes out (1.0 -> 0.0)
            alpha = (1.0 - phase) * opacity
            
            c_list = list(self.color)
            if len(c_list) == 3: c_list.append(255)
            # Modulate color brightness slightly with energy
            bright = 1.0 + energy if i == 0 else 1.0
            
            final_c = tuple([int(min(255, c * bright)) for c in c_list[:3]] + [int(c_list[3] * alpha)])
            
            x0, y0 = cx - r, cy - r
            x1, y1 = cx + r, cy + r
            
            # Center ring is solid-ish if energy high
            width = 2
            if i == 0 and energy > 0.2:
                 draw.ellipse([x0, y0, x1, y1], outline=final_c, width=4)
            else:
                 draw.ellipse([x0, y0, x1, y1], outline=final_c, width=width)

class PolyrhythmShapes(VisualModule):
    """
    Geometric polygons (Triangle, Square, Pentagon...).
    
    **Math/Logic**:
    - Uses polar coordinates `(r, theta)` to draw vertices.
    - `sides` parameter determines shape (3=Triangle, 4=Square).
    
    **Audio Reactivity**:
    - **Evolution**: Vertices drift and morph.
    - **Subtle Spin**: Shapes rotate very slowly (planetary drift).
    - **Size ("Breath")**: Shapes pulse with the beat.
    """
    def __init__(self, key=None, base_speed=1.0, colors=None, shape_types=None, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.colors = colors if colors else [(0, 255, 255), (255, 0, 255), (255, 255, 0)]
        self.base_speed = base_speed
        self.shape_types = shape_types if shape_types else [3, 4, 5]
        self.param_smooth = 0
        self.rotation = 0
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        base_r = min(w, h) * 0.35
        
        # Subtle planetary drift (User requested drift back)
        self.rotation += 0.002
        
        # Smooth accumulation for morphing
        self.param_smooth += 0.005 
        
        for i, sides in enumerate(self.shape_types):
            # Base angle + Slow Drift + Tiny sine flux
            angle_offset = (i * 0.5) + self.rotation + math.sin(t * 0.2 + i) * 0.1
            
            color = self.colors[i % len(self.colors)]
            
            # Apply Opacity (Hack for Outline)
            if opacity < 1.0:
                r, g, b = color[:3]
                color = (int(r * opacity), int(g * opacity), int(b * opacity))
            
            # Breathing: High energy pushes vertices out
            breath = math.sin(t * 2 + i) * 0.05 
            size_mod = 1.0 + breath + (energy * 0.4)
            
            points = []
            curr_r = base_r * (0.8 + i * 0.3) * size_mod
            
            for v in range(sides):
                angle = angle_offset + (v * 2 * math.pi / sides)
                
                # Morphing: Vertices wander individually based on audio
                wobble = math.sin(t * 3 + v * 1.5) * 30 * energy
                
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
    - **No Spin**: The shape is fixed in orientation.
    - **Shape Morphing**: High energy dramatically alters `m` (spikes) and `n1` (pinch), making the blob spasm/evolve.
    """
    def __init__(self, key=None, color=(255, 100, 255), n1=1, n2=1, n3=1, m=6, speed=0.5, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.n1 = n1; self.n2 = n2; self.n3 = n3; self.m = m
        self.speed = speed
        self.params_drift = 0
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        self.params_drift += 0.005 * self.speed
        
        # PARAMETER MORPHING:
        # m = number of points. Bass kicks make it spikey (increase m)
        curr_m = self.m + (energy * 4.0) 
        
        # n1 = pinching. Energy makes it tighter.
        curr_n1 = self.n1 + math.sin(t) * 0.2 + (energy * 0.5)
        
        curr_n2 = self.n2 + energy
        curr_n3 = self.n3 + energy
        
        scale = min(w, h) * 0.35 * (1 + energy * 0.1)
        
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
            
            # NO ROTATION: Just static phi
            # We add a tiny 'ooze' using sin(t) to r
            r += math.sin(phi * 5 + t) * 5
            
            x = cx + r * math.cos(phi)
            y = cy + r * math.sin(phi)
            points.append((x, y))
            
        # Opacity Dimming
        r, g, b = self.color
        main_color = (int(r * opacity), int(g * opacity), int(b * opacity))
        dim_color = (int(r * 0.5 * opacity), int(g * 0.5 * opacity), int(b * 0.5 * opacity))

        draw.polygon(points, outline=main_color, width=3)
        draw.polygon([(x,y) for x,y in points], outline=dim_color, width=1)

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
        
        # PRE-SEED: Don't start empty!
        self._seed_objects(15)
        
    def _seed_objects(self, count):
        # Fake screen dimensions for seeding
        w, h = 1000, 1000 
        for _ in range(count):
             self._add_object(w, h, random_pos=True)
             
    def _add_object(self, w, h, random_pos=False):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        # Velocities
        vx = random.uniform(1, 4) if side == 'left' else random.uniform(-4, -1)
        vy = random.uniform(1, 4) if side == 'top' else random.uniform(-4, -1)
        if side in ['bottom', 'right']: vy *= -1; vx *= -1
        
        # Position
        if random_pos:
            x, y = random.randint(0, w), random.randint(0, h)
        else:
            if side == 'top': x, y = random.randint(0, w), -50
            elif side == 'bottom': x, y = random.randint(0, w), h+50
            elif side == 'left': x, y = -50, random.randint(0, h)
            else: x, y = w+50, random.randint(0, h)
            
        self.objects.append({
            'x': x, 'y': y, 'vx': vx, 'vy': vy,
            'size': random.randint(20, 100),
            'type': random.choice(['rect', 'line', 'circle']),
            'rot': random.uniform(0, math.pi*2),
            'rot_vel': random.uniform(-0.1, 0.1)
        })
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
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
            if opacity < 1.0:
                 c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
            
            # Helper to generate shape points
            shape_points = []
            if obj['type'] == 'rect':
                 angle = obj['rot']
                 for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                     rx = dx * s/2; ry = dy * s/2
                     rot_x = rx * math.cos(angle) - ry * math.sin(angle)
                     rot_y = rx * math.sin(angle) + ry * math.cos(angle)
                     shape_points.append((cx + rot_x, cy + rot_y))
                     
            elif obj['type'] == 'circle':
                pass 
                
            elif obj['type'] == 'line':
                 angle = obj['rot']
                 l = s * 2
                 x1 = cx + math.cos(angle) * l/2
                 y1 = cy + math.sin(angle) * l/2
                 x2 = cx - math.cos(angle) * l/2
                 y2 = cy - math.sin(angle) * l/2
                 shape_points = [(x1, y1), (x2, y2)]

            # define drawing helper
            def draw_shape(pts, is_circle=False):
                if is_circle:
                    px, py = pts
                    draw.ellipse([px - s/2, py - s/2, px + s/2, py + s/2], outline=c, width=2)
                elif len(pts) == 2:
                    draw.line(pts, fill=c, width=2)
                else:
                    draw.polygon(pts, outline=c, width=2)

            # Draw 4 variations
            if obj['type'] == 'circle':
                 draw_shape((cx, cy), is_circle=True)
                 draw_shape((w-cx, cy), is_circle=True)
                 draw_shape((cx, h-cy), is_circle=True)
                 draw_shape((w-cx, h-cy), is_circle=True)
            else:
                 draw_shape(shape_points)
                 draw_shape([(w-x, y) for x, y in shape_points])
                 draw_shape([(x, h-y) for x, y in shape_points])
                 draw_shape([(w-x, h-y) for x, y in shape_points])

            margin = 200
            if -margin < obj['x'] < w + margin and -margin < obj['y'] < h + margin:
                active_objects.append(obj)
        self.objects = active_objects
