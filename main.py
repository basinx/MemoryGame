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
pygame.display.set_caption("Memorization Game")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# sound_manager instance
sound_manager = SoundManager()

game = TypingGame(sound_manager, font, screen)
# Initialize menu focus index (0: question_file, 1: game_length, 2: question_time, 3: start, 4: clear)
game.menu_focus_index = 0

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
            # button rects for click/focus detection
            start_rect = pygame.Rect(300, 430, 200, 50)
            clear_rect = pygame.Rect(300, 490, 200, 50)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                # cycle through Question File -> Game Length -> Question Time -> Start -> Clear
                game.menu_focus_index = (getattr(game, 'menu_focus_index', 0) + 1) % 5
                # update focus states
                game.input_box_question_file.active = (game.menu_focus_index == 0)
                game.input_box_question_file.color = game.input_box_question_file.color_active if game.input_box_question_file.active else game.input_box_question_file.color_inactive
                game.input_box_game_length.active = (game.menu_focus_index == 1)
                game.input_box_game_length.color = game.input_box_game_length.color_active if game.input_box_game_length.active else game.input_box_game_length.color_inactive
                game.input_box_question_time.active = (game.menu_focus_index == 2)
                game.input_box_question_time.color = game.input_box_question_time.color_active if game.input_box_question_time.active else game.input_box_question_time.color_inactive
                # clear error state on the box that receives focus via Tab
                if game.menu_focus_index == 0:
                    game.input_box_question_file.set_error(False)
                elif game.menu_focus_index == 1:
                    game.input_box_game_length.set_error(False)
                elif game.menu_focus_index == 2:
                    game.input_box_question_time.set_error(False)
                # when focus moves to buttons (3 or 4) ensure inputs are inactive
                if game.menu_focus_index in (3, 4):
                    game.input_box_question_file.active = False
                    game.input_box_game_length.active = False
                    game.input_box_question_time.active = False
                    game.input_box_question_file.color = game.input_box_question_file.color_inactive
                    game.input_box_game_length.color = game.input_box_game_length.color_inactive
                    game.input_box_question_time.color = game.input_box_question_time.color_inactive
                continue
            # handle Enter on focused button to start/clear
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
                if getattr(game, 'menu_focus_index', 0) == 3:
                    game.game_mode = "normal"
                    game.reset_game()
                    continue
                elif getattr(game, 'menu_focus_index', 0) == 4:
                    game.game_mode = "clear"
                    game.reset_game()
                    continue
            # handle events for all three input boxes
            game.input_box_question_file.handle_event(event)
            game.input_box_game_length.handle_event(event)
            game.input_box_question_time.handle_event(event)
            # set focus index when user clicks into a control
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game.input_box_question_file.rect.collidepoint(event.pos):
                    game.menu_focus_index = 0
                elif game.input_box_game_length.rect.collidepoint(event.pos):
                    game.menu_focus_index = 1
                elif game.input_box_question_time.rect.collidepoint(event.pos):
                    game.menu_focus_index = 2
                elif start_rect.collidepoint(event.pos):
                    game.menu_focus_index = 3
                elif clear_rect.collidepoint(event.pos):
                    game.menu_focus_index = 4
        if game.state == "playing":
            game.handle_input(event)
    # Update input boxes each frame so held-backspace repeat works
    if game.state == "menu":
        game.input_box_question_file.update()
        game.input_box_game_length.update()
        game.input_box_question_time.update()
    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
