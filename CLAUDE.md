# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based typing/quiz game built with Pygame called "A+ Typing Game". It's designed as an educational tool where users answer questions by typing responses within time limits.

## Running the Game

```bash
python3 main.py
```

The game requires Python 3.x and pygame. Currently uses pygame 2.6.1.

## Project Structure

- `main.py` - Single-file application containing the entire game
- `questions.csv` - Primary question database (question, answer, extra_info format)
- `questions1101.csv` - Alternative question set
- `sounds/` - Audio files for correct/incorrect feedback
  - `success.mp3` - Played on correct answers
  - `failure.mp3` - Played on incorrect answers

## Game Architecture

### Core Classes

- `TypingGame` - Main game controller managing all game states and logic
- `TextInputBox` - Custom text input widget for menu settings

### Game States
- `MENU` - Main menu with game configuration
- `PLAYING` - Active gameplay 
- `PAUSED` - Game paused (F9 key)
- `GAME_OVER` - End screen with final score

### Key Features

**Question System**: 
- CSV-based question loading with 3-column format (question, answer, extra_info)
- Prevents consecutive duplicate questions
- Configurable time limits per question

**Scoring System**:
- Base 10 points per correct answer
- Streak multiplier for consecutive correct answers (3+ streak = multiplier)
- Similarity checking (80%+ similarity = half points)
- Real-time accuracy percentage tracking

**Learning Mode** (F12):
- Shows correct answers and extra info after each question
- Helpful for educational use

**Game Modes**:
- Configurable game length (default 180 seconds)
- Configurable question time limit (default 15 seconds)
- Sound toggle (F11)
- Pause/resume functionality (F9)

**Progress Tracking**:
- Wrong answers automatically saved to Documents folder as timestamped text files
- Format: `WrongAnswersYYYYMMDDHHMMSS.txt`

### Technical Details

**Dependencies**: 
- pygame (graphics, sound, input handling)
- csv (question loading)  
- difflib (answer similarity checking)
- pathlib (cross-platform file paths)

**Display**: 800x600 pixel window with 36pt font

**Sound System**: Uses pygame.mixer for audio feedback

**File I/O**: 
- UTF-8 encoding for question files
- Cross-platform Documents folder detection
- Automatic file creation for wrong answers

## Customization

**Question Files**: 
- Modify `questions.csv` or create new CSV files
- Change the default file in `load_questions()` function at main.py:34

**Game Settings**:
- Adjust `default_game_length` and `default_question_time` at main.py:24-25
- Modify similarity threshold at main.py:354 (currently 0.8 = 80%)

**Visual/Audio**:
- Replace sound files in `sounds/` directory
- Modify colors, fonts, or layout in drawing functions
- Game uses RGB color tuples throughout