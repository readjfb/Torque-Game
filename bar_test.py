import pygame
from pygame.locals import *
from pygame.color import *

import math

class bar_test:
    def __init__(self, screen, sound_cues, state):
        self.screen = screen
        self.sound_cues = sound_cues

        self.width, self.height = screen.get_size()

        self.center = (self.width // 2, self.height // 2)

        self.state = state

    def flipped(self, value):
        return self.height - value

    def display_bar(self, l_val, r_val, color=(2, 2, 2)):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return ("EXIT")

        self.screen.fill((255, 255, 255))

        # # Takes in two values from 0-1 that correspond with the the amount of force exerted
        left_x, right_x = int(self.width*.25), int(self.width*.75)
        side_len = 30

        left_y, right_y = self.height * l_val, self.height * r_val

        m_0 = (right_y - left_y) / (right_x - left_x)

        if m_0 != 0:
            m_1 = -1/m_0
        else:
            m_1 = 9999999

        theta = math.atan(m_1)

        # print(left_y, right_y)

        x_dif, y_dif = (side_len/2) * math.cos(theta), (side_len/2) * math.sin(theta)

        rect_pts = [(left_x + x_dif, left_y + y_dif), (right_x + x_dif, right_y + y_dif),
                    (right_x - x_dif, right_y - y_dif), (left_x-x_dif, left_y-y_dif)]

        center_diff = self.center[1] - (left_y+right_y)/2

        rect_pts = [(point[0], self.flipped(point[1]) - center_diff) for point in rect_pts]

        pygame.draw.polygon(self.screen, color, rect_pts)

        pygame.display.update()

        return "True"


    def process_data(self, l_data, r_data, mvt_l, mvt_r):
        # Reach 2x threshold sum MVT to be done with the test
        threshold = .40

        l_data_perc = l_data / mvt_l
        r_data_perc = r_data / mvt_r

        total_force = l_data_perc + r_data_perc

        self.display_bar(l_data_perc, r_data_perc)

        # self.refrence_time = time.time()
        # self.internal_mode = "DEFAULT"


if __name__ == '__main__':
    bt = bar_test()
