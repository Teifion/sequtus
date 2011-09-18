from __future__ import division

import pygame

import math

def set_fps(screen, fps):
    screen._redraw_delay = 1/fps

def get_facing_angle(angle, facings=36):
    """Takes an angle and gives the 'rounded' result"""
    angle_per_facing = 360/facings
    
    return int(math.floor(angle/angle_per_facing) * angle_per_facing)

def make_rotated_image(image, angle):
    return pygame.transform.rotate(image, -angle)

