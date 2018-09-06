""" This contains the Animation class which generates a pygame
animation of the lights """

import pygame
import numpy as np
import sys

DIMENSIONS = (1000, 50)
BLACK = (0, 0, 0)
BORDER = 20

class Animation:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(DIMENSIONS)
        self.screen.fill(BLACK)

    def draw_circles(self, values):
        coords, diameter = spacing(len(values), 
                                 DIMENSIONS[0],
                                 DIMENSIONS[1],
                                 BORDER)
        radius = int(diameter / 2)
        for i, coord in enumerate(coords):
            pygame.draw.circle(self.screen, values[i], coord, radius)

    def update(self, values):
        self.draw_circles(values)
        pygame.display.update()
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def spacing(n, width, height, border):
    xs = np.linspace(border, width - border, n).astype(int)
    y = [height - border] * n
    coords = zip(xs, y)
    diameter = xs[1] - xs[0]
    return coords, diameter

