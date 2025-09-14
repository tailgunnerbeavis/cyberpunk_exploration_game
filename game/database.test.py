"""
Unit tests for database operations
"""

import pytest
import tempfile
import os
import json
from datetime import datetime
from game.database import DatabaseManager, DatabaseError


class TestDatabaseManager:
    """Test cases for DatabaseManager class"""
    
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
    
    def test_database_initialization(self, temp_db):
        """Test database initialization and table creation"""
        assert temp_db.connection is not None
        assert temp_db.db_file is not None
        
        # Check if tables exist
        cursor = temp_db.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cube_data'")
        assert cursor.fetchone() is not None
    
    def test_store_cube_description(self, temp_db):
        """Test storing cube descriptions"""
        # Test basic storage
        result = temp_db.store_cube_description(10, 20, 30, "Test description")
        assert result == True
        
        # Test with metadata
        metadata = {"type": "test", "value": 42}
        result = temp_db.store_cube_description(11, 21, 31, "Test with metadata", metadata)
        assert result == True
        
        # Test overwriting existing cube
        result = temp_db.store_cube_description(10, 20, 30, "Updated description")
        assert result == True
    
    def test_get_cube_description(self, temp_db):
        """Test retrieving cube descriptions"""
        # Store a cube first
        description = "Test cube description"
        metadata = {"type": "test"}
        temp_db.store_cube_description(5, 15, 25, description, metadata)
        
        # Retrieve the cube
        result = temp_db.get_cube_description(5, 15, 25)
        assert result is not None
        assert result['x'] == 5
        assert result['y'] == 15
        assert result['z'] == 25
        assert result['description'] == description
        assert result['metadata'] == metadata
        assert 'timestamp' in result
        
        # Test non-existent cube
        result = temp_db.get_cube_description(999, 999, 999)
        assert result is None
    
    def test_cube_exists(self, temp_db):
        """Test checking cube existence"""
        # Store a cube
        temp_db.store_cube_description(1, 2, 3, "Test")
        
        # Check existence
        assert temp_db.cube_exists(1, 2, 3) == True
        assert temp_db.cube_exists(999, 999, 999) == False
    
    def test_get_cubes_in_region(self, temp_db):
        """Test retrieving cubes in a 3D region"""
        # Store multiple cubes
        cubes = [
            (10, 10, 10, "Cube 1"),
            (10, 11, 10, "Cube 2"),
            (11, 10, 10, "Cube 3"),
            (20, 20, 20, "Cube 4"),  # Outside region
        ]
        
        for x, y, z, desc in cubes:
            temp_db.store_cube_description(x, y, z, desc)
        
        # Get cubes in region (10,10,10) to (11,11,11)
        results = temp_db.get_cubes_in_region(10, 10, 10, 11, 11, 11)
        assert len(results) == 3
        
        # Check that results are sorted
        coordinates = [(r['x'], r['y'], r['z']) for r in results]
        assert coordinates == [(10, 10, 10), (10, 11, 10), (11, 10, 10)]
    
    def test_get_total_cubes(self, temp_db):
        """Test getting total cube count"""
        assert temp_db.get_total_cubes() == 0
        
        # Add some cubes
        temp_db.store_cube_description(1, 1, 1, "Cube 1")
        temp_db.store_cube_description(2, 2, 2, "Cube 2")
        temp_db.store_cube_description(3, 3, 3, "Cube 3")
        
        assert temp_db.get_total_cubes() == 3
    
    def test_get_recent_cubes(self, temp_db):
        """Test getting recent cubes"""
        # Add cubes with slight delay
        temp_db.store_cube_description(1, 1, 1, "First cube")
        temp_db.store_cube_description(2, 2, 2, "Second cube")
        temp_db.store_cube_description(3, 3, 3, "Third cube")
        
        recent = temp_db.get_recent_cubes(2)
        assert len(recent) == 2
        
        # Should be ordered by timestamp (most recent first)
        assert recent[0]['description'] == "Third cube"
        assert recent[1]['description'] == "Second cube"
    
    def test_delete_cube(self, temp_db):
        """Test deleting cubes"""
        # Store a cube
        temp_db.store_cube_description(5, 5, 5, "To be deleted")
        assert temp_db.cube_exists(5, 5, 5) == True
        
        # Delete the cube
        result = temp_db.delete_cube(5, 5, 5)
        assert result == True
        assert temp_db.cube_exists(5, 5, 5) == False
        
        # Try to delete non-existent cube
        result = temp_db.delete_cube(999, 999, 999)
        assert result == False
    
    def test_clear_all_cubes(self, temp_db):
        """Test clearing all cubes"""
        # Add some cubes
        temp_db.store_cube_description(1, 1, 1, "Cube 1")
        temp_db.store_cube_description(2, 2, 2, "Cube 2")
        temp_db.store_cube_description(3, 3, 3, "Cube 3")
        
        assert temp_db.get_total_cubes() == 3
        
        # Clear all
        deleted_count = temp_db.clear_all_cubes()
        assert deleted_count == 3
        assert temp_db.get_total_cubes() == 0
    
    def test_metadata_handling(self, temp_db):
        """Test metadata JSON serialization/deserialization"""
        # Test with various metadata types
        metadata_cases = [
            {"simple": "value"},
            {"nested": {"key": "value"}},
            {"list": [1, 2, 3]},
            {"mixed": {"str": "test", "int": 42, "bool": True, "list": [1, 2]}},
            None,  # No metadata
        ]
        
        for i, metadata in enumerate(metadata_cases):
            temp_db.store_cube_description(i, i, i, f"Test {i}", metadata)
            result = temp_db.get_cube_description(i, i, i)
            assert result['metadata'] == metadata
    
    def test_context_manager(self):
        """Test database context manager"""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
            db_path = tmp.name
        
        try:
            with DatabaseManager(db_path) as db:
                db.store_cube_description(1, 1, 1, "Test")
                assert db.cube_exists(1, 1, 1) == True
            
            # Connection should be closed after context exit
            # This is hard to test directly, but we can verify the file exists
            assert os.path.exists(db_path)
        finally:
            os.unlink(db_path)
    
    def test_primary_key_constraint(self, temp_db):
        """Test that coordinates act as primary key"""
        # Store initial cube
        temp_db.store_cube_description(10, 20, 30, "Original description")
        
        # Try to store another cube with same coordinates
        temp_db.store_cube_description(10, 20, 30, "Updated description")
        
        # Should have only one cube with these coordinates
        result = temp_db.get_cube_description(10, 20, 30)
        assert result['description'] == "Updated description"
        assert temp_db.get_total_cubes() == 1
    
    def test_database_error_handling(self):
        """Test database error handling"""
        # Test with invalid database path
        with pytest.raises(DatabaseError):
            DatabaseManager("/invalid/path/that/does/not/exist/test.db")
    
    def test_coordinate_validation(self, temp_db):
        """Test that coordinates are properly handled"""
        # Test with various coordinate values
        test_coords = [
            (0, 0, 0),      # Minimum bounds
            (99, 99, 99),   # Maximum bounds (assuming 100x100x100 world)
            (50, 50, 50),   # Center
            (-1, -1, -1),   # Negative coordinates (should still work in DB)
        ]
        
        for x, y, z in test_coords:
            temp_db.store_cube_description(x, y, z, f"Test at ({x},{y},{z})")
            result = temp_db.get_cube_description(x, y, z)
            assert result is not None
            assert result['x'] == x
            assert result['y'] == y
            assert result['z'] == z
