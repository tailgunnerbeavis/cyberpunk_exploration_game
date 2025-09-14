"""
Unit tests for world generation and context management
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from game.world_generator import WorldGenerator
from game.database import DatabaseManager
from game.openai_client import OpenAIClient
from game.character import Character
from config import WORLD_MIN, WORLD_MAX, CONTEXT_RADIUS


class TestWorldGenerator:
    """Test cases for WorldGenerator class"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            db_path = tmp.name
        
        db_manager = DatabaseManager(db_path)
        yield db_manager
        
        # Cleanup
        db_manager.close()
        os.unlink(db_path)
    
    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client"""
        with patch('game.world_generator.OpenAIClient') as mock_openai:
            mock_client = Mock()
            mock_client.generate_location_description.return_value = "A cyberpunk test location"
            mock_openai.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def world_generator(self, temp_db, mock_openai_client):
        """Create WorldGenerator instance with mocked dependencies"""
        return WorldGenerator(temp_db, mock_openai_client)
    
    def test_initialization(self, temp_db, mock_openai_client):
        """Test WorldGenerator initialization"""
        generator = WorldGenerator(temp_db, mock_openai_client)
        
        assert generator.db == temp_db
        assert generator.openai == mock_openai_client
        assert generator.context_radius == CONTEXT_RADIUS
    
    def test_get_location_description_existing(self, world_generator, temp_db):
        """Test getting description for existing location"""
        # Store a cube in database
        temp_db.store_cube_description(10, 20, 30, "Existing location")
        
        character = Character((10, 20, 30))
        result = world_generator.get_location_description(character)
        
        assert result['x'] == 10
        assert result['y'] == 20
        assert result['z'] == 30
        assert result['description'] == "Existing location"
        assert result['source'] == 'database'
        assert 'timestamp' in result
    
    def test_get_location_description_new(self, world_generator, mock_openai_client):
        """Test generating description for new location"""
        character = Character((15, 25, 35))
        result = world_generator.get_location_description(character)
        
        assert result['x'] == 15
        assert result['y'] == 25
        assert result['z'] == 35
        assert result['description'] == "A cyberpunk test location"
        assert result['source'] == 'generated'
        assert result['metadata']['generated_by'] == 'openai'
        
        # Verify OpenAI was called
        mock_openai_client.generate_location_description.assert_called_once()
    
    def test_calculate_context_bounds_center(self, world_generator):
        """Test context bounds calculation at center of world"""
        min_bound, max_bound = world_generator._calculate_context_bounds(50, 1)
        assert min_bound == 49
        assert max_bound == 51
    
    def test_calculate_context_bounds_edge(self, world_generator):
        """Test context bounds calculation at world edge"""
        # Test at minimum boundary
        min_bound, max_bound = world_generator._calculate_context_bounds(0, 1)
        assert min_bound == 0
        assert max_bound == 1
        
        # Test at maximum boundary
        min_bound, max_bound = world_generator._calculate_context_bounds(99, 1)
        assert min_bound == 98
        assert max_bound == 99
    
    def test_get_context_grid_coordinates(self, world_generator):
        """Test getting context grid coordinates"""
        coordinates = world_generator.get_context_grid_coordinates(50, 50, 50)
        
        # Should have 3x3x3 = 27 coordinates
        assert len(coordinates) == 27
        
        # Check that center is included
        assert (50, 50, 50) in coordinates
        
        # Check bounds
        x_coords = [coord[0] for coord in coordinates]
        y_coords = [coord[1] for coord in coordinates]
        z_coords = [coord[2] for coord in coordinates]
        
        assert min(x_coords) == 49
        assert max(x_coords) == 51
        assert min(y_coords) == 49
        assert max(y_coords) == 51
        assert min(z_coords) == 49
        assert max(z_coords) == 51
    
    def test_get_context_grid_coordinates_edge(self, world_generator):
        """Test context grid coordinates at world edge"""
        coordinates = world_generator.get_context_grid_coordinates(0, 0, 0)
        
        # Should have fewer coordinates due to boundary constraints
        assert len(coordinates) < 27
        
        # All coordinates should be within world bounds
        for x, y, z in coordinates:
            assert WORLD_MIN <= x <= WORLD_MAX
            assert WORLD_MIN <= y <= WORLD_MAX
            assert WORLD_MIN <= z <= WORLD_MAX
    
    def test_gather_context_cubes(self, world_generator, temp_db):
        """Test gathering context cubes"""
        # Store some cubes around the center
        temp_db.store_cube_description(49, 50, 50, "Left neighbor")
        temp_db.store_cube_description(51, 50, 50, "Right neighbor")
        temp_db.store_cube_description(50, 50, 50, "Center cube")
        
        context_cubes = world_generator._gather_context_cubes(50, 50, 50)
        
        # Should have 2 cubes (excluding center)
        assert len(context_cubes) == 2
        
        # Check that center cube is excluded
        center_cubes = [cube for cube in context_cubes if cube['x'] == 50 and cube['y'] == 50 and cube['z'] == 50]
        assert len(center_cubes) == 0
        
        # Check that neighbors are included
        descriptions = [cube['description'] for cube in context_cubes]
        assert "Left neighbor" in descriptions
        assert "Right neighbor" in descriptions
    
    def test_get_context_grid_status(self, world_generator, temp_db):
        """Test getting context grid status"""
        # Store some cubes
        temp_db.store_cube_description(49, 50, 50, "Test cube 1")
        temp_db.store_cube_description(51, 50, 50, "Test cube 2")
        
        status = world_generator.get_context_grid_status(50, 50, 50)
        
        assert status['center'] == (50, 50, 50)
        assert status['total_cubes'] == 27
        assert status['existing_cubes'] == 2
        assert status['missing_cubes'] == 25
        assert status['context_radius'] == CONTEXT_RADIUS
        assert 'bounds' in status
    
    def test_pregenerate_area(self, world_generator, mock_openai_client):
        """Test pre-generating area around character"""
        character = Character((50, 50, 50))
        
        with patch.object(world_generator, '_generate_new_location') as mock_generate:
            mock_generate.return_value = {
                'x': 50, 'y': 50, 'z': 50,
                'description': 'Generated location',
                'source': 'generated'
            }
            
            results = world_generator.pregenerate_area(character, radius=1)
        
        assert results['center'] == (50, 50, 50)
        assert results['radius'] == 1
        assert results['total_cubes'] == 27  # 3x3x3
        assert results['generated'] >= 0
        assert results['existing'] >= 0
        assert results['errors'] >= 0
        assert len(results['coordinates']) == 27
    
    def test_get_world_statistics(self, world_generator, temp_db):
        """Test getting world statistics"""
        # Add some cubes
        temp_db.store_cube_description(1, 1, 1, "Test cube 1")
        temp_db.store_cube_description(2, 2, 2, "Test cube 2")
        
        stats = world_generator.get_world_statistics()
        
        assert stats['total_generated_cubes'] == 2
        assert stats['total_possible_cubes'] == 1000000  # 100^3
        assert stats['coverage_percentage'] == 0.0  # Very small percentage
        assert len(stats['recent_cubes']) == 2
        assert stats['world_bounds']['min'] == WORLD_MIN
        assert stats['world_bounds']['max'] == WORLD_MAX
        assert stats['world_bounds']['size'] == 100
    
    def test_clear_world_data(self, world_generator, temp_db):
        """Test clearing world data"""
        # Add some cubes
        temp_db.store_cube_description(1, 1, 1, "Test cube 1")
        temp_db.store_cube_description(2, 2, 2, "Test cube 2")
        
        assert temp_db.get_total_cubes() == 2
        
        cleared_count = world_generator.clear_world_data()
        
        assert cleared_count == 2
        assert temp_db.get_total_cubes() == 0
    
    def test_export_world_data(self, world_generator, temp_db):
        """Test exporting world data"""
        # Add some cubes
        temp_db.store_cube_description(1, 1, 1, "Test cube 1")
        temp_db.store_cube_description(2, 2, 2, "Test cube 2")
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            export_path = tmp.name
        
        try:
            result = world_generator.export_world_data(export_path)
            
            assert result == True
            
            # Check file contents
            with open(export_path, 'r') as f:
                content = f.read()
            
            assert "Cyberpunk Exploration Game" in content
            assert "Total cubes: 2" in content
            assert "(1, 1, 1): Test cube 1" in content
            assert "(2, 2, 2): Test cube 2" in content
        
        finally:
            os.unlink(export_path)
    
    def test_validate_world_integrity_valid(self, world_generator, temp_db):
        """Test world integrity validation with valid data"""
        # Add valid cubes
        temp_db.store_cube_description(50, 50, 50, "Valid cube 1")
        temp_db.store_cube_description(51, 51, 51, "Valid cube 2")
        
        validation = world_generator.validate_world_integrity()
        
        assert validation['valid'] == True
        assert len(validation['errors']) == 0
        assert validation['total_cubes_checked'] == 2
    
    def test_validate_world_integrity_invalid(self, world_generator, temp_db):
        """Test world integrity validation with invalid data"""
        # Manually insert invalid data (bypassing normal validation)
        cursor = temp_db.connection.cursor()
        cursor.execute('''
            INSERT INTO cube_data (x, y, z, description, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (150, 50, 50, "Invalid X coordinate", "2023-01-01"))
        temp_db.connection.commit()
        
        validation = world_generator.validate_world_integrity()
        
        assert validation['valid'] == False
        assert len(validation['errors']) > 0
        assert any("invalid X coordinate" in error.lower() for error in validation['errors'])
    
    def test_validate_world_integrity_empty_description(self, world_generator, temp_db):
        """Test world integrity validation with empty description"""
        # Manually insert cube with empty description
        cursor = temp_db.connection.cursor()
        cursor.execute('''
            INSERT INTO cube_data (x, y, z, description, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (50, 50, 50, "", "2023-01-01"))
        temp_db.connection.commit()
        
        validation = world_generator.validate_world_integrity()
        
        assert validation['valid'] == True  # Empty description is warning, not error
        assert len(validation['warnings']) > 0
        assert any("empty description" in warning.lower() for warning in validation['warnings'])
    
    def test_generate_new_location_integration(self, world_generator, mock_openai_client):
        """Test full integration of new location generation"""
        character = Character((25, 35, 45))
        
        result = world_generator._generate_new_location(character)
        
        assert result['x'] == 25
        assert result['y'] == 35
        assert result['z'] == 45
        assert result['description'] == "A cyberpunk test location"
        assert result['source'] == 'generated'
        assert result['metadata']['generated_by'] == 'openai'
        assert result['metadata']['character_position'] == (25, 35, 45)
        
        # Verify it was stored in database
        stored_cube = world_generator.db.get_cube_description(25, 35, 45)
        assert stored_cube is not None
        assert stored_cube['description'] == "A cyberpunk test location"
    
    def test_context_radius_customization(self, temp_db, mock_openai_client):
        """Test custom context radius"""
        generator = WorldGenerator(temp_db, mock_openai_client)
        generator.context_radius = 2  # 5x5x5 grid
        
        coordinates = generator.get_context_grid_coordinates(50, 50, 50)
        
        # Should have 5x5x5 = 125 coordinates
        assert len(coordinates) == 125
        
        # Check bounds
        x_coords = [coord[0] for coord in coordinates]
        assert min(x_coords) == 48
        assert max(x_coords) == 52
