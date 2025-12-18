import math
import random
from .base import VisualModule

class TruchetTiles(VisualModule):
    """
    A dynamic tiling system using semi-circular Truchet patterns.
    
    **Visuals**:
    - A grid of square tiles.
    - Each tile contains two quarter-circle arcs connecting adjacent sides.
    - Random rotation (0, 90, 180, 270) creates complex winding paths/blobs.
    
    **Audio Reactivity**:
    - **Glitch/Flip**: On bass hits, a percentage of tiles randomly rotate 90 degrees.
    - **Color**: High energy shifts the hue or brightness.
    - **Pulse**: Line thickness expands with volume.
    """
    def __init__(self, key=None, color=(255, 255, 255), count=10, center=None, drift=None):
        super().__init__(key)
        self.color = color
        self.grid_size = max(4, count) # e.g. 10x10
        self.tiles = [] # List of rotations [0, 1, 2, 3]
        self.tile_state = [] # Flattened list
        
        # Initialize grid
        for _ in range(self.grid_size * self.grid_size):
            self.tile_state.append(random.randint(0, 3))
            
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0) # Key driver
        e_bass = energy_levels.get("bass", 0)
        
        # Calculate cell size
        # We want to fill the screen or a central box
        # Let's fill screen for clubby feel
        cell_w = w / self.grid_size
        cell_h = h / self.grid_size
        
        # Audio Logic: Flip tiles
        # On strong bass, flip many. On weak energy, flip few.
        flip_chance = 0.01 + (e_bass * 0.2) 
        
        for i in range(len(self.tile_state)):
            if random.random() < flip_chance:
                # Rotate 90 deg
                self.tile_state[i] = (self.tile_state[i] + 1) % 4
                
        # Draw
        line_width = int(3 + energy * 5)
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
        
        for i, state in enumerate(self.tile_state):
            row = i // self.grid_size
            col = i % self.grid_size
            
            x = col * cell_w
            y = row * cell_h
            
            # Draw Truchet Arcs based on state
            # State 0: Arcs at (TL, BR) corners? (Top-Left, Bottom-Right)
            # Actually standard Truchet (Smith) uses two arcs.
            # Arc 1 center: (0,0), Arc 2 center: (w, h) OR (w,0) and (0,h)
            
            # Define arc rect helper
            def draw_arc(cx, cy):
                # Bounding box for arc of radius r=cell_w/2
                r = cell_w / 2
                draw.arc([x + cx - r, y + cy - r, x + cx + r, y + cy + r], 
                         start=0, end=360, fill=c, width=line_width)
                         
            # We will just draw 90 degree arcs. 
            # Pillow arc: start angles are 0=Right, 90=Bottom, 180=Left, 270=Top (clockwise? no usually counter-clockwise in math, let's verify visual)
            # Pillow: 0 is 3 o'clock, 90 is 6 o'clock (clockwise)
            
            half_w = cell_w / 2
            half_h = cell_h / 2
            
            # Simple approach: State determines which corners have the arc center
            # State 0: Top-Left & Bottom-Right
            # State 1: Top-Right & Bottom-Left (State 0 rotated 90)
            
            # We want quarter circles.
            # To simulate rotation, we rotate the logic.
            # But truchet usually just alternates between two states "/" and "\".
            # Rotation of 90 degrees flips from "/" to "\".
            
            is_flipped = (state % 2) == 1
            
            if not is_flipped:
                # Type A: Top-Left and Bottom-Right corners
                # Arc at Top-Left (0,0) -> draws bottom-right quadrant of circle (0 to 90)
                draw.arc([x - half_w, y - half_h, x + half_w, y + half_h], 0, 90, fill=c, width=line_width)
                
                # Arc at Bottom-Right (w, h) -> draws top-left quadrant (180 to 270)
                draw.arc([x + cell_w - half_w, y + cell_h - half_h, x + cell_w + half_w, y + cell_h + half_h], 180, 270, fill=c, width=line_width)
            else:
                # Type B: Bottom-Left and Top-Right
                # Arc at Bottom-Left (0, h) -> draws top-right quadrant (270 to 360/0)
                draw.arc([x - half_w, y + cell_h - half_h, x + half_w, y + cell_h + half_h], 270, 0, fill=c, width=line_width)
                
                # Arc at Top-Right (w, 0) -> draws bottom-left quadrant (90 to 180)
                draw.arc([x + cell_w - half_w, y - half_h, x + cell_w + half_w, y + half_h], 90, 180, fill=c, width=line_width)


class SacredGeometry(VisualModule):
    """
    Rotating, concentric polygons inspired by mandalas and sacred geometry.
    
    **Visuals**:
    - Nested shapes (Triangle, Square, Hexagon, Octagon).
    - Each layer rotates at a different harmonic speed.
    - Golden ratio proportions.
    
    **Audio Reactivity**:
    - **Rotation**: Speed boosts on energy.
    - **Pulse**: Entire distinct layers scale/pump with bass.
    """
    def __init__(self, key=None, color=(255, 215, 0), center=(0.5, 0.5), drift=(0.0, 0.0), complexity=0.5):
        super().__init__(key, center, drift)
        self.color = color
        
        # Complexity defines layer density
        # Low (0.2) -> 3 layers. High (1.0) -> 8 layers.
        num_layers = int(3 + 5 * complexity)
        
        # Generate varied shapes for layers
        # e.g. 3, 4, 3, 6, 8, ...
        possible_shapes = [3, 4, 5, 6, 8, 12]
        self.layers = [random.choice(possible_shapes) for _ in range(num_layers)]
        # Sort layers? Mixed looks cooler but sorting by sides is classic. Let's keep random.
        
        self.angle_offsets = [random.uniform(0, 6.28) for _ in self.layers]
        self.rotate_speeds = [random.choice([-0.01, 0.01, -0.005, 0.005]) * (i+1) for i in range(len(self.layers))]
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        e_bass = energy_levels.get("bass", 0)
        
        cx, cy = self.get_coords(w, h)
        max_r = min(w, h) * 0.45
        
        c = self.color
        if opacity < 1.0:
             c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
             
        # Draw from outside in? Or inside out.
        # Inside out allows transparency hacks if filled (but we are outline).
        
        for i, sides in enumerate(self.layers):
            # Harmonic radius: e.g. 1/1, 1/phi, 1/phi^2... or linear steps
            # Let's do linear for visibility
            step = max_r / len(self.layers)
            r_base = (i + 1) * step
            
            # Breath
            # Bass affects outer layers more? Or all?
            breath = r_base * 0.1 * e_bass * math.sin(t * 5 + i)
            r = r_base + breath
            
            # Rotation
            # self.rotate_speeds[i] is base drift
            # Energy adds swirl
            audio_rot = energy * 0.05 * (1 if i%2==0 else -1)
            self.angle_offsets[i] += self.rotate_speeds[i] + audio_rot
            
            points = []
            angle_step = 2 * math.pi / sides
            
            current_rot = self.angle_offsets[i]
            
            for v in range(sides):
                ang = current_rot + v * angle_step
                px = cx + math.cos(ang) * r
                py = cy + math.sin(ang) * r
                points.append((px, py))
            
            # Connect vertices
            # Option: Fill with very low alpha? Or Connect all corners?
            # Standard Polygon
            draw.polygon(points, outline=c, width=max(1, int(3 * energy)))
            
            # Option: Connect to center? No, too messy.
            # Star connections (connect every 2nd vertex)
            if sides > 4 and i % 2 == 1:
                 # Draw star version
                 star_points = []
                 # Naive star: connect i to i+2
                 # Pillow polygon fills, so we need lines
                 pass 
                 # Keeping it simple polygons for cleanliness "clean geometric"
