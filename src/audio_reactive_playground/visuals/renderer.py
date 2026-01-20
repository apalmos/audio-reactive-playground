import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter, ImageOps
import numpy as np
from scipy.ndimage import map_coordinates, zoom

class Renderer:
    """
    The Master Scene Controller.
    
    Responsibilities:
    1.  **Orchestration**: Decides which modules are active.
    2.  **Evolution**: Periodically (every ~8s) swaps old modules for new ones (The "AI VJ").
    3.  **Post-Processing**: Applies global effects like Feedback trails, Kaleidoscope mirroring, and Glitch.
    4.  **Audio Gating**: Processes threshold logic (ignoring low volume bass).
    """
    def __init__(self, audio_analyzer, modules, fps=24, feedback=True, glitch=True, kaleidoscope=False, kick_threshold=0.6, background_video_clip=None, speed_factor=1.0):
        self.speed_factor = speed_factor
        self.background_video_clip = background_video_clip
        self.audio = audio_analyzer
        self.active_modules = modules 
        
        # Ensure we start with exactly 2 modules for the "Gallery" feel
        # If main passed more, trim soundly. If less, we'll add later.
        if len(self.active_modules) > 2:
            self.active_modules = self.active_modules[:2]
            
        # Track when each module was added to calculate fade-in
        # dictionary: module -> start_time
        # Fix: Start at -100 so initial modules don't fade in from black (User request)
        self.module_start_times = {m: -100.0 for m in self.active_modules}
        
        self.available_module_factories = [] 
        self.fps = fps
        self.feedback = feedback
        self.glitch = glitch
        self.kaleidoscope = kaleidoscope
        self.kick_threshold = kick_threshold
        self.prev_image = None
        
        # Transition State
        # Transition State
        self.last_swap_beat = 0 
        self.bars_per_scene = 8 # Default, can be overridden
        self.transition_duration = 3.0 # Slower fade for artful feel
        
        # Glitch State
        self.last_glitch_beat = 0 
        self.next_glitch_wait_bars = random.choice([8, 16]) # Glitch only every 8 or 16 bars
        
        # Contour FX State (Randomly decided at start)
        self.contour_mode = random.choice(['liquid', 'glitch', 'shatter', 'prism'])
        print(f"  > CONTOUR MODE: {self.contour_mode.upper()}") # Log it
        
        # List of tuple (module, fade_start_time)
        self.fading_out_modules = []
        
    def set_module_pool(self, factories):
        self.available_module_factories = factories

    def set_bars(self, bars):
        self.bars_per_scene = bars
        if bars < 1: self.bars_per_scene = 1
        
    def check_scene_evolution(self, t):
        # Trigger swap based on BARS (1 bar = 4 beats)
        current_beat = self.audio.get_beat_index(t)
        beats_per_swap = self.bars_per_scene * 4
        
        if (current_beat - self.last_swap_beat) >= beats_per_swap and self.available_module_factories:
            self.last_swap_beat = current_beat
            print(f"  [SceneController] Evolving visuals at {t:.1f}s (Beat {current_beat})...")
            
            # Chance to swap Contour Mode (if video is active)
            if self.background_video_clip and random.random() > 0.9:
                 self.contour_mode = random.choice(['liquid', 'glitch', 'shatter', 'prism'])
                 print(f"    > CONTOUR MODE SWITCH: {self.contour_mode.upper()}")
            
            # 1. Pick ONE module to replace
            # If we don't have enough modules, just add one.
            if len(self.active_modules) < 2:
                 # Add new
                 factory = random.choice(self.available_module_factories)
                 new_mod = factory()
                 self.active_modules.append(new_mod)
                 self.module_start_times[new_mod] = t
                 print(f"    + Added {new_mod.__class__.__name__} (Filling slot)")
            else:
                 # Replace random one
                 remove_idx = random.randint(0, len(self.active_modules)-1)
                 old_mod = self.active_modules.pop(remove_idx)
                 
                 # Move to fading out list
                 self.fading_out_modules.append((old_mod, t))
                 
                 # Add new replacement
                 factory = random.choice(self.available_module_factories)
                 new_mod = factory()
                 # Insert at same index to preserve layer order (Back/Front)
                 self.active_modules.insert(remove_idx, new_mod)
                 self.module_start_times[new_mod] = t
                 print(f"    ~ Swapped {old_mod.__class__.__name__} -> {new_mod.__class__.__name__}")

            if random.random() > 0.85:
                self.kaleidoscope = not self.kaleidoscope
                print(f"    > Kaleidoscope flipped to {self.kaleidoscope}")
                
    def make_frame(self, t):
        w, h = 1080, 1920
        
        self.check_scene_evolution(t)
        
        # 1. Base Layer (Video or Black)
        if self.background_video_clip:
            # Get video frame
            try:
                video_frame_np = self.background_video_clip.get_frame(t)
                # VideoClip get_frame returns numpy array
                video_frame_np = self.background_video_clip.get_frame(t)
                # Convert to edges ONLY (Abstract look needed)
                # 1. Resize nicely (Aspect Ratio Preserved -> Center Crop)
                raw_image = Image.fromarray(video_frame_np)
                raw_image = ImageOps.fit(raw_image, (w, h), centering=(0.5, 0.5))
                
                # 2. Convert to grayscale
                gray_frame = raw_image.convert("L")
                
                # 3. Find Edges
                edges = gray_frame.filter(ImageFilter.FIND_EDGES)
                
                # 4. Threshold to make it high contrast (Binary mask essentially)
                # This makes lines distinct and removes noise
                threshold_val = 30 
                contour_mask = edges.point(lambda p: 255 if p > threshold_val else 0)
                
                # Base image is now BLACK. We want the video to define STRUCTURE, not CONTENT.
                base_image = Image.new("RGB", (w, h), (0, 0, 0))
                
            except Exception as e:
                print(f"Error getting video frame: {e}")
                base_image = Image.new("RGB", (w, h), (0, 0, 0))
                contour_mask = None
        else:
             base_image = Image.new("RGB", (w, h), (0, 0, 0))
             contour_mask = None

        # 2. Feedback / Decay
             pass 


        # Visuals Layer (The "Effects")
        # We draw these onto a transparent layer
        visuals_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(visuals_layer)
        
        levels = self.audio.get_energy_at_time(t)
        
        raw_bass = levels.get("bass", 0)
        if raw_bass < self.kick_threshold:
            levels["bass"] = 0.0
        else:
            range_width = 1.0 - self.kick_threshold
            if range_width > 0:
                levels["bass"] = (raw_bass - self.kick_threshold) / range_width
        
        # DRAWING LOGIC: PARTIAL EVOLUTION
        
        # 1. Draw Fading Out Modules
        active_fades = []
        for mod, start_t in self.fading_out_modules:
            progress = (t - start_t) / self.transition_duration
            if progress < 1.0:
                alpha = 1.0 - progress
                mod.draw(draw, w, h, t, levels, opacity=alpha)
                active_fades.append((mod, start_t))
        self.fading_out_modules = active_fades
        
        # 2. Draw Active Modules
        for mod in self.active_modules:
            start_t = self.module_start_times.get(mod, 0)
            progress = (t - start_t) / self.transition_duration
            alpha = 1.0
            if progress < 1.0:
                alpha = progress 
            mod.draw(draw, w, h, t, levels, opacity=alpha)

        # COMPOSITE
        # COMPOSITE
        if self.background_video_clip and contour_mask:
            # ABSTRACT MODE: "Creative Contour FX"
            
            # Common Setup: Clean 5px Border (Padding handles this now, but extra safety: ensure noise is zero at edges?)
            # Actually, map_coordinates(constant=0) handles the edges perfectly.
            
            if self.contour_mode == 'prism':
                # MODE: PRISM (Chromatic Aberration)
                # Split channels and offset them based on Bass
                
                # Base offset + Bass Kick
                # SCALED BY SPEED FACTOR
                base_off = 4 * self.speed_factor
                bass_off = (levels["bass"] * 30) * self.speed_factor
                offset_val = int(base_off + bass_off)
                
                # Convert 'L' mask to RGB so we can split it
                rgb_mask = contour_mask.convert("RGB")
                r, g, b = rgb_mask.split()
                
                # Offset channels
                # Red goes Left, Blue goes Right, Green stays
                r = ImageChops.offset(r, -offset_val, 0)
                b = ImageChops.offset(b, offset_val, 0)
                
                # Recombine
                # This creates a white line with colored fringes
                contour_mask = Image.merge("RGB", (r, g, b))
                
                # For alpha, we use the max of the 3 channels to ensure visibility
                # Or just Convert to grayscale for the alpha channel
                # But we want the COLORS to show up in the "White Contours" layer.
                # So we need white_contours to be RGB, not RGBA with white fill?
                # Actually, implementation below expects 'contour_mask' to be the ALPHA.
                # If we want colored lines, we need to change how we composite.
                # FIX: We will create a colored image and use luminance as alpha.
                
                colored_lines = Image.merge("RGB", (r, g, b))
                # New Alpha = Max(r, g, b)
                # Cheap approx: Convert to grayscale
                final_alpha = colored_lines.convert("L")
                
            else:
                # DISPLACEMENT MODES (Liquid, Glitch, Shatter)
                # All use map_coordinates but with different noise textures.
                
                mask_np = np.array(contour_mask)
                h_arr, w_arr = mask_np.shape
                
                # 1. LIQUID (Default)
                grid_h, grid_w = 16, 9
                zoom_order = 1 # Linear (Smooth)
                intensity_base = 2
                intensity_bass = 20.0
                
                if self.contour_mode == 'shatter':
                    # Blocky Noise (Nearest Neighbor)
                    grid_h, grid_w = 20, 12 # Slightly finer blocks
                    zoom_order = 0 # Nearest (Blocky/Jagged)
                    intensity_base = 0
                    intensity_bass = 50.0 # Snap hard on bass
                    
                elif self.contour_mode == 'glitch':
                    # Horizontal Strips (Data Mosh)
                    # High vertical res, Low horizontal res
                    grid_h, grid_w = 60, 2 
                    zoom_order = 0 # Blocky
                    intensity_base = 5
                    # Glitch reacts to Highs/Snare too!
                    intensity_bass = 100.0 * (levels.get("accent", 0) + levels["bass"])
                
                # Generate Noise
                noise_raw_x = np.random.rand(grid_h, grid_w) - 0.5
                noise_raw_y = np.random.rand(grid_h, grid_w) - 0.5
                
                # Scale factors
                scale_y = h_arr / grid_h
                scale_x = w_arr / grid_w
                
                # Upscale
                disp_x = zoom(noise_raw_x, (scale_y, scale_x), order=zoom_order)
                disp_y = zoom(noise_raw_y, (scale_y, scale_x), order=zoom_order)
                
                # Match size
                disp_x = disp_x[:h_arr, :w_arr]
                disp_y = disp_y[:h_arr, :w_arr]
                
                
                # Calculate Intensity
                # SCALED BY SPEED FACTOR
                # Both the base wavy-ness and the bass reaction are scaled down if speed is low.
                
                final_intensity_base = intensity_base * self.speed_factor
                final_intensity_bass = intensity_bass * self.speed_factor
                
                intensity = final_intensity_base + (levels["bass"] * final_intensity_bass)
                
                shift_x = disp_x * intensity
                shift_y = disp_y * intensity
                
                # Apply Warp
                y_coords, x_coords = np.mgrid[0:h_arr, 0:w_arr]
                new_coords = np.array([y_coords - shift_y, x_coords - shift_x])
                
                # Constant=0 prevents borders!
                warped_mask_np = map_coordinates(mask_np, new_coords, order=1, mode='constant', cval=0)
                
                # Cleanup
                threshold = 50 
                # For Shatter/Glitch, we want sharp edges
                # For Liquid, we handle it same way
                warped_mask_np = np.where(warped_mask_np > threshold, 255, 0).astype(np.uint8)
                
                contour_mask = Image.fromarray(warped_mask_np, mode='L')
                
                # Prepare for Composite (Standard White)
                colored_lines = None # Will just use White

            # 3. COMPOSITE: Layering (Double Exposure)
            # Layer 1: Base Black Image (base_image)
            image = base_image.copy()
            
            # Layer 2: Visuals (The colorful atmosphere) - FULLY VISIBLE
            # We do NOT mask this anymore.
            image.paste(visuals_layer, (0, 0), visuals_layer)
            
            # Layer 3: The Video Contours (The Subject) - ON TOP
            # Layer 3: The Video Contours (The Subject) - ON TOP
            
            if colored_lines:
                # PRISM MODE: Use the colored lines we generated
                white_contours = colored_lines.convert("RGBA")
                # Alpha is strictly the luminance of the lines
                # But convert("RGBA") sets alpha to 255.
                # We need to apply the mask.
                # If Prism, contour_mask is effectively the grayscale version of the displaced channels?
                # Actually we calculated 'final_alpha' in the prism block above.
                white_contours.putalpha(final_alpha)
            else:
                 # STANDARD MODES: White Lines
                white_contours = Image.new("RGBA", (w, h), (255, 255, 255, 0))
                white_contours.putalpha(contour_mask)
            
            # Paste outlines on top of visuals
            image.paste(white_contours, (0, 0), white_contours)
            
        else:
            # Standard Mode
            # visuals_layer is transparent. We need to composite onto black (or feedback).
            if self.feedback and self.prev_image:
                 decay = Image.new("RGB", (w, h), (0, 0, 0))
                 bg_base = Image.blend(self.prev_image, decay, 0.08)
            else:
                 bg_base = Image.new("RGB", (w, h), (0, 0, 0))
            
            bg_base.paste(visuals_layer, (0, 0), visuals_layer)
            image = bg_base
            
        if self.kaleidoscope:
            quad_w, quad_h = w // 2, h // 2
            source = image.crop((0, 0, quad_w, quad_h))
            row = Image.new("RGB", (w, quad_h))
            row.paste(source, (0, 0))
            row.paste(source.transpose(Image.FLIP_LEFT_RIGHT), (quad_w, 0))
            full = Image.new("RGB", (w, h))
            full.paste(row, (0, 0))
            full.paste(row.transpose(Image.FLIP_TOP_BOTTOM), (0, quad_h))
            image = full
 
        if self.glitch:
             e_high = levels.get("high", 0)
             accent = levels.get("accent", 0)
             
             # TUNING: "Rarely" means every 8 or 16 bars (randomized).
             # And only on strong hits.
             current_beat = self.audio.get_beat_index(t)
             beats_since_glitch = current_beat - self.last_glitch_beat
             wait_beats = self.next_glitch_wait_bars * 4
             
             # TUNING: More frequent glitches (Accents)
             # Threshold lowered 0.85 -> 0.7 to catch more snares
             is_accent = accent > 0.7
             ready = beats_since_glitch >= wait_beats
             
             if is_accent and ready: 
                 self.last_glitch_beat = current_beat
                 # Reset timer to 2-4 bars (was 8-16) for "occasional" feel
                 self.next_glitch_wait_bars = random.choice([2, 4, 8])
                 
                 r, g, b = image.split()
                 
                 # Dynamic offset: Accents hit HARDER but much subtler now
                 base_offset = 12 
                     
                 offset = int((e_high + accent) * 0.5 * base_offset)
                 
                 r = ImageChops.offset(r, offset, 0)
                 b = ImageChops.offset(b, -offset, 0)
                 image = Image.merge("RGB", (r, g, b))
                 
                 # Optional: White Flash Overlay for very strong accents
                 if accent > 0.95:
                     flash = Image.new("RGB", (w, h), (255, 255, 255))
                     image = Image.blend(image, flash, 0.05)
        
             # SCREEN WOBBLE (Accent Only - User Requested)
             # Triggers on SHARP transients (Snares/Claps), independent of the rare RGB glitch
             # Threshold 0.8 ensures we don't shake on minor noise, only hits.
             if accent > 0.8:
                 # Shake amount depends on how strong the accent is
                 shake_amt = int(8 + (accent * 8)) # Range ~10-16px
                 dx = random.randint(-shake_amt, shake_amt)
                 dy = random.randint(-shake_amt, shake_amt)
                 image = ImageChops.offset(image, dx, dy)

        self.prev_image = image.copy()
        return np.array(image)
