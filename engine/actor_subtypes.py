import pygame
from pygame.locals import *

import actors

class Building (actors.Actor):
    speed = 0
    
    def update(self, current_time):
        super(Building, self).update(current_time)
        self.velocity = [0,0]
