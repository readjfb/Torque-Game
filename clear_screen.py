import pygame
import time


class clearer:
    def __init__(self, screen, fps=10):
        """
            Very basic pygame displayer that keeps pygame from hanging

            Runs at a low FPS to give higher priority to more important tasks
        """
        self.screen = screen

        self.prev_time = time.time()
        self.frame_time = 1.0/fps

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

        if time.time() - self.prev_time > self.frame_time:
            self.screen.fill((255, 255, 255))

            pygame.draw.polygon(self.screen, (255, 0, 0), [(0, 0), (1, 0),
                                                           (1, 1), (0, 1)])
            pygame.display.update()
            self.prev_time = time.time()
        return True
