# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Application

This is a Python-based typing game built with Pygame. To run the game:

```bash
python main.py
```

## Dependencies

The application requires:
- `pygame` (for game framework and audio)
- `csv` (for loading questions)
- `random` (for question selection)
- `time` (for timing mechanics)

Install pygame if not already available:
```bash
pip install pygame
```

## Project Structure

- `main.py` - Main game application containing all game logic
- `questions.csv` - Default question bank in CSV format (question, answer, extra_info)
- `questions1101.csv` - Alternative question bank
- `sounds/` - Audio files for game feedback
  - `success.mp3` - Played on correct answers
  - `failure.mp3` - Played on incorrect answers

## Game Architecture

The game follows a state machine pattern with these states:
- `MENU` - Initial configuration screen
- `PLAYING` - Active gameplay
- `PAUSED` - Game paused (F9 key)
- `GAME_OVER` - End screen with final score

### Key Components

- `TypingGame` class manages all game state and logic
- `TextInputBox` class handles text input for settings
- Question loading system supports CSV files with 2-3 columns
- Timer system tracks both overall game time and per-question time
- Scoring system with streak multipliers for consecutive correct answers
- Sound system with toggle capability (F11)
- Learning mode shows answers and explanations (F12)

### Game Controls

- F9: Pause/Resume
- F11: Toggle sound on/off
- F12: Toggle learning mode on/off
- Enter: Submit answer
- Tab: Navigate between input fields in menu

## Question Format

CSV files should contain:
- Column 1: Question text
- Column 2: Answer text
- Column 3: Additional information (optional)

Questions are selected randomly with prevention of consecutive duplicates.

## Testing

No formal test framework is configured. Test by running the game and verifying:
- Menu navigation and settings input
- Question display and answer checking
- Timer functionality
- Sound playback
- Pause/resume mechanics
- Learning mode display