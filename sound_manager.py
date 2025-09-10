import pygame

class SoundManager:
    def __init__(self, success_path="sounds/success.mp3", failure_path="sounds/failure.mp3"):
        pygame.mixer.init()
        self.correct_sound = pygame.mixer.Sound(success_path)
        self.wrong_sound = pygame.mixer.Sound(failure_path)

    def play_correct(self):
        self.correct_sound.play()

    def play_wrong(self):
        self.wrong_sound.play()

