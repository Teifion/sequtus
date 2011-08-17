from __future__ import division
import pygame
from pygame.locals import *

import object_base
from engine.libs import vectors

class Bullet (object_base.ObjectBase):
    """It's intended that you sub-class this"""
    
    acceleration        = 0
    deceleration        = 0
    turn_speed          = 0
    drifts              = True
    max_velocity        = 0
    
    def __init__(self):
        super(Bullet, self).__init__()
        
        self.team = -1
        
        # An order is a tuple of (command_type, target)
        self.hp = 0
    
    def update(self):
        super(Bullet, self).update()
        
        # Check distance to target
        # potentially blow up
    