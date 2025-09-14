# Cyberpunk Exploration Game

A text-based exploration game set in a cyberpunk world where players navigate through a 100x100x100 cube world. Each location is dynamically generated using AI to create immersive cyberpunk-themed descriptions.

## Game Description

Welcome to the cyberpunk future! You are an explorer navigating through a vast 3D world where every location tells a unique story. The world is procedurally generated using AI, ensuring that no two playthroughs are exactly the same.

### Features

- **3D Navigation**: Move through a 100x100x100 cube world using 6-directional movement
- **AI-Generated Content**: Each location is dynamically created with cyberpunk-themed descriptions
- **Persistent World**: Your discoveries are saved to a database for future sessions
- **Context-Aware Generation**: AI considers surrounding areas when creating new locations
- **Interactive Exploration**: Discover hidden stories and environments as you explore

### World Structure

The game world is a 3D cube with coordinates ranging from (0,0,0) to (99,99,99):
- **X-axis**: Left/Right movement
- **Y-axis**: Up/Down movement  
- **Z-axis**: Forward/Backward movement
- **Starting Position**: (50, 50, 50) - the center of the world

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (for content generation)

### Setup Instructions

1. **Clone or download the project**
   `bash
   # If using git
   git clone <repository-url>
   cd cyberpunk_exploration_game
   
   # Or simply navigate to the project directory
   cd cyberpunk_exploration_game
   `

2. **Create a virtual environment (recommended)**
   `bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   `

3. **Install dependencies**
   `bash
   pip install -r requirements.txt
   `

4. **Configure OpenAI API**
   
   You have two options for setting up your OpenAI API key:
   
   **Option A: Environment Variable (Recommended)**
   `bash
   # On Windows
   set OPENAI_API_KEY=your_api_key_here
   
   # On macOS/Linux
   export OPENAI_API_KEY=your_api_key_here
   `
   
   **Option B: Edit config.py**
   Open config.py and replace the empty string with your API key:
   `python
   OPENAI_API_KEY = "your_api_key_here"
   `

5. **Run the game**
   `bash
   python main.py
   `

## How to Play

### Controls

- **W** or **up** - Move up (increase Y coordinate)
- **S** or **down** - Move down (decrease Y coordinate)
- **A** or **left** - Move left (decrease X coordinate)
- **D** or **right** - Move right (increase X coordinate)
- **E** or **forward** - Move forward (increase Z coordinate)
- **Q** or **backward** - Move backward (decrease Z coordinate)
- **help** - Show available commands
- **quit**, **exit**, or **q** - Exit the game

### Gameplay

1. **Start Exploring**: The game begins at position (50, 50, 50)
2. **Move Around**: Use the movement controls to navigate the 3D world
3. **Discover Locations**: Each new location will be generated with AI-created descriptions
4. **Build Your Map**: Previously visited locations are saved and can be revisited
5. **Explore Boundaries**: The world has boundaries at coordinates 0 and 99 in each dimension

### Tips

- Start by exploring in small areas to get familiar with the controls
- The AI generates context-aware descriptions based on surrounding areas
- Each location is unique and tells part of the cyberpunk world's story
- Use the help command if you forget the controls

## Project Structure

`
cyberpunk_exploration_game/
├── game/                    # Game package
│   ├── __init__.py         # Package initialization
│   ├── character.py        # Character movement and position tracking
│   ├── database.py         # SQLite database operations
│   ├── openai_client.py    # OpenAI API integration
│   ├── world_generator.py  # World generation and context management
│   └── display.py          # Text-based display and user interface
├── main.py                 # Main game entry point
├── config.py               # Configuration settings and constants
├── requirements.txt        # Python dependencies
└── README.md              # This file
`

## Configuration

The game can be customized by editing config.py:

- **World Settings**: Adjust world size and starting position
- **OpenAI Settings**: Change model, temperature, and token limits
- **Display Settings**: Modify terminal display dimensions
- **Game Settings**: Adjust context radius and retry logic
- **Controls**: Customize movement key mappings

## Development

### Running Tests

`bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest game/character.test.py
`

### Adding Features

The game is designed with a modular architecture:
- **Character System**: Handle player movement and position
- **Database Layer**: Manage persistent world data
- **AI Integration**: Generate location descriptions
- **World Generation**: Create context-aware content
- **Display System**: Handle user interface and output

## Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure you have internet connectivity

2. **Import Errors**
   - Make sure all dependencies are installed: pip install -r requirements.txt
   - Verify you're using the correct Python version (3.8+)

3. **Database Issues**
   - The game will create the database file automatically
   - If you encounter database errors, try deleting game_data.db to reset

4. **Display Issues**
   - Ensure your terminal supports the required display width (80 characters)
   - On Windows, use Windows Terminal or PowerShell for best experience

### Getting Help

If you encounter issues:
1. Check the error messages for specific details
2. Verify your setup matches the installation instructions
3. Ensure all dependencies are properly installed
4. Check that your OpenAI API key is valid and has credits

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Areas for improvement include:
- Enhanced AI prompt engineering
- Additional movement controls
- Improved display formatting
- More sophisticated world generation
- Save/load game states
- Multiplayer support

---

**Enjoy exploring the cyberpunk world!**
