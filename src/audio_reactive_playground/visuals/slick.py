import math
import random
from .base import VisualModule

class DNAStrand(VisualModule):
    """
    A rotating 3D Double Helix.
    
    **Visuals**:
    - Two intertwined sine waves (strands).
    - Horizontal rungs connecting them.
    - 3D rotation effect.
    
    **Audio Reactivity**:
    - **Rotation**: Speed varies with mid/high energy.
    - **Width**: Expands/contracts with bass (breathing).
    """
    def __init__(self, key=None, color=(0, 255, 128), count=20, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.num_pairs = max(10, count) # Number of rungs
        self.angle_offset = 0
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        # Audio params
        self.angle_offset += 0.02 + (energy * 0.05)
        
        # Dimensions
        height = min(w, h) * 0.7
        base_width = min(w, h) * 0.15
        width = base_width * (1.0 + energy * 0.5) # Breath
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             
        # Draw pairs
        for i in range(self.num_pairs):
            # Y position (linear down the screen)
            progress = i / (self.num_pairs - 1)
            # Center y around cy
            y = cy - (height/2) + (progress * height)
            
            # Phase for rotation
            # Twist factor: full twist over length?
            twist = 4 * math.pi * progress
            phase = self.angle_offset + twist
            
            # X offsets for the two strands (sine of phase)
            x_off = math.sin(phase) * width
            
            # 3D Depth fake (scale/brightness based on cos)
            z_depth = math.cos(phase) # -1 to 1 (Back to Front)
            
            x1 = cx + x_off
            x2 = cx - x_off
            
            # Draw Rung (if complex enough)
            if self.num_pairs > 15:
                # Dim rung if in back?
                draw.line([x1, y, x2, y], fill=c, width=1)
                
            # Draw Nucleotides (Dots)
            # Scale radius by depth for 3D feel
            r_base = 4 + (energy * 3)
            r1 = r_base * (0.8 + 0.4 * z_depth) # Front bigger
            r2 = r_base * (0.8 - 0.4 * z_depth) # Back smaller
            
            # Strand 1
            draw.ellipse([x1-r1, y-r1, x1+r1, y+r1], fill=c)
            # Strand 2
            draw.ellipse([x2-r2, y-r2, x2+r2, y+r2], fill=c)


class SonarRadar(VisualModule):
    """
    A rotating radar sweep that reveals 'blips' on audio accents.
    Minimalist UI aesthetic.
    """
    def __init__(self, key=None, color=(0, 255, 0), speed=1.0, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.speed = speed
        self.angle = 0
        self.blips = [] # List of (x, y, birth_time, max_r)
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        # inputs
        accent = energy_levels.get("accent", 0)
        
        cx, cy = self.get_coords(w, h)
        radius = min(w, h) * 0.4
        
        # Update sweep
        self.angle += 0.05 * self.speed
        sweep_x = cx + math.cos(self.angle) * radius
        sweep_y = cy + math.sin(self.angle) * radius
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             
        # 1. Draw Ring
        draw.ellipse([cx-radius, cy-radius, cx+radius, cy+radius], outline=c, width=2)
        
        # 2. Draw Sweep Line
        draw.line([cx, cy, sweep_x, sweep_y], fill=c, width=2)
        
        # 3. Handle Blips
        # Spawn on accent
        if accent > 0.7 and random.random() < 0.2:
            # Spawn a blip somewhere within radius
            r_blip = random.uniform(radius * 0.2, radius * 0.9)
            a_blip = random.uniform(0, 6.28)
            bx = cx + math.cos(a_blip) * r_blip
            by = cy + math.sin(a_blip) * r_blip
            self.blips.append({
                'x': bx, 'y': by, 't': t, 'size': 5 + accent * 10
            })
            
        # Draw and age blips
        active_blips = []
        for blip in self.blips:
            age = t - blip['t']
            if age < 1.0: # Live for 1 sec
                # Fade
                alpha = 1.0 - age
                # Color fade?
                bc = c
                if alpha < 1.0:
                    bc = (int(c[0]*alpha), int(c[1]*alpha), int(c[2]*alpha))
                
                # Draw Blip (Target)
                sz = blip['size']
                draw.ellipse([blip['x']-sz, blip['y']-sz, blip['x']+sz, blip['y']+sz], outline=bc, width=2)
                # Crosshair
                draw.line([blip['x']-sz, blip['y'], blip['x']+sz, blip['y']], fill=bc, width=1)
                draw.line([blip['x'], blip['y']-sz, blip['x'], blip['y']+sz], fill=bc, width=1)
                
                active_blips.append(blip)
        self.blips = active_blips


class CyberPlane(VisualModule):
    """
    Retro-future perspective grid (Tron/Synthwave style).
    Infinite scrolling ground plane.
    """
    def __init__(self, key=None, color=(255, 0, 255), grid_cols=12, center=None, drift=None):
        super().__init__(key) # Full screen usually
        self.color = color
        self.grid_cols = grid_cols
        self.scroll_z = 0
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        
        # Horizon is at h/2 usually
        horizon_y = h / 2
        bottom_y = h
        
        # Scroll speed
        self.scroll_z += 0.1 + (energy * 0.2)
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
        
        # Draw Vertical Lines (Fan out from center horizon)
        # They emanate from vanish point (w/2, horizon_y)
        cx = w / 2
        
        # Perspective projection params
        # x_screen = (x_world / z) 
        
        # Draw Horizon Line
        draw.line([0, horizon_y, w, horizon_y], fill=c, width=2)
        
        # Draw Verticals
        # Spaced in world coordinates?
        # Simpler: just lines from center to bottom edge
        # We want infinite grid left/right
        for i in range(-self.grid_cols, self.grid_cols + 1):
            # x coordinate at bottom
            x_bottom = cx + (i * (w / (self.grid_cols/2))) * 2 
            # all lines meet at (cx, horizon_y) theoretically if parallel in 3D
            draw.line([cx, horizon_y, x_bottom, bottom_y], fill=c, width=1)
            
        # Draw Horizontal Lines (Scrolling Z)
        # z goes from near to far.
        # Screen y is proportional to 1/z.
        # y = horizon_y + (scale / z)
        
        scale = h / 2
        
        # Loop for z lines
        # Z moves from 1 (near) to 10 (far)
        # phase offset by scroll_z
        
        num_lines = 10
        for i in range(num_lines):
            # Virtual Z distance
            # Line should approach camera (z decreases) then reset
            # base_z = i
            # z = (base_z - self.scroll_z) % num_lines
            # Prevent div by zero, z range [0.1, num_lines]
            
            z = (i + 1 - (self.scroll_z % 1)) 
            # if z < 0.1: z += num_lines # Wrap around?
            # actually (t % 1) creates smooth scroll for interval 1
            
            # Transform Z to Screen Y
            # Perspective: y = H/2 + H/2 * (1/z) ?
            # Z=1 -> Bottom. Z=inf -> Horizon.
            
            screen_y = horizon_y + (scale / z)
            
            if screen_y > h: continue
            
            # Width? Infinite.
            width_line = max(1, int(3 / z)) # Thicker near camera
            
            # Alpha fade near horizon
            # z large -> alpha low
            alpha_z = 1.0 / z
            line_c = c
            if alpha_z < 0.5:
                # dim
                lc = list(c)
                if len(lc) == 3: lc.append(255)
                dim = int(lc[3] * alpha_z * 2) 
                # wait, RGB only usually
                line_c = (int(c[0]*alpha_z*1.5), int(c[1]*alpha_z*1.5), int(c[2]*alpha_z*1.5))

            draw.line([0, screen_y, w, screen_y], fill=line_c, width=width_line)
