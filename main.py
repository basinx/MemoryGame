import pygame
import random
import time
import os
from datetime import datetime
from ui_helpers import draw_text, draw_wrapped_text, button, TextInputBox
from data_loader import load_questions
from utils import calculate_similarity, get_documents_folder
from sound_manager import SoundManager
from game_logic import TypingGame

# Initialize Pygame and the mixer for sound.
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("A+ Typing Game")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# sound_manager instance
sound_manager = SoundManager()

game = TypingGame(sound_manager, font, screen)

# Default game settings
default_game_length = 180  # seconds
default_question_time = 15  # seconds


# Game States
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"

# Game Modes
NORMAL_MODE = "normal"
CLEAR_MODE = "clear"

# Main loop
running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
            if game.state == "playing":
                game.pause()
            elif game.state == "paused":
                game.resume()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            game.sound_enabled = not game.sound_enabled
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
            game.learning_mode = not game.learning_mode
        game.handle_mouse_click(event)
        if game.state == "menu":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                if game.input_box_game_length.active:
                    game.input_box_game_length.active = False
                    game.input_box_game_length.color = game.input_box_game_length.color_inactive
                    game.input_box_question_time.active = True
                    game.input_box_question_time.text = ""
                    game.input_box_question_time.txt_surface = font.render(game.input_box_question_time.text, True,(0, 0, 0))
                    game.input_box_question_time.color = game.input_box_question_time.color_active
                elif game.input_box_question_time.active:
                    game.input_box_question_time.active = False
                    game.input_box_question_time.color = game.input_box_question_time.color_inactive
                    game.input_box_game_length.active = True
                    game.input_box_game_length.text = ""
                    game.input_box_game_length.txt_surface = font.render(game.input_box_game_length.text, True,(0, 0, 0))
                    game.input_box_game_length.color = game.input_box_game_length.color_active
                else:
                    game.input_box_game_length.active = True
                    game.input_box_game_length.text = ""
                    game.input_box_game_length.txt_surface = font.render(game.input_box_game_length.text, True,(0, 0, 0))
                    game.input_box_game_length.color = game.input_box_game_length.color_active
                continue
            game.input_box_game_length.handle_event(event)
            game.input_box_question_time.handle_event(event)
        if game.state == "playing":
            game.handle_input(event)
    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
