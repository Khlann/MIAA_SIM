import time
import pygame
class Speaker:
    def __init__(self, model: str):
        self.model = model
        # Initialize the speaker

    def play_audio(self, audio_path: str):
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        pygame.mixer.music.stop()

