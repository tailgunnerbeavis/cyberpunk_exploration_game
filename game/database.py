"""
Database operations for cube persistence in Cyberpunk Exploration Game
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from config import DATABASE_FILE


class DatabaseManager:
    """Manages SQLite database operations for cube data persistence"""
    
    def __init__(self, db_file: str = DATABASE_FILE):
        """
        Initialize database manager
        
        Args:
            db_file (str): Path to SQLite database file
        """
        self.db_file = db_file
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database connection and create tables if they don't exist"""
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            self._create_tables()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {e}")
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.connection.cursor()
        
        # Create cube_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cube_data (
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                z INTEGER NOT NULL,
                description TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                PRIMARY KEY (x, y, z)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cube_coordinates 
            ON cube_data (x, y, z)
        ''')
        
        # Create index for timestamp queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cube_timestamp 
            ON cube_data (timestamp)
        ''')
        
        self.connection.commit()
    
    def store_cube_description(self, x: int, y: int, z: int, description: str, 
                              metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store cube description with coordinates as primary key
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate  
            z (int): Z coordinate
            description (str): Description of the cube location
            metadata (dict, optional): Additional metadata as JSON
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            # Convert metadata to JSON string if provided
            metadata_json = json.dumps(metadata) if metadata else None
            
            # Use INSERT OR REPLACE to handle primary key conflicts
            cursor.execute('''
                INSERT OR REPLACE INTO cube_data 
                (x, y, z, description, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (x, y, z, description, datetime.now().isoformat(), metadata_json))
            
            self.connection.commit()
            return True
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to store cube description: {e}")
    
    def get_cube_description(self, x: int, y: int, z: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve existing cube description by coordinates
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            z (int): Z coordinate
            
        Returns:
            dict: Cube data with description, timestamp, and metadata, or None if not found
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT x, y, z, description, timestamp, metadata
                FROM cube_data
                WHERE x = ? AND y = ? AND z = ?
            ''', (x, y, z))
            
            row = cursor.fetchone()
            if row:
                result = {
                    'x': row['x'],
                    'y': row['y'], 
                    'z': row['z'],
                    'description': row['description'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
                return result
            return None
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to retrieve cube description: {e}")
    
    def get_cubes_in_region(self, min_x: int, min_y: int, min_z: int,
                           max_x: int, max_y: int, max_z: int) -> List[Dict[str, Any]]:
        """
        Get all cubes in a 3D region
        
        Args:
            min_x, min_y, min_z (int): Minimum coordinates
            max_x, max_y, max_z (int): Maximum coordinates
            
        Returns:
            list: List of cube data dictionaries
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT x, y, z, description, timestamp, metadata
                FROM cube_data
                WHERE x >= ? AND x <= ? 
                  AND y >= ? AND y <= ?
                  AND z >= ? AND z <= ?
                ORDER BY x, y, z
            ''', (min_x, max_x, min_y, max_y, min_z, max_z))
            
            results = []
            for row in cursor.fetchall():
                result = {
                    'x': row['x'],
                    'y': row['y'],
                    'z': row['z'], 
                    'description': row['description'],
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
                results.append(result)
            
            return results
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to retrieve cubes in region: {e}")
    
    def cube_exists(self, x: int, y: int, z: int) -> bool:
        """
        Check if a cube exists in the database
        
        Args:
            x, y, z (int): Coordinates to check
            
        Returns:
            bool: True if cube exists, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT 1 FROM cube_data
                WHERE x = ? AND y = ? AND z = ?
                LIMIT 1
            ''', (x, y, z))
            
            return cursor.fetchone() is not None
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to check cube existence: {e}")
    
    def get_total_cubes(self) -> int:
        """
        Get total number of cubes in database
        
        Returns:
            int: Total number of cubes
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('SELECT COUNT(*) FROM cube_data')
            return cursor.fetchone()[0]
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get total cubes: {e}")
    
    def get_recent_cubes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recently created cubes
        
        Args:
            limit (int): Maximum number of cubes to return
            
        Returns:
            list: List of recent cube data dictionaries
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                SELECT x, y, z, description, timestamp, metadata
                FROM cube_data
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            results = []
            for row in cursor.fetchall():
                result = {
                    'x': row['x'],
                    'y': row['y'],
                    'z': row['z'],
                    'description': row['description'], 
                    'timestamp': row['timestamp'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                }
                results.append(result)
            
            return results
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get recent cubes: {e}")
    
    def delete_cube(self, x: int, y: int, z: int) -> bool:
        """
        Delete a cube from the database
        
        Args:
            x, y, z (int): Coordinates of cube to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute('''
                DELETE FROM cube_data
                WHERE x = ? AND y = ? AND z = ?
            ''', (x, y, z))
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete cube: {e}")
    
    def clear_all_cubes(self) -> int:
        """
        Clear all cubes from database
        
        Returns:
            int: Number of cubes deleted
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute('DELETE FROM cube_data')
            self.connection.commit()
            return cursor.rowcount
            
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to clear all cubes: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close()


class DatabaseError(Exception):
    """Custom exception for database-related errors"""
    pass
