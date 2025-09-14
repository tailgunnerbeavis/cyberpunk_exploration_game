"""
Unit tests for character movement and position tracking
"""

import pytest
from game.character import Character
from config import STARTING_POSITION, WORLD_MIN, WORLD_MAX


class TestCharacter:
    """Test cases for Character class"""
    
    def test_character_initialization_default(self):
        """Test character initialization with default position"""
        char = Character()
        assert char.position == STARTING_POSITION
        assert char.x == STARTING_POSITION[0]
        assert char.y == STARTING_POSITION[1]
        assert char.z == STARTING_POSITION[2]
    
    def test_character_initialization_custom(self):
        """Test character initialization with custom position"""
        custom_pos = (10, 20, 30)
        char = Character(custom_pos)
        assert char.position == custom_pos
        assert char.x == 10
        assert char.y == 20
        assert char.z == 30
    
    def test_character_initialization_invalid_position(self):
        """Test character initialization with invalid position"""
        with pytest.raises(ValueError):
            Character((WORLD_MAX + 1, 50, 50))
        
        with pytest.raises(ValueError):
            Character((50, WORLD_MIN - 1, 50))
        
        with pytest.raises(ValueError):
            Character((50, 50, WORLD_MAX + 1))
    
    def test_position_property(self):
        """Test position property getter and setter"""
        char = Character()
        assert char.position == STARTING_POSITION
        
        new_pos = (25, 35, 45)
        char.position = new_pos
        assert char.position == new_pos
        assert char.x == 25
        assert char.y == 35
        assert char.z == 45
    
    def test_position_setter_invalid(self):
        """Test position setter with invalid position"""
        char = Character()
        with pytest.raises(ValueError):
            char.position = (WORLD_MAX + 1, 50, 50)
    
    def test_move_up(self):
        """Test move_up method"""
        char = Character((50, 50, 50))
        assert char.move_up() == True
        assert char.position == (50, 51, 50)
        
        # Test boundary
        char = Character((50, WORLD_MAX, 50))
        assert char.move_up() == False
        assert char.position == (50, WORLD_MAX, 50)
    
    def test_move_down(self):
        """Test move_down method"""
        char = Character((50, 50, 50))
        assert char.move_down() == True
        assert char.position == (50, 49, 50)
        
        # Test boundary
        char = Character((50, WORLD_MIN, 50))
        assert char.move_down() == False
        assert char.position == (50, WORLD_MIN, 50)
    
    def test_move_left(self):
        """Test move_left method"""
        char = Character((50, 50, 50))
        assert char.move_left() == True
        assert char.position == (49, 50, 50)
        
        # Test boundary
        char = Character((WORLD_MIN, 50, 50))
        assert char.move_left() == False
        assert char.position == (WORLD_MIN, 50, 50)
    
    def test_move_right(self):
        """Test move_right method"""
        char = Character((50, 50, 50))
        assert char.move_right() == True
        assert char.position == (51, 50, 50)
        
        # Test boundary
        char = Character((WORLD_MAX, 50, 50))
        assert char.move_right() == False
        assert char.position == (WORLD_MAX, 50, 50)
    
    def test_move_forward(self):
        """Test move_forward method"""
        char = Character((50, 50, 50))
        assert char.move_forward() == True
        assert char.position == (50, 50, 51)
        
        # Test boundary
        char = Character((50, 50, WORLD_MAX))
        assert char.move_forward() == False
        assert char.position == (50, 50, WORLD_MAX)
    
    def test_move_backward(self):
        """Test move_backward method"""
        char = Character((50, 50, 50))
        assert char.move_backward() == True
        assert char.position == (50, 50, 49)
        
        # Test boundary
        char = Character((50, 50, WORLD_MIN))
        assert char.move_backward() == False
        assert char.position == (50, 50, WORLD_MIN)
    
    def test_can_move_methods(self):
        """Test can_move_* methods"""
        char = Character((50, 50, 50))
        
        # Test all directions when in middle
        assert char.can_move_up() == True
        assert char.can_move_down() == True
        assert char.can_move_left() == True
        assert char.can_move_right() == True
        assert char.can_move_forward() == True
        assert char.can_move_backward() == True
        
        # Test boundaries
        char = Character((WORLD_MIN, WORLD_MIN, WORLD_MIN))
        assert char.can_move_up() == True
        assert char.can_move_down() == False
        assert char.can_move_left() == False
        assert char.can_move_right() == True
        assert char.can_move_forward() == True
        assert char.can_move_backward() == False
        
        char = Character((WORLD_MAX, WORLD_MAX, WORLD_MAX))
        assert char.can_move_up() == False
        assert char.can_move_down() == True
        assert char.can_move_left() == True
        assert char.can_move_right() == False
        assert char.can_move_forward() == False
        assert char.can_move_backward() == True
    
    def test_get_distance_from_center(self):
        """Test distance calculation from center"""
        char = Character((50, 50, 50))  # At center
        assert char.get_distance_from_center() == 0.0
        
        char = Character((51, 50, 50))  # 1 unit away
        assert char.get_distance_from_center() == 1.0
        
        char = Character((50, 51, 50))  # 1 unit away
        assert char.get_distance_from_center() == 1.0
        
        char = Character((50, 50, 51))  # 1 unit away
        assert char.get_distance_from_center() == 1.0
    
    def test_get_distance_from_origin(self):
        """Test distance calculation from origin"""
        char = Character((0, 0, 0))  # At origin
        assert char.get_distance_from_origin() == 0.0
        
        char = Character((3, 4, 0))  # 5 units away (3-4-5 triangle)
        assert char.get_distance_from_origin() == 5.0
    
    def test_string_representations(self):
        """Test string representations"""
        char = Character((10, 20, 30))
        
        str_repr = str(char)
        assert "Character at position (10, 20, 30)" in str_repr
        
        repr_str = repr(char)
        assert "Character(x=10, y=20, z=30)" in repr_str
    
    def test_multiple_movements(self):
        """Test multiple movements in sequence"""
        char = Character((50, 50, 50))
        
        # Move in a pattern
        char.move_up()
        char.move_right()
        char.move_forward()
        assert char.position == (51, 51, 51)
        
        char.move_down()
        char.move_left()
        char.move_backward()
        assert char.position == (50, 50, 50)
    
    def test_boundary_validation(self):
        """Test boundary validation in various scenarios"""
        # Test all boundaries
        char = Character((WORLD_MIN, WORLD_MIN, WORLD_MIN))
        assert char.position == (WORLD_MIN, WORLD_MIN, WORLD_MIN)
        
        char = Character((WORLD_MAX, WORLD_MAX, WORLD_MAX))
        assert char.position == (WORLD_MAX, WORLD_MAX, WORLD_MAX)
        
        # Test edge cases
        char = Character((WORLD_MIN, WORLD_MAX, 50))
        assert char.position == (WORLD_MIN, WORLD_MAX, 50)
