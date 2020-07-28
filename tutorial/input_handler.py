import pygame
from tutorial.game_state import GameState

class InputHandler(object):
    def __init__(self):
        self.keys_pressed = set()
        self.keys_down = set()

    def process_events(self):
        self.keys_pressed = set()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GameState.QUIT = True

            # Process Keyboard input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    GameState.QUIT = True
                if event.key not in self.keys_down:
                    self.keys_pressed.add(event.key)
                    self.keys_down.add(event.key)
            if event.type == pygame.KEYUP:
                self.keys_down.remove(event.key)
