import pygame
import random
import csv
import time


# Initialize Pygame and the mixer for sound.
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("A+ Typing Game")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Load sound files.
# Place your MP3 files (correct.mp3 and wrong.mp3) in your working folder.
correct_sound = pygame.mixer.Sound("sounds/success.mp3")
wrong_sound = pygame.mixer.Sound("sounds/failure.mp3")

# Default game settings
default_game_length = 180  # seconds
default_question_time = 15  # seconds


# Load questions from CSV
def load_questions(filename="questions.csv"):
    questions = []
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Expecting three columns: question, answer, extra info.
            if len(row) == 3:
                questions.append((row[0], row[1], row[2]))
            elif len(row) == 2:
                questions.append((row[0], row[1], ""))
    return questions


# UI Helper Functions
def draw_text(surface, text, pos, font, color=(255, 255, 255)):
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_wrapped_text(surface, text, pos, font, color=(255, 255, 255), max_width=700):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)

    x, y = pos
    for line in lines:
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (x, y))
        y += font.get_height()


def button(rect, text):
    pygame.draw.rect(screen, (0, 128, 255), rect)
    draw_text(screen, text, (rect[0] + 10, rect[1] + 10), font)
    return rect


# Text input box class with auto-overwrite on click.
class TextInputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = (200, 200, 200)
        self.color_active = (255, 255, 255)
        self.color = self.color_inactive
        self.text = text
        self.txt_surface = font.render(text, True, (0, 0, 0))
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state if clicked inside the box.
            if self.rect.collidepoint(event.pos):
                self.active = True
                # Clear text on click so new typing overwrites previous entry.
                self.text = ""
                self.txt_surface = font.render(self.text, True, (0, 0, 0))
                self.color = self.color_active
            else:
                self.active = False
                self.color = self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, (0, 0, 0))

    def draw(self, surface):
        # Draw a background for the text box that changes shade when active.
        bg_color = (150, 150, 150) if self.active else (200, 200, 200)
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, self.color, self.rect, 2)
        surface.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))


# Game States
MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
GAME_OVER = "game_over"


# Main Game Class
class TypingGame:
    def __init__(self):
        self.state = MENU
        self.pause_start = None  # Timestamp captured on pause
        self.questions = load_questions()
        self.score = 0
        self.start_time = None
        self.question_timer = 0
        self.current_question = None
        self.user_input = ""
        self.game_length = default_game_length
        self.question_time = default_question_time
        self.time_left = self.game_length
        self.feedback = ""
        self.feedback_color = (255, 255, 255)
        self.feedback_timer = 0
        self.last_question_answer = ""  # Previous question's answer
        self.last_question_info = ""  # Previous question's extra info
        self.learning_mode = False  # Learning mode off by default
        self.sound_enabled = True  # Sound on by default
        self.correct_streak = 0  # For consecutive correct answers
        self.questions_answered = 0  # Total questions answered
        self.questions_correct = 0  # Total questions answered correctly

        # Create text input boxes for settings.
        self.input_box_game_length = TextInputBox(300, 300, 200, 40, str(default_game_length))
        self.input_box_question_time = TextInputBox(300, 370, 200, 40, str(default_question_time))

    def pause(self):
        if self.state == PLAYING:
            self.state = PAUSED
            self.pause_start = time.time()

    def resume(self):
        if self.state == PAUSED:
            delta = time.time() - self.pause_start
            # shift every running timer forward by the time we were paused
            self.start_time += delta  # overall game clock
            self.question_timer += delta  # current‑question deadline
            self.feedback_timer += delta  # feedback visibility
            self.state = PLAYING

    def reset_game(self):
        try:
            self.game_length = int(self.input_box_game_length.text)
        except ValueError:
            self.game_length = default_game_length
        try:
            self.question_time = int(self.input_box_question_time.text)
        except ValueError:
            self.question_time = default_question_time

        self.score = 0
        self.start_time = time.time()
        self.time_left = self.game_length
        self.user_input = ""
        self.feedback = ""
        self.feedback_timer = 0
        self.last_question_answer = ""
        self.last_question_info = ""
        self.correct_streak = 0  # Reset streak at game start.
        self.questions_answered = 0  # Reset question counters
        self.questions_correct = 0
        self.next_question()
        self.state = PLAYING

    def next_question(self):
        # Store the previous question's info.
        if self.current_question is not None:
            self.last_question_answer = self.current_question[1]
            self.last_question_info = self.current_question[2]
        # Prevent the same question twice in a row.
        if len(self.questions) > 1:
            new_question = random.choice(self.questions)
            while self.current_question is not None and new_question == self.current_question:
                new_question = random.choice(self.questions)
            self.current_question = new_question
        else:
            self.current_question = random.choice(self.questions)
        self.question_timer = time.time() + self.question_time
        self.user_input = ""
        self.feedback_timer = time.time() + self.question_time

    def draw_question_timer_bar(self):
        if self.state == PLAYING and self.current_question:
            total = self.question_time
            remaining = max(0, self.question_timer - time.time())
            fraction = remaining / total
            bar_width = int(710 * fraction)
            pygame.draw.rect(screen, (100, 100, 100), (40, 170, 710, 10))
            pygame.draw.rect(screen, (0, 200, 0), (40, 170, bar_width, 10))

    def draw_all_information(self):
        if self.feedback and time.time() < self.feedback_timer:
            feedback_surface = font.render(self.feedback, True, self.feedback_color)
            feedback_rect = feedback_surface.get_rect(center=(400, 350))
            screen.blit(feedback_surface, feedback_rect)
            if self.learning_mode:
                answer_text = f"Answer: {self.last_question_answer}"
                answer_surface = font.render(answer_text, True, (255, 255, 0))
                answer_rect = answer_surface.get_rect(center=(400, 390))
                screen.blit(answer_surface, answer_rect)
                if self.last_question_info.strip():
                    info_text = f"Info: {self.last_question_info}"
                    draw_wrapped_text(screen, info_text, (50, 430), font, color=(200, 200, 0), max_width=700)
        self.draw_question_timer_bar()
        draw_text(screen, f"Time Left: {self.time_left}s", (10, 10), font)
        draw_text(screen, f"Score: {self.score}", (10, 550), font)
        # Display correct percentage
        if self.questions_answered > 0:
            percentage = int((self.questions_correct / self.questions_answered) * 100)
            correct_text = f"Correct: {percentage}%"
        else:
            correct_text = "Correct: 0%"
        correct_surface = font.render(correct_text, True, (255, 255, 255))
        correct_rect = correct_surface.get_rect(center=(400, 560))
        screen.blit(correct_surface, correct_rect)

    def update(self):
        if self.state != PLAYING:
            return  # skip countdowns while paused or on menus
        if self.state == PLAYING:
            self.time_left = self.game_length - int(time.time() - self.start_time)
            if self.time_left <= 0:
                self.state = GAME_OVER
            elif time.time() > self.question_timer:
                self.questions_answered += 1
                self.feedback = "Pass"
                self.feedback_color = (255, 255, 255)
                self.correct_streak = 0  # Reset streak on pass.
                self.next_question()

    def handle_input(self, event):
        if self.state == PLAYING and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.questions_answered += 1
                if self.user_input.strip().lower() == self.current_question[1].strip().lower():
                    # Correct answer.
                    self.questions_correct += 1
                    self.correct_streak += 1
                    multiplier = 1
                    if self.correct_streak >= 3:
                        multiplier = self.correct_streak - 1
                    self.score += 10 * multiplier
                    self.feedback = f"Correct x{multiplier}"
                    self.feedback_color = (0, 255, 0)
                    if self.sound_enabled:
                        correct_sound.play()
                else:
                    self.feedback = "Incorrect"
                    self.feedback_color = (255, 0, 0)
                    self.correct_streak = 0
                    if self.sound_enabled:
                        wrong_sound.play()
                self.next_question()
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            else:
                self.user_input += event.unicode

    def draw(self):
        screen.fill((0, 0, 0))
        # Display F11 (Sound) and F12 (Learning Mode) toggles in the top-right.
        sound_text = f"F11 > Sound: {'On' if self.sound_enabled else 'Off'}"
        lm_text = f"F12 > Learning Mode: {'On' if self.learning_mode else 'Off'}"
        sound_surface = font.render(sound_text, True, (255, 255, 255))
        lm_surface = font.render(lm_text, True, (255, 255, 255))
        sound_rect = sound_surface.get_rect(topright=(790, 10))
        lm_rect = lm_surface.get_rect(topright=(790, 40))
        screen.blit(sound_surface, sound_rect)
        screen.blit(lm_surface, lm_rect)
        pause_text = "F9 > Pause/Resume"
        pause_surface = font.render(pause_text, True, (255, 255, 255))
        pause_rect = pause_surface.get_rect(topright=(790, 70))
        screen.blit(pause_surface, pause_rect)

        if self.state == MENU:
            draw_text(screen, "A+ Typing Game", (300, 100), font)
            draw_text(screen, "Game Length (s):", (300, 270), font)
            self.input_box_game_length.draw(screen)
            draw_text(screen, "Question Time (s):", (300, 340), font)
            self.input_box_question_time.draw(screen)
            start_btn = button((300, 450, 200, 50), "Start Game")
            if pygame.mouse.get_pressed()[0]:
                if pygame.Rect(start_btn).collidepoint(pygame.mouse.get_pos()):
                    self.reset_game()
        elif self.state == PLAYING:


            draw_wrapped_text(screen, f"{self.current_question[0]}", (40, 200), font)
            draw_text(screen, f"> {self.user_input}", (40, 300), font)
            #where the info text was
            self.draw_all_information()

        elif self.state == PAUSED:

            # we do not want to draw the question while paused - no cheating!
            # draw_wrapped_text(screen, f"{self.current_question[0]}", (40, 200), font)
            draw_text(screen, f"> {self.user_input}", (40, 300), font)

            # … plus any feedback/learning‑mode lines you normally show …
            self.draw_all_information()
            # Overlay (semi‑transparent dark layer)
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # RGBA – last value is alpha
            screen.blit(overlay, (0, 0))

            pause_msg = font.render("PAUSED – press F9 to resume", True, (255, 255, 0))
            rect = pause_msg.get_rect(center=(400, 300))
            screen.blit(pause_msg, rect)
        elif self.state == GAME_OVER:
            draw_text(screen, "Game Over", (335, 200), font)
            draw_text(screen, f"Final Score: {self.score}", (315, 250), font)
            restart_btn = button((300, 350, 200, 50), "Restart")
            menu_btn = button((300, 420, 200, 50), "Main Menu")
            if pygame.mouse.get_pressed()[0]:
                if pygame.Rect(restart_btn).collidepoint(pygame.mouse.get_pos()):
                    self.reset_game()
                elif pygame.Rect(menu_btn).collidepoint(pygame.mouse.get_pos()):
                    self.state = MENU


# Main loop
game = TypingGame()
running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F9:
            if game.state == PLAYING:
                game.pause()
            elif game.state == PAUSED:
                game.resume()

        # Toggle Sound with F11.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            game.sound_enabled = not game.sound_enabled

        # Toggle Learning Mode with F12.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
            game.learning_mode = not game.learning_mode

        # Handle input box events in the MENU state.
        if game.state == MENU:
            # Handle tabbing between input boxes.
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
                continue  # Skip further processing of the Tab key.

            game.input_box_game_length.handle_event(event)
            game.input_box_question_time.handle_event(event)
        # Handle gameplay input in the PLAYING state.
        if game.state == PLAYING:
            game.handle_input(event)

    game.update()
    game.draw()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
