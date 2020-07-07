import pygame
import time


class error_test:
    def __init__(self, screen, audio_cues, fps=30):
        self.screen = screen
        self.audio_cues = audio_cues

        self.width, self.height = screen.get_size()

        self.bg_color = (255, 255, 255)

        self.frame_time = 1.0/fps
        self.prev_time = time.time()

        '''
            "DEFAULT" - Display blank screen with a static circle

            "ERROR_TEST_0": Say "Beginning test", and wait for 2 seconds

            "ERROR_TEST_1": Say Pull in; wait until level reaches
            ~ desired percentage for X seconds

            "ERROR_TEST_2": Say "match", collect data for 6 seconds

            "ERROR_TEST_3": Say "relax",Save data and end
        '''
        self.refrence_time = time.time()
        self.internal_mode = "DEFAULT"
        self.in_zone = False

    def display_clear(self):
        # Display the default screen with a circle on it
        self.screen.fill(self.bg_color)

        center = (self.width // 2, self.height // 2)

        static_radius = self.width // 3

        pygame.draw.circle(self.screen, (1, 1, 1), center, static_radius, 12)

        pygame.display.update()

    def one_circle_target(self, force, max_force, target_perc):
        self.screen.fill(self.bg_color)

        center = (self.width // 2, self.height // 2)

        static_radius = self.width // 3

        pygame.draw.circle(self.screen, (1, 1, 1), center, static_radius, 12)

        target_value = max_force * target_perc

        variable_rad = (force/target_value) * static_radius
        variable_rad = max(int(variable_rad), 6)

        pygame.draw.circle(self.screen, (255, 0, 0), center, variable_rad, 6)

        pygame.display.update()

    def begin_automation(self):
        self.internal_mode = "ERROR_TEST_0"
        self.refrence_time = time.time()
        self.audio_cues['starting'].play()

    def process_mode(self, ref_force, ref_max_force, target_perc):
        time_0, time_1, time_2 = 2, 2, 8

        current_perc = ref_force/ref_max_force

        if self.internal_mode == "DEFAULT":
            self.display_clear()

        elif self.internal_mode == "ERROR_TEST_0":
            if time.time()-self.refrence_time > time_0 and current_perc < .1:
                self.internal_mode = "ERROR_TEST_1"
                self.refrence_time = time.time()
                self.audio_cues['pull to line'].play()

            self.one_circle_target(ref_force, ref_max_force, target_perc)

        elif self.internal_mode == "ERROR_TEST_1":
            # Wait until we get to the right height and a bit of
            # time has elapsed
            if abs(current_perc - target_perc) < .05 and time.time()-self.refrence_time > time_1:
                # We're in a good zone
                # TODO: Do checking to make sure we stay here for a bit
                self.internal_mode = "ERROR_TEST_2"
                self.refrence_time = time.time()
                self.audio_cues['match forces'].play()

            self.one_circle_target(ref_force, ref_max_force, target_perc)

        elif self.internal_mode == "ERROR_TEST_2":
            if time.time()-self.refrence_time > time_2:
                self.internal_mode = "ERROR_TEST_3"
                self.refrence_time = time.time()

            self.one_circle_target(ref_force, ref_max_force, target_perc)

        elif self.internal_mode == "ERROR_TEST_3":
            self.audio_cues['relax'].play()

            self.internal_mode = "DEFAULT"

            # TBD: Do we want to return something(s) to be saved?
            return "SAVE"

    def process_data(self, ref_force, ref_max_force, target_perc, force_2, max_force_2):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "False"

        target_perc_1 = ref_force / ref_max_force
        target_perc_2 = force_2 / max_force_2

        error = target_perc_1 - target_perc_2

        if self.internal_mode != "DEFAULT":
            print(target_perc_1, target_perc_2, error)

        if time.time() - self.prev_time > self.frame_time:
            return self.process_mode(ref_force, ref_max_force, target_perc)

            self.prev_time = time.time()

        return "True"

    def display_circles(self, f_1, max_f_1, f_2, max_f_2):
        self.screen.fill(self.bg_color)

        center = (self.width//2, self.height//2)

        h = self.height // 2

        rad_1 = max(int((f_1/max_f_1) * h), 5)
        rad_2 = max(int((f_2/max_f_2) * h), 5)

        pygame.draw.circle(self.screen, (255, 0, 0), center, rad_1, 5)

        pygame.draw.circle(self.screen, (0, 0, 255), center, rad_2, 5)

        pygame.display.update()

    def process_data_debug(self, f_1, max_f_1, f_2, max_f_2, hide=False):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "False"

        if time.time() - self.prev_time > self.frame_time:
            if hide:
                self.display_clear()
            else:
                self.display_circles(f_1, max_f_1, f_2, max_f_2)

            self.prev_time = time.time()

        return "True"
