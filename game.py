import sys
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from graphics import draw_cube
from controls import handle_input

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced 3D Cube")
        self.running = True
        self.clock = pygame.time.Clock()

    def run(self):
        while self.running:
            self.running = handle_input()
            angle_x, angle_y, angle_z = handle_input()
            draw_cube(self.screen, angle_x, angle_y, angle_z)
            pygame.display.flip()
            self.clock.tick(60)
        
        self.quit()

    def quit(self):
        pygame.quit()
        sys.exit()