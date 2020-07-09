'''
    Calibrates the two data inputs by finding an average according to
    a specific sequence of timings.
'''
import pygame
import time


class zeroer:
    def __init__(self, screen, sound_effects, fps=10):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.sound_effects = sound_effects

        self.saved_values = []

        font = pygame.font.Font('freesansbold.ttf', 90)
        self.text = font.render('Zeroing!', True, (0, 0, 0), (255, 255, 255))

        self.text_rect = self.text.get_rect()
        self.text_rect.center = (self.width//2, self.height//2)

        self.prev_time = time.time()
        self.refrence_time = time.time()
        self.frame_time = 1.0/fps

        self.internal_mode = "ZERO"

    def begin_zeroing(self):
        # Start the zeroing process

        self.internal_mode = "ZERO_0"
        self.saved_values.clear()
        self.refrence_time = time.time()
        self.sound_effects['beginning zero'].play()

    def display_clear(self):
        # Display the default blank screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "False"

        if time.time() - self.prev_time > self.frame_time:
            self.screen.fill((255,255,255))

            pygame.display.update()

            self.prev_time = time.time()

        return "True"

    def display_screen(self):
        # Display the screen with "ZERO" on it

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "False"

        if time.time() - self.prev_time > self.frame_time:
            self.screen.fill((255, 255, 255))

            pygame.display.set_caption('Zero Sensor')

            self.screen.blit(self.text, self.text_rect)

            pygame.display.update()

            self.prev_time = time.time()

        return "True"

    def process_data(self, data):
        '''
            Takes both data points, displays the appropriate screen

            Also handles the program state
        '''

        time_0, time_1 = 2, 5

        if self.internal_mode == "ZERO":
            return self.display_clear()

        elif self.internal_mode == "ZERO_0":
            if time.time() - self.refrence_time > time_0:
                self.internal_mode = "ZERO_1"
                self.refrence_time = time.time()

            self.saved_values.append(data)
            return self.display_screen()

        elif self.internal_mode == "ZERO_1":
            if time.time() - self.refrence_time > time_1:
                self.sound_effects["end zero"].play()
                self.internal_mode = "ZERO"

                mean_l = sum([x[0] for x in self.saved_values])
                mean_r = sum([x[1] for x in self.saved_values])

                mean_l = mean_l / len(self.saved_values)
                mean_r = mean_r / len(self.saved_values)

                return(f"DATA,{mean_l},{mean_r}")
            return "True"
