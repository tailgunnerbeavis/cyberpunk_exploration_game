"""
World generation and context management for Cyberpunk Exploration Game
"""

from typing import List, Dict, Any, Optional, Tuple
from game.database import DatabaseManager
from game.openai_client import OpenAIClient
from game.character import Character
from config import WORLD_MIN, WORLD_MAX, CONTEXT_RADIUS


class WorldGenerator:
    """Manages world generation, context gathering, and location description creation"""
    
    def __init__(self, database_manager: DatabaseManager, openai_client: OpenAIClient):
        """
        Initialize world generator
        
        Args:
            database_manager (DatabaseManager): Database manager instance
            openai_client (OpenAIClient): OpenAI client instance
        """
        self.db = database_manager
        self.openai = openai_client
        self.context_radius = CONTEXT_RADIUS
    
    def get_location_description(self, character: Character) -> Dict[str, Any]:
        """
        Get or generate description for character's current location
        
        Args:
            character (Character): Character instance with current position
            
        Returns:
            dict: Location data with description, coordinates, and metadata
        """
        x, y, z = character.position
        
        # Check if location already exists in database
        existing_location = self.db.get_cube_description(x, y, z)
        if existing_location:
            return {
                'x': x,
                'y': y,
                'z': z,
                'description': existing_location['description'],
                'source': 'database',
                'timestamp': existing_location['timestamp'],
                'metadata': existing_location.get('metadata')
            }
        
        # Generate new location description
        return self._generate_new_location(character)
    
    def _generate_new_location(self, character: Character) -> Dict[str, Any]:
        """
        Generate a new location description using AI
        
        Args:
            character (Character): Character instance with current position
            
        Returns:
            dict: Generated location data
        """
        x, y, z = character.position
        
        # Gather context from surrounding area
        context_cubes = self._gather_context_cubes(x, y, z)
        
        # Generate description using OpenAI
        description = self.openai.generate_location_description(x, y, z, context_cubes)
        
        # Store in database
        metadata = {
            'generated_by': 'openai',
            'context_cubes_count': len(context_cubes),
            'character_position': character.position
        }
        
        self.db.store_cube_description(x, y, z, description, metadata)
        
        return {
            'x': x,
            'y': y,
            'z': z,
            'description': description,
            'source': 'generated',
            'timestamp': None,  # Will be set by database
            'metadata': metadata
        }
    
    def _gather_context_cubes(self, x: int, y: int, z: int) -> List[Dict[str, Any]]:
        """
        Gather cube data from surrounding area for context
        
        Args:
            x, y, z (int): Center coordinates
            
        Returns:
            list: List of surrounding cube data
        """
        # Calculate 3x3x3 grid bounds around current position
        min_x, max_x = self._calculate_context_bounds(x, self.context_radius)
        min_y, max_y = self._calculate_context_bounds(y, self.context_radius)
        min_z, max_z = self._calculate_context_bounds(z, self.context_radius)
        
        # Get cubes in the context region
        context_cubes = self.db.get_cubes_in_region(min_x, max_x, min_y, max_y, min_z, max_z)
        
        # Filter out the center cube (current position)
        filtered_cubes = [
            cube for cube in context_cubes 
            if not (cube['x'] == x and cube['y'] == y and cube['z'] == z)
        ]
        
        return filtered_cubes
    
    def _calculate_context_bounds(self, center: int, radius: int) -> Tuple[int, int]:
        """
        Calculate min/max bounds for context grid around center coordinate
        
        Args:
            center (int): Center coordinate
            radius (int): Radius around center
            
        Returns:
            tuple: (min_bound, max_bound)
        """
        min_bound = max(WORLD_MIN, center - radius)
        max_bound = min(WORLD_MAX, center + radius)
        return min_bound, max_bound
    
    def get_context_grid_coordinates(self, x: int, y: int, z: int) -> List[Tuple[int, int, int]]:
        """
        Get all coordinates in the 3x3x3 context grid around given position
        
        Args:
            x, y, z (int): Center coordinates
            
        Returns:
            list: List of (x, y, z) tuples in context grid
        """
        coordinates = []
        
        min_x, max_x = self._calculate_context_bounds(x, self.context_radius)
        min_y, max_y = self._calculate_context_bounds(y, self.context_radius)
        min_z, max_z = self._calculate_context_bounds(z, self.context_radius)
        
        for cx in range(min_x, max_x + 1):
            for cy in range(min_y, max_y + 1):
                for cz in range(min_z, max_z + 1):
                    coordinates.append((cx, cy, cz))
        
        return coordinates
    
    def get_context_grid_status(self, x: int, y: int, z: int) -> Dict[str, Any]:
        """
        Get status of all cubes in the context grid
        
        Args:
            x, y, z (int): Center coordinates
            
        Returns:
            dict: Status information about context grid
        """
        coordinates = self.get_context_grid_coordinates(x, y, z)
        
        status = {
            'center': (x, y, z),
            'total_cubes': len(coordinates),
            'existing_cubes': 0,
            'missing_cubes': 0,
            'context_radius': self.context_radius,
            'bounds': {
                'x': self._calculate_context_bounds(x, self.context_radius),
                'y': self._calculate_context_bounds(y, self.context_radius),
                'z': self._calculate_context_bounds(z, self.context_radius)
            }
        }
        
        for coord in coordinates:
            if self.db.cube_exists(*coord):
                status['existing_cubes'] += 1
            else:
                status['missing_cubes'] += 1
        
        return status
    
    def pregenerate_area(self, character: Character, radius: int = 1) -> Dict[str, Any]:
        """
        Pre-generate descriptions for an area around the character
        
        Args:
            character (Character): Character instance
            radius (int): Radius of area to pre-generate
            
        Returns:
            dict: Pre-generation results
        """
        x, y, z = character.position
        
        # Calculate area bounds
        min_x, max_x = self._calculate_context_bounds(x, radius)
        min_y, max_y = self._calculate_context_bounds(y, radius)
        min_z, max_z = self._calculate_context_bounds(z, radius)
        
        results = {
            'center': (x, y, z),
            'radius': radius,
            'total_cubes': 0,
            'generated': 0,
            'existing': 0,
            'errors': 0,
            'coordinates': []
        }
        
        # Generate descriptions for all cubes in the area
        for cx in range(min_x, max_x + 1):
            for cy in range(min_y, max_y + 1):
                for cz in range(min_z, max_z + 1):
                    results['total_cubes'] += 1
                    results['coordinates'].append((cx, cy, cz))
                    
                    # Skip if already exists
                    if self.db.cube_exists(cx, cy, cz):
                        results['existing'] += 1
                        continue
                    
                    try:
                        # Create temporary character for this position
                        temp_character = Character((cx, cy, cz))
                        
                        # Generate description
                        location_data = self._generate_new_location(temp_character)
                        results['generated'] += 1
                        
                    except Exception as e:
                        results['errors'] += 1
                        print(f"Error generating cube ({cx}, {cy}, {cz}): {e}")
        
        return results
    
    def get_world_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the generated world
        
        Returns:
            dict: World statistics
        """
        total_cubes = self.db.get_total_cubes()
        recent_cubes = self.db.get_recent_cubes(10)
        
        # Calculate world coverage percentage
        total_possible = (WORLD_MAX - WORLD_MIN + 1) ** 3
        coverage_percentage = (total_cubes / total_possible) * 100
        
        return {
            'total_generated_cubes': total_cubes,
            'total_possible_cubes': total_possible,
            'coverage_percentage': round(coverage_percentage, 2),
            'recent_cubes': recent_cubes,
            'world_bounds': {
                'min': WORLD_MIN,
                'max': WORLD_MAX,
                'size': WORLD_MAX - WORLD_MIN + 1
            }
        }
    
    def clear_world_data(self) -> int:
        """
        Clear all world data from database
        
        Returns:
            int: Number of cubes cleared
        """
        return self.db.clear_all_cubes()
    
    def export_world_data(self, filepath: str) -> bool:
        """
        Export world data to a file (for backup/debugging)
        
        Args:
            filepath (str): Path to export file
            
        Returns:
            bool: True if successful
        """
        try:
            # Get all cubes
            all_cubes = self.db.get_cubes_in_region(
                WORLD_MIN, WORLD_MAX, 
                WORLD_MIN, WORLD_MAX, 
                WORLD_MIN, WORLD_MAX
            )
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("# Cyberpunk Exploration Game - World Data Export\n")
                f.write(f"# Total cubes: {len(all_cubes)}\n")
                f.write(f"# Export timestamp: {self._get_timestamp()}\n\n")
                
                for cube in all_cubes:
                    f.write(f"({cube['x']}, {cube['y']}, {cube['z']}): {cube['description']}\n")
            
            return True
            
        except Exception as e:
            print(f"Error exporting world data: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_world_integrity(self) -> Dict[str, Any]:
        """
        Validate the integrity of the world data
        
        Returns:
            dict: Validation results
        """
        validation = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'total_cubes_checked': 0
        }
        
        # Get all cubes
        all_cubes = self.db.get_cubes_in_region(
            WORLD_MIN, WORLD_MAX,
            WORLD_MIN, WORLD_MAX,
            WORLD_MIN, WORLD_MAX
        )
        
        validation['total_cubes_checked'] = len(all_cubes)
        
        for cube in all_cubes:
            # Check coordinate bounds
            x, y, z = cube['x'], cube['y'], cube['z']
            if not (WORLD_MIN <= x <= WORLD_MAX):
                validation['errors'].append(f"Cube ({x}, {y}, {z}) has invalid X coordinate")
                validation['valid'] = False
            
            if not (WORLD_MIN <= y <= WORLD_MAX):
                validation['errors'].append(f"Cube ({x}, {y}, {z}) has invalid Y coordinate")
                validation['valid'] = False
            
            if not (WORLD_MIN <= z <= WORLD_MAX):
                validation['errors'].append(f"Cube ({x}, {y}, {z}) has invalid Z coordinate")
                validation['valid'] = False
            
            # Check description
            if not cube.get('description') or len(cube['description'].strip()) == 0:
                validation['warnings'].append(f"Cube ({x}, {y}, {z}) has empty description")
        
        return validation
