import pygame
import time


class mvt_viewer(object):
    def __init__(self, surface, audio_cues, state, scale_min=None, scale_max=None, fps=25):
        """
        :param height: Height of pygame window
        :param width: Width of pygame window
        :param surface: pygame surface to modify when called upon
        :param scale_min: minimum value of range of data values
        :param scale_max: maximum value of range of data values
        :param fps: approxmate frames per second
        """

        self.audio_cues = audio_cues

        self.state = state

        self.width, self.height = surface.get_size()

        self.cache = []


        self.prev_time = time.time()
        self.frame_time = 1.0/fps

        if scale_max:
            self.scale_max = scale_max
        else:
            self.scale_max = self.height

        if scale_min:
            self.scale_min = scale_min
        else:
            self.scale_min = 0

        self.running = True

        eighth = self.width // 8

        self.screen = surface

        '''To be used in mode selection

        CLEAR displays a white screen

        DISPLAY_MVT just does the regular displaying indefinitely


        automation_start()
        DISPLAY_MVT_0 does regular display for certain seconds before playing
        sound

        DISPLAY_MVT_1 collects data for X seconds

        DISPLAY_MVT_2 waits until average isn't increasing anymore

        "Relax"

        Set back to DISPLAY_MVT or CLEAR
        '''
        self.refrence_time = time.time()
        self.internal_mode = "DISPLAY_MVT"

    # Just clears the screen
    def blank_screen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return ("EXIT")

        self.screen.fill((255, 255, 255))

        pygame.display.update()
        return True

    def transform(self, value):
        """
        Internal method
        Does the range mapping to generate the radius of the circle

        :param value: The raw datapoint to be mapped into a radius
        :return: the transformed value
        """
        temp = abs(self.width * (value / (self.scale_max-self.scale_min))) / 2
        temp = max(temp, 6)
        return int(temp)

    def mode_process(self, rad):
        time_0, time_1 = 2, 5

        default = "DISPLAY_MVT"

        self.state[0] = self.internal_mode

        '''To be used in mode selection

        CLEAR displays a white screen

        DISPLAY_MVT just does the regular displaying indefinitely

        automation_start()
        DISPLAY_MVT_0 does regular display for time_0 seconds before playing sound
        play sound cue

        DISPLAY_MVT_1 collects data for tine_1 seconds

        DISPLAY_MVT_2 waits until average isn't increasing anymore


        DISPLAY_MVT_3 triggers saving
        "Relax"

        Set back to DISPLAY_MVT or CLEAR
        '''
        if self.internal_mode == "CLEAR":
            return self.blank_screen

        elif self.internal_mode == "DISPLAY_MVT":
            return self.one_step(rad, (200, 200, 200))

        elif self.internal_mode == "DISPLAY_MVT_0":
            if time.time() - self.refrence_time > time_0:
                self.internal_mode = "DISPLAY_MVT_1"
                self.refrence_time = time.time()
                self.audio_cues['pull hard'].play()

            return self.one_step(rad)

        elif self.internal_mode == "DISPLAY_MVT_1":
            if time.time() - self.refrence_time > time_1:
                self.refrence_time = time.time()
                self.internal_mode = "DISPLAY_MVT_2"

            return self.one_step(rad)

        elif self.internal_mode == "DISPLAY_MVT_2":
            # TODO: Logic for waiting until stabilitzation
            self.refrence_time = time.time()
            self.internal_mode = "DISPLAY_MVT_3"
            return self.one_step(rad)

        elif self.internal_mode == "DISPLAY_MVT_3":
            self.audio_cues['relax'].play()

            self.internal_mode = default
            return (f"SAVE,{self.get_max_value()}")

        else:
            return self.one_step(rad)

    def begin_automation(self):
        """
        sets the starting refrence time for the MVT collection system
        Also sets the internal mode, and plays the "Start cue"

        :return: Nothing
        """
        self.refrence_time = time.time()
        self.internal_mode = "DISPLAY_MVT_0"
        self.audio_cues['starting'].play()

    def one_step(self, rad, color=(255, 0, 0)):
        """
        Does one drawing step for pygame
        Also handles pygame events; returns False if the pygame window should be exited

        :return: if the program should be quit/ exited
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return ("EXIT")

        self.screen.fill((255,255,255))

        center = (self.width//2, self.height//2)

        pygame.draw.circle(self.screen, color, center, rad, 6)

        pygame.display.update()
        return str(self.running)

    def run(self):
        """
        testing function

        is not used in production
        """
        while self.running:
            self.one_step()

    def process_data(self, data, continue_run=True):
        """
        the step that does it all
        Takes in a single datapoint, adds it to it's internal cache
        If its internal FPS counter indicates so, it sets the circle,
        and processes a new frame

        :param data: Single numerical datapoint to be correlated with the scale_min/ scale_max
        that results in the adjusting of the height. Will be added to internal buffer for eventual
        MVT calculation
        """
        
        # If there are adiquate data points, begin a scrolling average
        if len(self.cache) > 250:
            avg_value = sum(self.cache[-249:]) + data
            avg_value /= 250
            self.cache.append(avg_value)
        else:
            self.cache.append(data)

        self.running = continue_run

        if time.time() - self.prev_time > self.frame_time:
            self.prev_time = time.time()

            return self.mode_process(self.transform(data))
        else:
            return "True"

    def clear_cache(self):
        """
        Clears the data cache
        """
        self.cache.clear()

    def get_max_value(self):
        """
        Returns the maximum value from the internal cache.
        """
        return max(self.cache)
