#!/usr/bin/env python3
"""
Cyberpunk Exploration Game
Main entry point and game loop
"""

import sys
import os
import time
from config import *
from dotenv import load_dotenv
from game.character import Character
from game.database import DatabaseManager
from game.openai_client import OpenAIClient
from game.world_generator import WorldGenerator
from game.display import DisplayManager


class CyberpunkGame:
    """Main game class that coordinates all components"""
    
    def __init__(self):
        """Initialize the game"""
        self.character = None
        self.database = None
        self.openai_client = None
        self.world_generator = None
        self.display = DisplayManager()
        self.running = False
    
    def initialize(self):
        """Initialize all game components"""
        try:
            load_dotenv()
            # Initialize character
            self.character = Character()
            
            # Initialize database
            self.database = DatabaseManager()
            
            # Initialize OpenAI client
            self.openai_client = OpenAIClient()
            
            # Initialize world generator
            self.world_generator = WorldGenerator(self.database, self.openai_client)
            
            return True
            
        except Exception as e:
            self.display.display_error_message("Initialization", f"Failed to initialize game: {e}")
            return False
    
    def run(self):
        """Main game loop"""
        if not self.initialize():
            return
        
        self.running = True
        self.display.display_header()
        
        print("Welcome to the cyberpunk world!")
        print("Navigate through a 100x100x100 cube world.")
        print("Each location will be dynamically generated with AI.")
        print()
        print("Type 'help' for controls or 'quit' to exit.")
        print()
        self.display.display_pause()
        
        # Main game loop
        while self.running:
            try:
                # Get current location description
                location_data = self.world_generator.get_location_description(self.character)
                
                # Display location
                self.display.display_location_info(location_data, self.character.position)
                
                # Get user input
                user_input = self.display.get_user_input("Enter command").lower()
                
                # Process input
                self.process_input(user_input)
                
            except KeyboardInterrupt:
                self.quit_game()
            except Exception as e:
                self.display.display_error_message("Game Error", f"Unexpected error: {e}")
                self.display.display_pause()
    
    def process_input(self, user_input: str):
        """Process user input and execute commands"""
        # Validate and sanitize input
        if not user_input or len(user_input) > 100:
            self.display.display_invalid_command(user_input)
            return
        
        # Movement commands
        if user_input in ['w', 'up']:
            self.move_character('up', self.character.move_up)
        elif user_input in ['s', 'down']:
            self.move_character('down', self.character.move_down)
        elif user_input in ['a', 'left']:
            self.move_character('left', self.character.move_left)
        elif user_input in ['d', 'right']:
            self.move_character('right', self.character.move_right)
        elif user_input in ['e', 'forward']:
            self.move_character('forward', self.character.move_forward)
        elif user_input in ['q', 'backward']:
            self.move_character('backward', self.character.move_backward)
        
        # Game commands
        elif user_input in ['help', 'h']:
            self.display.display_help()
        elif user_input in ['stats', 'statistics']:
            self.show_world_statistics()
        elif user_input in ['export']:
            self.export_world_data()
        elif user_input in ['clear']:
            self.clear_world_data()
        elif user_input in ['validate']:
            self.validate_world()
        elif user_input in ['quit', 'exit', 'q']:
            self.quit_game()
        else:
            self.display.display_invalid_command(user_input)
    
    def move_character(self, direction: str, move_func):
        """Handle character movement with feedback"""
        start_time = time.time()
        
        # Show loading indicator for movement
        self.display.display_loading_indicator(f"Moving {direction}")
        
        # Perform movement
        success = move_func()
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Display feedback
        self.display.display_movement_feedback(direction, success, self.character.position)
        
        # Show performance info if movement was slow
        if duration > 0.5:
            self.display.display_performance_info("Movement", duration)
        
        self.display.display_pause()
    
    def show_world_statistics(self):
        """Display world statistics"""
        try:
            start_time = time.time()
            self.display.display_loading_indicator("Loading statistics")
            
            stats = self.world_generator.get_world_statistics()
            duration = time.time() - start_time
            
            self.display.display_world_statistics(stats)
            
            if duration > 1.0:
                self.display.display_performance_info("Statistics query", duration)
                
        except Exception as e:
            self.display.display_error_message("Statistics", f"Failed to load statistics: {e}")
            self.display.display_pause()
    
    def export_world_data(self):
        """Export world data to file"""
        try:
            # Get export filename
            filename = f"cyberpunk_world_export_{int(time.time())}.txt"
            filepath = os.path.join(os.getcwd(), filename)
            
            start_time = time.time()
            self.display.display_loading_indicator("Exporting world data")
            
            success = self.world_generator.export_world_data(filepath)
            duration = time.time() - start_time
            
            if success:
                stats = self.world_generator.get_world_statistics()
                count = stats['total_generated_cubes']
                self.display.display_export_result(True, filepath, count)
            else:
                self.display.display_export_result(False)
            
            if duration > 2.0:
                self.display.display_performance_info("Export", duration)
            
            self.display.display_pause()
            
        except Exception as e:
            self.display.display_error_message("Export", f"Failed to export data: {e}")
            self.display.display_pause()
    
    def clear_world_data(self):
        """Clear all world data with confirmation"""
        try:
            # Show confirmation
            self.display.clear_screen()
            self.display.display_header("CLEAR WORLD DATA")
            print("⚠️  WARNING: This will permanently delete all generated world data!")
            print()
            print("This action cannot be undone.")
            print()
            
            confirm = self.display.get_user_input("Type 'DELETE' to confirm").upper()
            
            if confirm == 'DELETE':
                start_time = time.time()
                self.display.display_loading_indicator("Clearing world data")
                
                count = self.world_generator.clear_world_data()
                duration = time.time() - start_time
                
                self.display.display_clear_result(count)
                
                if duration > 1.0:
                    self.display.display_performance_info("Clear operation", duration)
            else:
                self.display.display_success_message("Operation cancelled")
            
            self.display.display_pause()
            
        except Exception as e:
            self.display.display_error_message("Clear", f"Failed to clear data: {e}")
            self.display.display_pause()
    
    def validate_world(self):
        """Validate world data integrity"""
        try:
            start_time = time.time()
            self.display.display_loading_indicator("Validating world data")
            
            validation = self.world_generator.validate_world_integrity()
            duration = time.time() - start_time
            
            self.display.display_validation_result(validation)
            
            if duration > 2.0:
                self.display.display_performance_info("Validation", duration)
                
        except Exception as e:
            self.display.display_error_message("Validation", f"Failed to validate world: {e}")
            self.display.display_pause()
    
    def quit_game(self):
        """Quit the game gracefully"""
        self.running = False
        
        # Show farewell message
        self.display.display_quit_message()
        
        # Cleanup
        if self.database:
            self.database.close()


def main():
    """Main game entry point"""
    try:
        game = CyberpunkGame()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Please check your configuration and try again.")
    finally:
        print("\nThanks for playing!")


if __name__ == "__main__":
    main()
