import math
import random
from .base import VisualModule

class PlatonicSolids(VisualModule):
    """
    Renders 3D rotating wireframe solids (Cube, Octahedron, Tetrahedron).
    
    **Visuals**:
    - A 3D shape spinning in the center.
    - Edges glow with audio energy.
    
    **Audio Reactivity**:
    - **Rotation**: Speed increases with energy.
    - **Scale**: Pulse on bass.
    - **Jitter**: High frequencies shake the vertices.
    """
    def __init__(self, key=None, color=(0, 255, 255), shape="cube", speed=1.0, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.speed = speed
        self.shape_type = random.choice(["cube", "octahedron"])
        self.vertices, self.edges = self._get_shape_data(self.shape_type)
        self.angle_x = 0
        self.angle_y = 0
        self.angle_z = 0
        
    def _get_shape_data(self, shape):
        # Normalized coordinates -1 to 1
        if shape == "cube":
            v = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                 (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]
            e = [(0,1), (1,2), (2,3), (3,0), # Back face
                 (4,5), (5,6), (6,7), (7,4), # Front face
                 (0,4), (1,5), (2,6), (3,7)] # Connecting lines
            return v, e
        elif shape == "octahedron":
             v = [(0, 1, 0), (0, -1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)]
             e = [(0,2), (0,3), (0,4), (0,5), # Top pyramid
                  (1,2), (1,3), (1,4), (1,5), # Bottom pyramid
                  (2,4), (4,3), (3,5), (5,2)] # Middle ring
             return v, e
        return [], []
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        cx, cy = self.get_coords(w, h)
        energy = energy_levels.get(self.key, 0)
        e_high = energy_levels.get("high", 0)
        
        # Rotation
        gradual = 0.02 * self.speed
        boost = energy * 0.1
        self.angle_x += gradual + boost
        self.angle_y += gradual * 0.5 + boost * 0.5
        self.angle_z += gradual * 0.2
        
        scale = min(w, h) * 0.3 * (1 + energy * 0.3)
        
        # 3D Projection Calculation
        points_2d = []
        
        # Jitter vertices on high freq
        jitter_amt = e_high * 0.2
        
        for x, y, z in self.vertices:
            # Jitter
            if jitter_amt > 0.1:
                x += random.uniform(-jitter_amt, jitter_amt)
                y += random.uniform(-jitter_amt, jitter_amt)
                z += random.uniform(-jitter_amt, jitter_amt)
                
            # Rotation Matrices
            # Rotate X
            sy, cy_rot = math.sin(self.angle_x), math.cos(self.angle_x)
            y, z = y * cy_rot - z * sy, y * sy + z * cy_rot
            
            # Rotate Y
            sx, cx_rot = math.sin(self.angle_y), math.cos(self.angle_y)
            x, z = x * cx_rot + z * sx, -x * sx + z * cx_rot
            
            # Rotate Z
            sz, cz_rot = math.sin(self.angle_z), math.cos(self.angle_z)
            x, y = x * cz_rot - y * sz, x * sz + y * cz_rot
            
            # Perspective Project
            focal_length = 4
            z_offset = 5
            factor = focal_length / (z + z_offset)
            
            px = cx + x * scale * factor
            py = cy + y * scale * factor
            points_2d.append((px, py))
            
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             
        # Draw Edges
        # Line width based on energy
        lw = max(2, int(2 + energy * 8))
        
        for i, j in self.edges:
            p1 = points_2d[i]
            p2 = points_2d[j]
            draw.line([p1, p2], fill=c, width=lw)
            
        # Draw Vertices (Dots)
        for px, py in points_2d:
            r = 3 + int(energy * 5)
            draw.ellipse([px-r, py-r, px+r, py+r], fill=c)


class EqualizerRing(VisualModule):
    """
    Circular spectrum analyzer style.
    Renders radial bars around a center point.
    """
    def __init__(self, key=None, color=(0, 255, 0), bars=60, radius_ratio=0.3, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.num_bars = bars
        self.radius_ratio = radius_ratio
        
        # Audio memory to simulate different freq bands per bar
        # We don't have true fft bins per bar, so we simulate it with noise + energy
        self.bar_levels = [0.0] * bars
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        cx, cy = self.get_coords(w, h)
        
        # Audio inputs
        bass = energy_levels.get("bass", 0)
        mid = energy_levels.get("mid", 0)
        high = energy_levels.get("high", 0)
        
        base_r = min(w, h) * self.radius_ratio
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
        
        # Update fake FFT bars
        for i in range(self.num_bars):
            # Map bar index to frequency roughly
            # 0-20: Bass, 20-40: Mid, 40-60: High
            target = 0
            if i < self.num_bars // 3:
                target = bass * random.uniform(0.8, 1.2)
            elif i < 2 * self.num_bars // 3:
                target = mid * random.uniform(0.8, 1.2)
            else:
                target = high * random.uniform(0.8, 1.2)
            
            # Smooth decay
            self.bar_levels[i] = self.bar_levels[i] * 0.8 + target * 0.2
            
        angle_step = 2 * math.pi / self.num_bars
        
        for i, level in enumerate(self.bar_levels):
            angle = i * angle_step - math.pi/2 # Start at top
            
            # Rotation drift?
            angle += t * 0.2
            
            bar_h = 10 + level * (min(w, h) * 0.2)
            
            # Inner point
            x1 = cx + math.cos(angle) * base_r
            y1 = cy + math.sin(angle) * base_r
            
            # Outer point
            x2 = cx + math.cos(angle) * (base_r + bar_h)
            y2 = cy + math.sin(angle) * (base_r + bar_h)
            
            draw.line([x1, y1, x2, y2], fill=c, width=4)


class BinaryRain(VisualModule):
    """
    Digital Matrix-style rain.
    Falling vertical strips of rectangular blocks.
    """
    def __init__(self, key=None, color=(0, 255, 0), count=40, center=None, drift=None):
        super().__init__(key) # Full screen
        self.color = color
        self.columns = [] 
        self.count = count # Number of active columns
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        
        # Initialize columns if empty
        if not self.columns:
            for _ in range(self.count):
                self.columns.append({
                    'x': random.randint(0, w),
                    'y': random.randint(-h, 0),
                    'speed': random.uniform(5, 15),
                    'len': random.randint(5, 15), # Number of blocks in tail
                    'width': random.randint(10, 30)
                })
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             
        for col in self.columns:
            # Update Position
            speed_boost = 1 + energy * 2
            col['y'] += col['speed'] * speed_boost
            
            # Reset if off screen
            if col['y'] - (col['len'] * 30) > h:
                col['y'] = random.randint(-500, -100)
                col['x'] = random.randint(0, w)
                
            # Draw tail
            # We draw discrete rectangles
            block_h = 20
            gap = 5
            
            for i in range(col['len']):
                by = col['y'] - i * (block_h + gap)
                if by > h or by < -50: continue
                
                # Alpha fade for tail
                alpha = 1.0 - (i / col['len'])
                
                # Random glitch: some blocks missing
                if random.random() > 0.9: continue
                
                # Color fade
                bc = (int(c[0]*alpha), int(c[1]*alpha), int(c[2]*alpha))
                
                draw.rectangle([col['x'], by, col['x'] + col['width'], by + block_h], fill=bc)
