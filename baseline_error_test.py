import pygame
import time

# This file was originally called constant_error_test, so any references to constant error test refer
# to this file
class error_test:
    def __init__(self, screen, audio_cues, state, fps=30):
        self.screen = screen
        self.audio_cues = audio_cues

        self.width, self.height = screen.get_size()

        self.bg_color = (255, 255, 255)

        self.frame_time = 1.0/fps
        self.prev_time = time.time()

        self.state = state

        self.match = False

        '''
            "DEFAULT" - Display blank screen with a static circle

            "ERROR_TEST_BASELINE": Say "Beginning test", and wait for 2 seconds

            "ERROR_TEST_PULL": Say Pull in; wait until level reaches
            ~ desired percentage for X seconds

            "ERROR_TEST_MATCHING": Say "match", collect until match signal

            "ERROR_TEST_MATCHED": Say "relax",Save data and end
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

        #added by polina: upper and lower error bars (+/- 5%)
        upper_err_perc = 0.05
        lower_err_perc = 0.05
        upper_err_rad = static_radius * ((target_perc + upper_err_perc)/target_perc)
        lower_err_rad = static_radius * ((target_perc - lower_err_perc)/target_perc)

        pygame.draw.circle(self.screen, (192,192,192), center, int(upper_err_rad), 3)
        pygame.draw.circle(self.screen, (192,192,192), center, int(lower_err_rad), 3)
        
        target_value = max_force * target_perc

        variable_rad = (force/target_value) * static_radius
        variable_rad = max(int(variable_rad), 6)

        pygame.draw.circle(self.screen, (255, 0, 0), center, variable_rad, 6)


        

        pygame.display.update()

    def begin_automation(self):
        self.internal_mode = "ERROR_TEST_BASELINE"
        self.refrence_time = time.time()
        self.audio_cues['starting'].play()

    def process_mode(self, ref_force, ref_max_force, target_perc):
        time_0, time_1, time_2, time_3 = 2, 2, .1, 15

        current_perc = ref_force/ref_max_force

        self.state[0] = self.internal_mode

        if self.internal_mode == "DEFAULT":
            self.display_clear()

        elif self.internal_mode == "ERROR_TEST_BASELINE":
            if time.time()-self.refrence_time > time_0 and current_perc < .1:
                self.internal_mode = "ERROR_TEST_PULL"
                self.refrence_time = time.time()
                self.audio_cues['pull to line'].play()

            self.one_circle_target(ref_force, ref_max_force, target_perc)

        elif self.internal_mode == "ERROR_TEST_PULL":
            # Wait until we get to the right height and a bit of
            # time has elapsed
            if abs(current_perc - target_perc) < .05 and time.time()-self.refrence_time > time_1:
                # We're in a good zone
                # TODO: Do checking to make sure we stay here for a bit
                self.internal_mode = "ERROR_TEST_MATCHING"
                self.refrence_time = time.time()
                self.match = False

            self.one_circle_target(ref_force, ref_max_force, target_perc)

        elif self.internal_mode == "ERROR_TEST_MATCHING":
            if (self.match == True) and (abs(current_perc - target_perc) <= .05):
                self.match = False
                self.internal_mode = "ERROR_TEST_MATCHED"
                self.refrence_time = time.time()
                self.audio_cues['relax'].play()
            #if out of bounds, play "out of range" sound
            elif (self.match == True):
                self.match = False
                self.audio_cues['out of range'].play()
                

            self.one_circle_target(ref_force, ref_max_force, target_perc)

        
        elif self.internal_mode == "ERROR_TEST_MATCHED":
            if time.time() - self.refrence_time > time_2:
                self.internal_mode = "ERROR_TEST_PULL2"
                self.refrence_time = time.time()


        elif self.internal_mode == "ERROR_TEST_PULL2":
            
            if time.time() - self.refrence_time > time_3:
                self.display_clear()
                self.internal_mode = "ERROR_TEST_MATCHING2"
                self.refrence_time = time.time()
                self.audio_cues['match forces'].play()

        elif self.internal_mode == "ERROR_TEST_MATCHING2":
            if (self.match == True):
                self.match = False
                self.internal_mode = "ERROR_TEST_MATCHED2"
                self.refrence_time = time.time()
                self.audio_cues['relax'].play()

        elif self.internal_mode == "ERROR_TEST_MATCHED2":
            if time.time() - self.refrence_time > time_2:
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

        if time.time() - self.prev_time > self.frame_time:
            return self.process_mode(ref_force, ref_max_force, target_perc)

            self.prev_time = time.time()

        return "True"
