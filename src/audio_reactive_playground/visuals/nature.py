import math
import random
import colorsys
import numpy as np
from PIL import Image, ImageDraw
from .base import VisualModule

class FractalGrowth(VisualModule):
    """
    Organic recursive tree structure that grows with the music.
    
    **Concept**:
    - A 'seed' plants at the bottom (or center).
    - Branches grow recursively.
    
    **Reactivity**:
    - **Angle**: The branch split angle opens/closes on the beat (breathing).
    - **Depth**: High energy reveals deeper levels of recursion (the tree gets more detailed).
    - **Sway**: The whole tree sways slightly with low-frequency energy (wind).
    """
    def __init__(self, key=None, color=(255, 255, 255), center=(0.5, 0.8), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.sway_accum = 0
        
    def draw_branch(self, draw, x, y, length, angle, depth, max_depth, angle_split, color_intensity):
        if depth > max_depth:
            return
            
        x2 = x + length * math.cos(angle)
        y2 = y + length * math.sin(angle)
        
        # Color gradient based on depth
        c = self.color
        alpha = int(255 * (1 - (depth / max_depth) * 0.5))
        # Mix with green/nature tint? No, keep it abstract for now, use main color.
        # Just fade thickness
        width = max(1, int((max_depth - depth) * 2 * color_intensity))
        
        c_list = list(c)
        if len(c_list) == 3: 
             # Apply global opacity to RGB
             c = (int(c_list[0]*color_intensity), int(c_list[1]*color_intensity), int(c_list[2]*color_intensity))
             # If opacity < 1.0, dim it further
             if color_intensity < 1.0: # passed arg
                 pass
        
        # Actually simplest:
        r,g,b = self.color
        c = (int(r*color_intensity), int(g*color_intensity), int(b*color_intensity))
        
        draw.line([x, y, x2, y2], fill=c, width=width)
        
        # Recursive calls
        new_length = length * 0.7
        self.draw_branch(draw, x2, y2, new_length, angle - angle_split, depth + 1, max_depth, angle_split, color_intensity)
        self.draw_branch(draw, x2, y2, new_length, angle + angle_split, depth + 1, max_depth, angle_split, color_intensity)

    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        # Grow logic
        # Mapping energy to recursion depth (0 to 1 -> 4 to 9)
        # SAFETY: Cap max depth to 7 to prevent performance freeze (2^7 = 128 branches)
        # Previously could go to 9+ (512+ branches), which killed Python
        base_depth = 4
        energy_depth = int(energy * 3) 
        max_depth = min(base_depth + energy_depth, 7)
        
        # Breathing angle (standard Fractal is pi/4 or pi/6)
        base_angle = math.pi / 6
        angle_mod = base_angle + (math.sin(t) * 0.1) + (energy * 0.5)
        
        self.sway_accum += 0.01 + energy_levels.get("bass", 0) * 0.05
        sway = math.sin(self.sway_accum) * 0.1
        
        start_length = min(w, h) * 0.15
        
        # Draw the tree
        # Initial angle is -PI/2 (pointing up)
        self.draw_branch(draw, cx, cy, start_length, -math.pi/2 + sway, 0, max_depth, angle_mod, (1.0 + energy) * opacity)

class Metaballs(VisualModule):
    """
    Simulates organic, gooey fluids using moving particles and 'blob' rendering.
    
    **Implementation Note**:
    True metaballs (marching squares / isosurface) are slow in pure Python.
    This module simulates the aesthetic using overlapping soft circles that visually merge.
    
    **Reactivity**:
    - **Attraction**: Particles clump together on bass hits.
    - **Scatter**: Particles explode outward on high frequencies.
    """
    def __init__(self, key=None, color=(0, 255, 128), count=10, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.count = count
        self.balls = [] # {x, y, vx, vy, r}
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        if not self.balls:
            for _ in range(self.count):
                self.balls.append({
                    'x': cx + random.uniform(-100, 100),
                    'y': cy + random.uniform(-100, 100),
                    'vx': random.uniform(-2, 2),
                    'vy': random.uniform(-2, 2),
                    'r': random.uniform(20, 50)
                })
        
        # Update physics
        # "Gooey" force: Attract to center, but repel neighbors slightly
        for b in self.balls:
            # Center attraction (Gravity)
            dx = cx - b['x']
            dy = cy - b['y']
            dist_sq = dx*dx + dy*dy
            
            # Gentle pull to center so they don't fly away
            b['vx'] += dx * 0.001
            b['vy'] += dy * 0.001
            
            # Chaos/Heat
            b['vx'] += random.uniform(-0.5, 0.5) * energy
            b['vy'] += random.uniform(-0.5, 0.5) * energy
            
            # Move
            b['x'] += b['vx']
            b['y'] += b['vy']
            
            # Drag/Friction
            b['vx'] *= 0.95
            b['vy'] *= 0.95
            
            # Render
            # To simulate "goo", we draw multiple layers
            # Core
            r_core = b['r'] * (1 + energy * 0.5)
            c = self.color
            if opacity < 1.0:
                 c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
            draw.ellipse([b['x']-r_core, b['y']-r_core, b['x']+r_core, b['y']+r_core], fill=c)
            
            # Halo (fake glow/merge)
            # Standard PIL doesn't do additive blending easily, so we use outlines for distinct look
            draw.ellipse([b['x']-r_core*1.5, b['y']-r_core*1.5, b['x']+r_core*1.5, b['y']+r_core*1.5], outline=c, width=1)
            
        # Draw connecting "web" for logic-based merging visuals
        # If two balls are close, connect them with a thick line to simulate the "neck" of a metaball merge
        for i in range(len(self.balls)):
            for j in range(i+1, len(self.balls)):
                b1 = self.balls[i]
                b2 = self.balls[j]
                dx = b1['x'] - b2['x']
                dy = b1['y'] - b2['y']
                dist = math.hypot(dx, dy)
                
                limit = (b1['r'] + b2['r']) * 1.5
                if dist < limit:
                    # Draw a filler line
                    thickness = int(limit - dist)
                    if thickness > 0:
                        draw.line([b1['x'], b1['y'], b2['x'], b2['y']], fill=c, width=thickness)

class SpectrumHorizon(VisualModule):
    """
    A retro-wave style landscape generated from FFT spectrum data.
    
    **Visuals**:
    - Lines of varying height stretching across the screen.
    - Simulates a mountain range or cityscape.
    
    **Reactivity**:
    - **Height**: The 'mountains' are literally the audio spectrum values.
    """
    def __init__(self, key=None, color=(255, 100, 200), center=(0.5, 0.9), drift=(0.0, 0.0)):
        super().__init__(key, center, drift) # Usually sits at bottom
        self.color = color
        self.history = [] # For scrolling effect? Or just static?
        # Let's do simple real-time first
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        # We need more than just 3 float values (bass, mid, high) for a full spectrum.
        # But our AudioAnalyzer currenly pre-computes only those 3 bands for global state.
        # We can SIMULATE a detailed spectrum by interpolating the 3 values + mixing in noise.
        # Or we can create an aesthetic "fake" terrain based on the 3 bands.
        
        # Let's create a 30-point terrain
        # Points 0-10: Bass influence
        # Points 10-20: Mid influence
        # Points 20-30: High influence
        
        points = []
        num_points = 40
        width_per_seg = w / (num_points - 1)
        
        bass = energy_levels.get("bass", 0)
        mid = energy_levels.get("mid", 0)
        high = energy_levels.get("high", 0)
        
        for i in range(num_points):
            x = i * width_per_seg
            
            # Determine zone height
            val = 0
            if i < num_points * 0.33:
                val = bass
            elif i < num_points * 0.66:
                val = mid
            else:
                val = high
                
            # Add Perlin-ish noise (using sin waves of different frequencies)
            noise = math.sin(i * 0.5 + t) * 0.3 + math.cos(i * 1.2 + t * 2) * 0.2
            
            # Height curve
            height_mod = val * (1 + noise * 0.5) 
            # Envelope (taper at ends)
            envelope = math.sin((i / num_points) * math.pi) 
            
            bar_height = h * 0.4 * height_mod * envelope
            
            y = cy - bar_height
            points.append((x, y))
            
        # Draw the ridgeline
        if len(points) > 1:
            # We want to fill below the line
            poly_points = points + [(w, h), (0, h)]
            
            # Fill with low opacity
            # draw.polygon(poly_points, fill=tuple(c//4 for c in self.color))
            
            # Draw Outline
            c = self.color
            if opacity < 1.0:
                 c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
            draw.line(points, fill=c, width=3)
            
            # Draw vertical lines for "grid" look
            for px, py in points[::2]: # Every 2nd point
                draw.line([px, py, px, h], fill=c, width=1)

class DifferentialLine(VisualModule):
    """
    Simulates organic growth (like lichen or brain coral) using a "Differential Line" algorithm.
    
    **Algorithm**:
    - Starts as a small circle of nodes.
    - **Forces**:
        1. Attraction: Nodes pull towards neighbors (elasticity).
        2. Repulsion: Nodes push away from close non-neighbors (volume).
    - **Growth**: New nodes are injected when segments get too long.
    
    **Audio Reactivity**:
    - **Growth Rate**: Bass energy allows new nodes to spawn.
    - **Repulsion Force**: High energy increases the "personal space" of nodes, making the structure expand/puff up.
    """
    def __init__(self, key=None, color=(100, 255, 150), max_nodes=200, center=(0.5, 0.5), drift=(0.0, 0.0)):
        super().__init__(key, center, drift)
        self.color = color
        self.max_nodes = max_nodes
        self.nodes = [] # List of [x, y]
        self.initialized = False
        
        # Physics params
        self.r_interaction = 15 # Radius of repulsion
        self.force_repulsion = 0.5
        self.force_attraction = 0.5
        self.desired_dist = 5 # Target distance between nodes
        
    def init_nodes(self, cx, cy):
        # Start with a small polygon/circle
        r = 10
        for i in range(10):
            theta = (i / 10) * math.pi * 2
            x = cx + math.cos(theta) * r + random.uniform(-1, 1)
            y = cy + math.sin(theta) * r + random.uniform(-1, 1)
            self.nodes.append([x, y])
        self.initialized = True
        
    def draw(self, draw, w, h, t, energy_levels, opacity=1.0):
        energy = energy_levels.get(self.key, 0)
        cx, cy = self.get_coords(w, h)
        
        if not self.initialized:
            self.init_nodes(cx, cy)
            
        # --- PHYSICS STEP ---
        # 0. Audio modulation
        # Kick expands the interaction radius (puff up)
        curr_r_interaction = self.r_interaction * (1.0 + energy * 0.5)
        
        # 1. Calculate Forces
        forces = [[0.0, 0.0] for _ in self.nodes]
        count = len(self.nodes)
        
        # Optimization: Spatial hashing is better, but N=200 is small enough for O(N^2) here (approx 40k ops)
        for i in range(count):
            p1 = self.nodes[i]
            
            # Repulsion (Logic: preserve volume/prevent overlap)
            for j in range(count):
                if i == j: continue
                p2 = self.nodes[j]
                dx = p1[0] - p2[0]
                dy = p1[1] - p2[1]
                dist_sq = dx*dx + dy*dy
                
                if dist_sq < curr_r_interaction**2 and dist_sq > 0.1:
                    dist = math.sqrt(dist_sq)
                    force = (curr_r_interaction - dist) / curr_r_interaction # 0 to 1
                    # Stronger repulsion
                    fx = (dx / dist) * force * self.force_repulsion
                    fy = (dy / dist) * force * self.force_repulsion
                    forces[i][0] += fx
                    forces[i][1] += fy
            
            # Attraction (Logic: stay connected to neighbors)
            # Elastic force
            for offset in [-1, 1]:
                idx_neighbor = (i + offset) % count
                n = self.nodes[idx_neighbor]
                dx = n[0] - p1[0]
                dy = n[1] - p1[1]
                dist = math.sqrt(dx*dx + dy*dy)
                
                if dist > self.desired_dist:
                    f = (dist - self.desired_dist) * self.force_attraction
                    forces[i][0] += (dx / dist) * f
                    forces[i][1] += (dy / dist) * f
                    
            # Centering force (Logic: don't drift off screen)
            dx_c = cx - p1[0]
            dy_c = cy - p1[1]
            forces[i][0] += dx_c * 0.005
            forces[i][1] += dy_c * 0.005

        # 2. Apply Forces
        for i in range(count):
            self.nodes[i][0] += forces[i][0]
            self.nodes[i][1] += forces[i][1]
            
        # 3. Growth (Split Edges)
        # Only grow if we haven't hit max nodes AND we have some energy (beat)
        if count < self.max_nodes:
            # We iterate backwards to insert safely? Actually simplest: find longest segment and split it
            # But standard algo is: Check all segments, split if too long.
            # Limit to 1 split per frame to be smooth/stable
            best_dist = 0
            split_idx = -1
            
            for i in range(count):
                idx_next = (i + 1) % count
                p1 = self.nodes[i]
                p2 = self.nodes[idx_next]
                dist = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                
                if dist > self.desired_dist * 2 and dist > best_dist:
                    best_dist = dist
                    split_idx = i
            
            # If we found a candidate and energy allows growth
            if split_idx != -1 and energy > 0.2:
                i = split_idx
                j = (i + 1) % count
                p1 = self.nodes[i]
                p2 = self.nodes[j]
                mid_x = (p1[0] + p2[0]) / 2
                mid_y = (p1[1] + p2[1]) / 2
                self.nodes.insert(j, [mid_x, mid_y])

        # --- DRAW STEP ---
        # Convert to tuples for PIL
        poly_points = [(n[0], n[1]) for n in self.nodes]
        
        # Draw smooth closed curve
        # Since PIL doesn't have spline, we just use the polygon. With many nodes it looks smooth.
        if len(poly_points) > 2:
            c = self.color
            if opacity < 1.0:
                 c = (int(c[0]*opacity), int(c[1]*opacity), int(c[2]*opacity))
            
            # Draw Outline
            draw.polygon(poly_points, outline=c, width=2)
            
            # Optional: Draw faint fill
            # fill_c = (int(c[0]*0.2), int(c[1]*0.2), int(c[2]*0.2))
            # draw.polygon(poly_points, fill=fill_c)

