import random
import time
import os
from datetime import datetime
from ui_helpers import draw_text, draw_wrapped_text, button, TextInputBox
from data_loader import load_questions
from utils import calculate_similarity, get_documents_folder

class TypingGame:
    def __init__(self, sound_manager, font, screen, default_game_length=180, default_question_time=15):
        self.state = "menu"
        self.pause_start = None
        self.questions = load_questions()
        self.available_questions = []
        self.game_mode = "normal"
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
        self.last_question_answer = ""
        self.last_question_info = ""
        self.learning_mode = False
        self.sound_enabled = True
        self.correct_streak = 0
        self.questions_answered = 0
        self.questions_correct = 0
        self.clear_mode_correct = 0
        self.wrong_answers = []
        self.wrong_answers_file = None
        self.sound_manager = sound_manager
        self.font = font
        self.screen = screen
        self.input_box_game_length = TextInputBox(300, 300, 200, 40, str(default_game_length), font)
        self.input_box_question_time = TextInputBox(300, 370, 200, 40, str(default_question_time), font)

    def pause(self):
        if self.state == "playing":
            self.state = "paused"
            self.pause_start = time.time()

    def resume(self):
        if self.state == "paused":
            delta = time.time() - self.pause_start
            self.start_time += delta
            self.question_timer += delta
            self.feedback_timer += delta
            self.state = "playing"

    def reset_game(self):
        try:
            self.game_length = int(self.input_box_game_length.text)
        except ValueError:
            self.game_length = 180
        try:
            self.question_time = int(self.input_box_question_time.text)
        except ValueError:
            self.question_time = 15
        if self.game_mode == "clear":
            self.available_questions = self.questions.copy()
        self.score = 0
        self.start_time = time.time()
        self.time_left = self.game_length
        self.user_input = ""
        self.feedback = ""
        self.feedback_timer = 0
        self.last_question_answer = ""
        self.last_question_info = ""
        self.correct_streak = 0
        self.questions_answered = 0
        self.questions_correct = 0
        self.clear_mode_correct = 0
        self.wrong_answers = []
        self.next_question()
        self.state = "playing"

    def save_wrong_answers(self):
        if not self.wrong_answers:
            return None
        now = datetime.now()
        date_str = now.strftime('%Y%m%d')
        time_str = now.strftime('%H%M%S')
        filename = f'WrongAnswers{date_str}{time_str}.txt'
        docs_folder = get_documents_folder()
        docs_folder.mkdir(exist_ok=True)
        filepath = docs_folder / filename
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('Wrong Answers Report\n')
                f.write('=' * 50 + '\n\n')
                for i, entry in enumerate(self.wrong_answers, 1):
                    f.write(f'Question {i}:\n')
                    f.write(f'Q: {entry["question"]}\n')
                    f.write(f'Correct Answer: {entry["correct_answer"]}\n')
                    f.write(f'Your Answer: {entry["user_answer"]}\n')
                    if entry['extra_info']:
                        f.write(f'Extra Info: {entry["extra_info"]}\n')
                    f.write('\n' + '-' * 30 + '\n\n')
                f.write(f'Total Wrong Answers: {len(self.wrong_answers)}\n')
            return str(filepath)
        except Exception as e:
            print(f'Error saving wrong answers: {e}')
            return None

    def next_question(self):
        if self.current_question is not None:
            self.last_question_answer = self.current_question[1]
            self.last_question_info = self.current_question[2]
        if self.game_mode == "clear":
            if not self.available_questions:
                self.wrong_answers_file = self.save_wrong_answers()
                self.state = "game_over"
                return
            if len(self.available_questions) > 1:
                new_question = random.choice(self.available_questions)
                while self.current_question is not None and new_question == self.current_question:
                    new_question = random.choice(self.available_questions)
                self.current_question = new_question
            else:
                self.current_question = self.available_questions[0]
        else:
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
        if self.state == "playing" and self.current_question:
            total = self.question_time
            remaining = max(0, self.question_timer - time.time())
            fraction = remaining / total
            bar_width = int(710 * fraction)
            import pygame
            pygame.draw.rect(self.screen, (100, 100, 100), (40, 170, 710, 10))
            pygame.draw.rect(self.screen, (0, 200, 0), (40, 170, bar_width, 10))

    def draw_all_information(self):
        import pygame
        if self.feedback and time.time() < self.feedback_timer:
            feedback_surface = self.font.render(self.feedback, True, self.feedback_color)
            feedback_rect = feedback_surface.get_rect(center=(400, 350))
            self.screen.blit(feedback_surface, feedback_rect)
            if self.learning_mode:
                answer_text = f"Answer: {self.last_question_answer}"
                answer_surface = self.font.render(answer_text, True, (255, 255, 0))
                answer_rect = answer_surface.get_rect(center=(400, 390))
                self.screen.blit(answer_surface, answer_rect)
                if self.last_question_info.strip():
                    info_text = f"Info: {self.last_question_info}"
                    draw_wrapped_text(self.screen, info_text, (50, 430), self.font, color=(200, 200, 0), max_width=700)
        self.draw_question_timer_bar()
        draw_text(self.screen, f"Time Left: {self.time_left}s", (10, 10), self.font)
        if self.game_mode == "clear":
            remaining_text = f"Questions Remaining: {len(self.available_questions)}"
            draw_text(self.screen, remaining_text, (10, 40), self.font)
            correct_count_text = f"Correct Questions: {self.clear_mode_correct}"
            draw_text(self.screen, correct_count_text, (10, 70), self.font)
        draw_text(self.screen, f"Score: {self.score}", (10, 550), self.font)
        if self.questions_answered > 0:
            percentage = int((self.questions_correct / self.questions_answered) * 100)
            correct_text = f"Correct: {percentage}%"
        else:
            correct_text = "Correct: 0%"
        correct_surface = self.font.render(correct_text, True, (255, 255, 255))
        correct_rect = correct_surface.get_rect(center=(400, 560))
        self.screen.blit(correct_surface, correct_rect)

    def update(self):
        if self.state != "playing":
            return
        if self.state == "playing":
            self.time_left = self.game_length - int(time.time() - self.start_time)
            if self.time_left <= 0:
                self.wrong_answers_file = self.save_wrong_answers()
                self.state = "game_over"
            elif time.time() > self.question_timer:
                self.questions_answered += 1
                self.feedback = "Pass"
                self.feedback_color = (255, 255, 255)
                self.correct_streak = 0
                wrong_entry = {
                    'question': self.current_question[0],
                    'correct_answer': self.current_question[1],
                    'user_answer': '(No answer - time expired)',
                    'extra_info': self.current_question[2] if len(self.current_question) > 2 else ''
                }
                self.wrong_answers.append(wrong_entry)
                self.next_question()

    def handle_mouse_click(self, event):
        import pygame
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.state == "menu":
                start_btn = pygame.Rect(300, 430, 200, 50)
                clear_btn = pygame.Rect(300, 490, 200, 50)
                if start_btn.collidepoint(event.pos):
                    self.game_mode = "normal"
                    self.reset_game()
                elif clear_btn.collidepoint(event.pos):
                    self.game_mode = "clear"
                    self.reset_game()
            elif self.state == "game_over":
                restart_btn = pygame.Rect(300, 350, 200, 50)
                menu_btn = pygame.Rect(300, 420, 200, 50)
                if restart_btn.collidepoint(event.pos):
                    self.reset_game()
                elif menu_btn.collidepoint(event.pos):
                    self.state = "menu"

    def handle_input(self, event):
        import pygame
        if self.state == "playing" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.questions_answered += 1
                user_answer = self.user_input.strip().lower()
                correct_answer = self.current_question[1].strip().lower()
                if user_answer == correct_answer:
                    self.questions_correct += 1
                    if self.game_mode == "clear":
                        self.clear_mode_correct += 1
                        if self.current_question in self.available_questions:
                            self.available_questions.remove(self.current_question)
                    self.correct_streak += 1
                    multiplier = 1
                    if self.correct_streak >= 3:
                        multiplier = self.correct_streak - 1
                    self.score += 10 * multiplier
                    self.feedback = f"Correct x{multiplier}"
                    self.feedback_color = (0, 255, 0)
                    if self.sound_enabled:
                        self.sound_manager.play_correct()
                else:
                    similarity = calculate_similarity(user_answer, correct_answer)
                    if similarity >= 0.9:
                        self.questions_correct += 0.5
                        if self.game_mode == "clear":
                            self.clear_mode_correct += 1
                            if self.current_question in self.available_questions:
                                self.available_questions.remove(self.current_question)
                        self.correct_streak += 1
                        multiplier = 1
                        if self.correct_streak >= 3:
                            multiplier = self.correct_streak - 1
                        half_points = int((10 * multiplier) / 2)
                        self.score += half_points
                        self.feedback = f"Close! - half points! x{multiplier}"
                        self.feedback_color = (255, 225, 0)
                        if self.sound_enabled:
                            self.sound_manager.play_correct()
                    else:
                        self.feedback = "Incorrect"
                        self.feedback_color = (255, 0, 0)
                        self.correct_streak = 0
                        wrong_entry = {
                            'question': self.current_question[0],
                            'correct_answer': self.current_question[1],
                            'user_answer': self.user_input.strip(),
                            'extra_info': self.current_question[2] if len(self.current_question) > 2 else ''
                        }
                        self.wrong_answers.append(wrong_entry)
                        if self.sound_enabled:
                            self.sound_manager.play_wrong()
                self.next_question()
            elif event.key == pygame.K_BACKSPACE:
                self.user_input = self.user_input[:-1]
            else:
                self.user_input += event.unicode

    def draw(self):
        import pygame
        self.screen.fill((0, 0, 0))
        sound_text = f"F11 > Sound: {'On' if self.sound_enabled else 'Off'}"
        lm_text = f"F12 > Learning Mode: {'On' if self.learning_mode else 'Off'}"
        sound_surface = self.font.render(sound_text, True, (255, 255, 255))
        lm_surface = self.font.render(lm_text, True, (255, 255, 255))
        sound_rect = sound_surface.get_rect(topright=(790, 10))
        lm_rect = lm_surface.get_rect(topright=(790, 40))
        self.screen.blit(sound_surface, sound_rect)
        self.screen.blit(lm_surface, lm_rect)
        pause_text = "F9 > Pause/Resume"
        pause_surface = self.font.render(pause_text, True, (255, 255, 255))
        pause_rect = pause_surface.get_rect(topright=(790, 70))
        self.screen.blit(pause_surface, pause_rect)
        if self.state == "menu":
            draw_text(self.screen, "A+ Typing Game", (300, 100), self.font)
            draw_text(self.screen, "Game Length (s):", (300, 270), self.font)
            self.input_box_game_length.draw(self.screen)
            draw_text(self.screen, "Question Time (s):", (300, 340), self.font)
            self.input_box_question_time.draw(self.screen)
            button((300, 430, 200, 50), "Start Game", self.screen, self.font)
            button((300, 490, 200, 50), "Clear Mode", self.screen, self.font)
        elif self.state == "playing":
            draw_wrapped_text(self.screen, f"{self.current_question[0]}", (40, 200), self.font)
            draw_text(self.screen, f"> {self.user_input}", (40, 300), self.font)
            self.draw_all_information()
        elif self.state == "paused":
            draw_text(self.screen, f"> {self.user_input}", (40, 300), self.font)
            self.draw_all_information()
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            pause_msg = self.font.render("PAUSED – press F9 to resume", True, (255, 255, 0))
            rect = pause_msg.get_rect(center=(400, 300))
            self.screen.blit(pause_msg, rect)
        elif self.state == "game_over":
            draw_text(self.screen, "Game Over", (335, 200), self.font)
            draw_text(self.screen, f"Final Score: {self.score}", (315, 250), self.font)
            if self.game_mode == "clear":
                clear_stats_text = f"Questions Completed: {self.clear_mode_correct}"
                draw_text(self.screen, clear_stats_text, (280, 280), self.font)
            if hasattr(self, 'wrong_answers_file') and self.wrong_answers_file:
                import os
                msg = f"Questions missed written to: {os.path.basename(self.wrong_answers_file)}"
                draw_wrapped_text(self.screen, msg, (200, 130), self.font, color=(255, 255, 0), max_width=700)
            button((300, 350, 200, 50), "Restart", self.screen, self.font)
            button((300, 420, 200, 50), "Main Menu", self.screen, self.font)

