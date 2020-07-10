"""
    Not currently using this class!

"""

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk import Vec2d
import pymunk.pygame_util

import time


class ball:
    def __init__(self, position, space, radius):
        self.mass = 30

        self.moment = pymunk.moment_for_circle(self.mass, 0, radius)

        self.body = pymunk.Body(self.mass, self.moment, pymunk.Body.DYNAMIC)
        self.body.position = pymunk.Vec2d(*position)
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.1
        self.shape.friction = 10

        self.shape.color = pygame.color.THECOLORS["red"]

        space.add(self.shape, self.body)


class paddle:
    def __init__(self, position, space, paddle_radius=19):
        self.mass = 1000.0
        # Don't let the circle rotate. However, if a more accurate physics sim is desired, this should be changed
        self.moment = pymunk.inf 
        # self.moment = pymunk.moment_for_circle(self.mass, 0, paddle_radius)
        self.body = pymunk.Body(self.mass, self.moment, pymunk.Body.DYNAMIC)
        self.body.position = pymunk.Vec2d(*position)
        self.shape = pymunk.Circle(self.body, paddle_radius)
        self.shape.elasticity = 0.0
        self.shape.friction = 10

        space.add(self.shape, self.body)


class box:
    def __init__(self, space, position, width, height):
        self.mass = 50
        self.moment = pymunk.moment_for_box(self.mass, (width, height))
        self.body = pymunk.Body(self.mass, self.moment, pymunk.Body.DYNAMIC)
        self.body.position = pymunk.Vec2d(*position)
        points = [(-width/2, 0), (width/2, 0), (width/2, height), (-width/2, height)]
        self.shape = pymunk.Poly(self.body, points)
        self.shape.elasticity = 0.0
        self.shape.friction = 20

        self.shape.color = pygame.color.THECOLORS["black"]

        space.add(self.body, self.shape)


class game(object):
    def __init__(self, screen, paddle_radius, state, fps=25):
        """
        Creates the main tray game

        :param screen: the pygame screen object to be drawn to
        :param width: pygame width
        :param height: pygame height
        :param paddle_radius: size of the paddle
        :param fps: the approximate locked fps of the game
        """
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.clock = pygame.time.Clock()

        self.max_force = 1
        self.min_force = 0

        self.space = pymunk.Space()

        self.space.iterations = 30

        # self.space.gravity = (0.0, 0.0)
        self.space.gravity = (0.0, -500.0)

        self.static_lines = []

        self.prev_time = time.time()
        self.frame_time = 1.0/fps

        # Create the floor
        floor_height = 10
        body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        shape = pymunk.Segment(body, [0, floor_height], [self.width, floor_height], 0.0)
        shape.friction = 10
        self.space.add(shape)
        self.static_lines.append(shape)

        fourth = self.width/4

        # Create the left paddle
        self.left_paddle = paddle((fourth, 200), self.space)

        self.right_paddle = paddle((fourth*3, 200), self.space)

        self.box = box(self.space, (fourth*2, 500), self.width*.9, 30)

        self.ball = ball((fourth*2, 550), self.space, 10)

        self.draw_options = pymunk.pygame_util.DrawOptions(screen)

        self.state = state

    def converted(self, point):
        """
        Converts the point 'point' from range [self.min_force, self.max_force] -> [0, self.height]

        :param point: Point on range [self.min_force, self.max_force] to be converted
        :return: returns the converted value
        """
        m = float(self.height - 0) / (self.max_force - self.min_force)
        return m * (point - self.min_force)

    def draw_tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False

        self.screen.fill((255,255,255))

        self.space.debug_draw(self.draw_options)

        pygame.display.flip()

    def reset(self):
        # Untested, still needs to be automated
        del self.box
        del self.ball

        self.box = box(self.space, (fourth*2, 500), self.width*.9, 30)

        self.ball = ball((fourth*2, 550), self.space, 10)

    def update_tick(self, l_data, r_data):
        """
        Main updater for the main_game object
        Takes in the left and right data; sets the paddle positions accordingly, and updates the physics engine

        If the time as calculated by the game's internal buffer dictates it so, it also updates the pygame visual

        :param l_data: the current left datapoint
        :param r_data: the current right datapoint
        """
        dt = 1.0/50
        self.space.step(dt)
        self.clock.tick(50)

        # This should be changed if a more acurate physics simulation is desired
        r_acc_new = (self.converted(r_data) - self.right_paddle.shape.body.position.y) * 3
        l_acc_new = (self.converted(l_data) - self.left_paddle.shape.body.position.y) * 3

        self.right_paddle.shape.body.velocity = (0, r_acc_new)
        self.left_paddle.shape.body.velocity = (0, l_acc_new)

        if time.time() - self.prev_time > self.frame_time:
            self.prev_time = time.time()
            return self.draw_tick()
        else:
            return True
