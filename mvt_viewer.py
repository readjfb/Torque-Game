import pygame
import time

class rectangle(object):
    def __init__(self, l_x, r_x, height, thickness, window_height=600):
        self.l_x = l_x

        self.r_x = r_x

        self.height = height
        self.window_height = window_height
        self.thickness = thickness

        

    def draw(self, surface, color=(255,0,0)):
        pygame.draw.polygon(surface, color, [(self.l_x, self.height),
                                                       (self.r_x, self.height),
                                                       (self.r_x, self.height + self.thickness),
                                                       (self.l_x, self.height + self.thickness)])

class mvt_viewer(object):
    def __init__(self, height, width, surface, audio_cues, scale_min=None, scale_max=None, fps=25):
        """
        :param height: Height of pygame window
        :param width: Width of pygame window
        :param surface: pygame surface to modify when called upon
        :param scale_min: minimum value of range of data values 
        :param scale_max: maximum value of range of data values 
        :param fps: approxmate frames per second
        """
        
        self.audio_cues = audio_cues

        self.height = height
        self.width = width
        self.cache = []

        self.rectangle = None

        self.prev_time = time.time()
        self.frame_time = 1.0/fps

        if scale_max:
            self.scale_max = scale_max
        else:
            self.scale_max = height

        if scale_min:
            self.scale_min = scale_min
        else:
            self.scale_min = 0

        self.running = True
        # pygame.init()
        eighth = self.width // 8
        self.rectangle = rectangle(eighth, self.width -  eighth, 20, 50, height)

        self.screen = surface

        '''To be used in mode selection
        
        CLEAR displays a white screen 

        DISPLAY_MVT just does the regular displaying indefinitely


        automation_start()
        DISPLAY_MVT_0 does regular display for certain seconds before playing sound
        
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

        self.screen.fill((255,255,255))

        pygame.display.update()
        return True

    def transform(self,value):
        """
        Internal method
        Does the range mapping to generate the actual y cordinate of the rectangle
        
        :param value: The raw datapoint to be mapped into a y coordinate
        :return: the transformed value
        """
        temp = self.height * (value / (self.scale_max-self.scale_min))
        return self.height - temp

    def mode_process(self):
        time_0, time_1 = 2, 6

        default = "DISPLAY_MVT"

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
            return self.one_step((200, 200, 200))
        
        elif self.internal_mode == "DISPLAY_MVT_0":
            if time.time() - self.refrence_time > time_0:
                self.internal_mode = "DISPLAY_MVT_1"
                self.refrence_time = time.time()
                self.audio_cues['pull hard'].play()

            return self.one_step()
        
        elif self.internal_mode == "DISPLAY_MVT_1":
            if time.time() - self.refrence_time > time_1:
                self.refrence_time = time.time()
                self.internal_mode = "DISPLAY_MVT_2"

            return self.one_step()

        elif self.internal_mode == "DISPLAY_MVT_2":
            # TODO: Logic
                # self.internal_mode = default
            self.refrence_time = time.time()
            self.internal_mode = "DISPLAY_MVT_3"
            return self.one_step()

        elif self.internal_mode == "DISPLAY_MVT_3":
            self.audio_cues['relax'].play()
            
            self.internal_mode = default
            return (f"SAVE,{self.get_max_value()}")

        else:
            return self.one_step()


    def begin_automation(self):
        """
        sets the starting refrence time for the MVT collection system
        Also sets the internal mode, and plays the "Start cue"
        
        :return: Nothing
        """
        self.refrence_time = time.time()
        self.internal_mode = "DISPLAY_MVT_0"
        self.audio_cues['starting'].play()


    def one_step(self, color=(255,0,0)):
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

        self.rectangle.draw(self.screen, color)

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
        the step that does it all! 
        Takes in a single datapoint, adds it to it's internal cache
        If its internal FPS counter indicates so, it sets the rectangle's height,
        and processes a new frame

        :param data: Single numerical datapoint to be correlated with the scale_min/ scale_max
        that results in the adjusting of the height. Will be added to internal buffer for eventual
        MVT calculation 
        """
        self.cache.append(data)
        self.running = continue_run

        if time.time() - self.prev_time > self.frame_time:
            self.rectangle.height = self.transform(data)

            self.prev_time = time.time()

            return self.mode_process()
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


