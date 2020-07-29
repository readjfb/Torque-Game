import pygame
from pygame.locals import *
from pygame.color import *

import math

import time

class bar_game:
    def __init__(self, screen, test_data, sound_cues, state, fps=30):
        self.screen = screen
        self.sound_cues = sound_cues
        self.test_data = test_data

        self.width, self.height = screen.get_size()

        self.center = (self.width // 2, self.height // 2)

        self.state = state

        self.prev_time = time.time()

        self.internal_mode = "MAIN_GAME:DEFAULT"
        self.refrence_time = time.time()

        self.frame_time = 1.0/fps

        self.locked_forces = [0.0, 0.0]

        self.square_radius = 20
        self.box_height = 30
        self.box_width = self.width*.7

        self.square_speed = 10
        self.square_x = self.width/2

    def get_bar_slope(self, l_val, r_val):
        return ((r_val - l_val) * self.height) / self.box_width

    def draw_bar(self, l_val, r_val, m_0, color=(2, 2, 2)):
        if m_0 != 0:
            m_1 = -1.0/m_0
        else:
            m_1 = 9999999

        theta = math.atan(m_0)

        left_x, right_x = -math.cos(theta) * (self.box_width/2), math.cos(theta) * (self.box_width/2)

        left_x += self.width/2
        right_x += self.width/2

        left_y, right_y = m_0*left_x, m_0*right_x

        theta_2 = math.atan(m_1)

        x_dif, y_dif = (self.box_height/2) * math.cos(theta_2), (self.box_height/2) * math.sin(theta_2)

        rect_pts = [(left_x + x_dif, left_y + y_dif), (right_x + x_dif, right_y + y_dif),
                    (right_x - x_dif, right_y - y_dif), (left_x-x_dif, left_y-y_dif)]

        center_diff = self.center[1] - (left_y+right_y)/2

        rect_pts = [(point[0], self.height - point[1] - center_diff) for point in rect_pts]

        pygame.draw.polygon(self.screen, color, rect_pts)


    def draw_square(self, x, y, m_0, color=(10,100,10)):
        if m_0 != 0:
            m_1 = -1.0/m_0
        else:
            m_1 = 9999999

        theta = math.atan(m_0)

        left_x, right_x = -math.cos(theta) * (self.square_radius), math.cos(theta) * self.square_radius
        left_y, right_y = m_0*left_x, m_0*right_x

        theta_2 = math.atan(m_1)

        x_dif, y_dif = (self.square_radius) * math.cos(theta_2), (self.square_radius) * math.sin(theta_2)

        rect_pts = [(left_x + x_dif, left_y + y_dif), (right_x + x_dif, right_y + y_dif),
                    (right_x - x_dif, right_y - y_dif), (left_x-x_dif, left_y-y_dif)]

        y_diff = y - (left_y+right_y)/2
        x_diff = x

        rect_pts = [(point[0] + x_diff, self.height - point[1] - y_diff) for point in rect_pts]

        pygame.draw.polygon(self.screen, color, rect_pts)

    def display_bar(self, l_val, r_val, color=(2, 2, 2)):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return ("EXIT")

        self.screen.fill((255, 255, 255))

        m_0 = self.get_bar_slope(l_val, r_val)
        self.draw_bar(l_val, r_val, m_0, color)

        pygame.display.update()

        return "True"

    def display_square_bar(self, l_val, r_val, square_col=(255,0,0), bar_col=(0,0,255), move=True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return ("EXIT")

        self.screen.fill((255, 255, 255))

        m_0 = self.get_bar_slope(l_val, r_val)

        self.draw_bar(l_val, r_val, m_0, bar_col)

        y = self.center[1] + (self.box_height/2) + self.square_radius
        y += (self.square_x - (self.width/2)) * m_0

        self.draw_square(int(self.square_x), int(y), m_0, square_col)

        if move:
            self.square_x += -5 if m_0 > 0 else 5

        pygame.display.update()

        return "True"

    def display_hidden(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return ("EXIT")

        self.screen.fill((200,10,10))

        pygame.display.update()

        return "True"

    def process_mode(self, l_torque, l_mvt, r_torque, r_mvt):
        # Set the global program state that's used for saving information 
        self.state[0] = self.internal_mode

        time_0, time_1, time_2, time_3 = 2, 2, 5, 3

        raise_thresh = .2 * min(l_mvt, r_mvt)

        # Box mass
        m = 10
        # Acceleration due to gravity
        g = 9.8
        # Static friction coefficient
        sf = .15

        l_perc = l_torque / l_mvt
        r_perc = r_torque / r_mvt

        """
        Modes

        MAIN_GAME:DEFAULT
    
        MAIN_GAME:START: Play MAIN_GAME:START; set color, wait 2 seconds

        MAIN_GAME:RELAX: Play "Relax," wait until forces go below .05 or 2 seconds

        MAIN_GAME:RAISE: Play "Raise," wait until sum of percentage of forces surpass .8 

        fork

        MAIN_GAME:SUCCESS: Display square dropping onto platform

        MAIN_GAME:FAILURE: Display square dropping off platform

        MAIN_GAME:WAIT: Wait to see if we should loop or not
        """
        if self.internal_mode == "MAIN_GAME:DEFAULT":
            return self.display_square_bar(l_torque, r_torque, (255,0,0), (0,0,0), False)
            # return self.display_bar(l_torque, r_torque)
        
        elif self.internal_mode == "MAIN_GAME:START":
            if time.time()-self.refrence_time > time_0:
                
                self.sound_cues["relax"].play()
                self.internal_mode = "MAIN_GAME:RELAX"
                self.refrence_time = time.time()
            return self.display_hidden()
        
        elif self.internal_mode == "MAIN_GAME:RELAX":
            if l_perc < .05 and r_perc < .05 and time.time()-self.refrence_time > time_1:
                self.sound_cues["match forces"].play()
                self.internal_mode = "MAIN_GAME:RAISE"
                self.refrence_time = time.time()
                self.square_x = self.width/2
            return self.display_hidden()

        elif self.internal_mode == "MAIN_GAME:RAISE":
            if l_torque + r_torque > 2 * raise_thresh:

                theta = abs(math.atan(self.get_bar_slope(l_torque, r_torque)))

                f = m * g * math.sin(theta) - sf * m * g * math.cos(theta)

                print(f"Angle={theta}, f={f}")

                if f > 0:
                    self.internal_mode = "MAIN_GAME:FAILURE"
                    self.locked_forces = [l_perc, r_perc]
                else:
                    self.internal_mode = "MAIN_GAME:SUCCESS"
                    self.locked_forces = [l_perc, r_perc]
                    # self.locked_forces = [l_perc, l_perc] #Artificially make it seem like it's perfectly matched

                self.refrence_time = time.time()
            return self.display_hidden()

        elif self.internal_mode == "MAIN_GAME:FAILURE":
            if time.time()-self.refrence_time > time_2:
                self.internal_mode = "MAIN_GAME:WAIT"
                return "SAVE,MAIN_GAME:FAILURE"
            return self.display_square_bar(*self.locked_forces, (255,0,0), (0,0,0), True)

        elif self.internal_mode == "MAIN_GAME:SUCCESS":
            if time.time()-self.refrence_time > time_2:
                self.internal_mode = "MAIN_GAME:WAIT"
                return "SAVE,MAIN_GAME:SUCCESS"
            return self.display_square_bar(*self.locked_forces, (0,255,0), (0, 0, 0), False)

        elif self.internal_mode == "MAIN_GAME:WAIT":
            if not self.test_data["continue"]:
                self.internal_mode = "MAIN_GAME:DEFAULT"
            else:
                if time.time()-self.refrence_time > time_3:
                    if self.test_data["test_number"] < self.test_data["number_of_tests"]:
                        self.internal_mode = "MAIN_GAME:START"
                        self.test_data["test_number"] += 1
                        print("LOOP")
                    else:
                        self.internal_mode = "MAIN_GAME:DEFAULT"

            return "" 

    def begin_automation(self):
        self.internal_mode = "MAIN_GAME:START"
        self.refrence_time = time.time()
        self.sound_cues["starting"].play()

    def process_data(self, l_torque, r_torque, mvt_l, mvt_r):
        if time.time() - self.prev_time > self.frame_time:
            self.prev_time = time.time()
            return self.process_mode(l_torque, mvt_l, r_torque, mvt_r)
        else:
            return "True"


if __name__ == '__main__':
    bt = bar_game()
