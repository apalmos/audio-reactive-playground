from abc import ABC, abstractmethod
import random
import math
from PIL import ImageDraw

class VisualModule(ABC):
    """
    Base class for all visual effects in the playground.
    
    Responsibilities:
    1.  **Identity**: Stores 'key' (bass/mid/high) which determines which audio frequency band drives this visual.
    2.  **Positioning**: Handles 'center' (x, y) coordinates and 'drift' (velocity) to allow visuals to float across the screen.
    3.  **Drawing**: Abstract `draw` method that subclasses must implement.

    Note on Coordinates:
    - Internal coordinates are normalized (0.0 to 1.0).
    - `get_coords(w, h)` converts these to pixel values.
    """
    def __init__(self, key=None, center=(0.5, 0.5), drift=(0.0, 0.0)):
        # If no key is specified, pick a random frequency band to react to.
        # This ensures variety: sometimes Tunnels pulse to Bass, sometimes to High hats.
        if key is None:
            self.key = random.choice(["bass", "mid", "high"])
        else:
            self.key = key
        self.center = list(center)
        self.drift = drift
        
    def update_center(self):
        """
        Updates the center position based on drift velocity.
        Wraps around the screen edges (toroidal topology) so shapes never disappear forever.
        """
        self.center[0] += self.drift[0]
        self.center[1] += self.drift[1]
        self.center[0] %= 1.0
        self.center[1] %= 1.0
        
    def get_coords(self, w, h):
        """Returns the current (x, y) pixel coordinates based on screen size."""
        self.update_center()
        return int(self.center[0] * w), int(self.center[1] * h)
    
    @abstractmethod
    def draw(self, draw: ImageDraw.ImageDraw, w, h, t, energy_levels):
        """
        Main draw loop called every frame.
        
        Args:
            draw: PIL ImageDraw object to draw onto.
            w, h: Width and Height of the canvas.
            t: Current timestamp in seconds.
            energy_levels: Dictionary of audio energy {'bass': 0.5, 'mid': 0.2 ...}
        """
        pass
