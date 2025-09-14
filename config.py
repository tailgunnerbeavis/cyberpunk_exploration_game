# Cyberpunk Exploration Game Configuration
import os

# World Configuration
WORLD_SIZE = 100  # 100x100x100 cube world
WORLD_MIN = 0
WORLD_MAX = WORLD_SIZE - 1  # 99

# Starting Position (center of the world)
STARTING_POSITION = (50, 50, 50)

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 500
OPENAI_TEMPERATURE = 0.8

# Database Configuration
DATABASE_FILE = "game_data.db"

# Display Configuration
DISPLAY_WIDTH = 80
DISPLAY_HEIGHT = 24

# Game Settings
CONTEXT_RADIUS = 1  # 3x3x3 context grid around current position
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Movement Controls
MOVEMENT_KEYS = {
    'up': ['w', 'W', 'up'],
    'down': ['s', 'S', 'down'],
    'left': ['a', 'A', 'left'],
    'right': ['d', 'D', 'right'],
    'forward': ['e', 'E'],
    'backward': ['q', 'Q'],
    'quit': ['esc', 'quit', 'exit']
}
