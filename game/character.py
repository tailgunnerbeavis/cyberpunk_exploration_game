"""
Character movement and position tracking for Cyberpunk Exploration Game
"""

from config import STARTING_POSITION, WORLD_MIN, WORLD_MAX


class Character:
    """Character class for managing player position and movement in 3D space"""
    
    def __init__(self, position=None):
        """
        Initialize character with starting position
        
        Args:
            position (tuple): Initial position as (x, y, z). Defaults to STARTING_POSITION.
        """
        if position is None:
            position = STARTING_POSITION
        
        self.x, self.y, self.z = position
        self._validate_position()
    
    def _validate_position(self):
        """Validate that current position is within world bounds"""
        if not (WORLD_MIN <= self.x <= WORLD_MAX):
            raise ValueError(f"X coordinate {self.x} is out of bounds [{WORLD_MIN}, {WORLD_MAX}]")
        if not (WORLD_MIN <= self.y <= WORLD_MAX):
            raise ValueError(f"Y coordinate {self.y} is out of bounds [{WORLD_MIN}, {WORLD_MAX}]")
        if not (WORLD_MIN <= self.z <= WORLD_MAX):
            raise ValueError(f"Z coordinate {self.z} is out of bounds [{WORLD_MIN}, {WORLD_MAX}]")
    
    @property
    def position(self):
        """Get current position as tuple (x, y, z)"""
        return (self.x, self.y, self.z)
    
    @position.setter
    def position(self, new_position):
        """Set position and validate bounds"""
        self.x, self.y, self.z = new_position
        self._validate_position()
    
    def move_up(self):
        """Move up (increase Y coordinate)"""
        if self.y < WORLD_MAX:
            self.y += 1
            return True
        return False
    
    def move_down(self):
        """Move down (decrease Y coordinate)"""
        if self.y > WORLD_MIN:
            self.y -= 1
            return True
        return False
    
    def move_left(self):
        """Move left (decrease X coordinate)"""
        if self.x > WORLD_MIN:
            self.x -= 1
            return True
        return False
    
    def move_right(self):
        """Move right (increase X coordinate)"""
        if self.x < WORLD_MAX:
            self.x += 1
            return True
        return False
    
    def move_forward(self):
        """Move forward (increase Z coordinate)"""
        if self.z < WORLD_MAX:
            self.z += 1
            return True
        return False
    
    def move_backward(self):
        """Move backward (decrease Z coordinate)"""
        if self.z > WORLD_MIN:
            self.z -= 1
            return True
        return False
    
    def can_move_up(self):
        """Check if character can move up"""
        return self.y < WORLD_MAX
    
    def can_move_down(self):
        """Check if character can move down"""
        return self.y > WORLD_MIN
    
    def can_move_left(self):
        """Check if character can move left"""
        return self.x > WORLD_MIN
    
    def can_move_right(self):
        """Check if character can move right"""
        return self.x < WORLD_MAX
    
    def can_move_forward(self):
        """Check if character can move forward"""
        return self.z < WORLD_MAX
    
    def can_move_backward(self):
        """Check if character can move backward"""
        return self.z > WORLD_MIN
    
    def get_distance_from_center(self):
        """Calculate distance from world center (50, 50, 50)"""
        center_x, center_y, center_z = 50, 50, 50
        return ((self.x - center_x) ** 2 + (self.y - center_y) ** 2 + (self.z - center_z) ** 2) ** 0.5
    
    def get_distance_from_origin(self):
        """Calculate distance from world origin (0, 0, 0)"""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def __str__(self):
        """String representation of character position"""
        return f"Character at position ({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        """Detailed string representation"""
        return f"Character(x={self.x}, y={self.y}, z={self.z})"
