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
        self.dead = False
    
    def update(self):
        super(Bullet, self).update()
        
        # Check distance to target
        # potentially blow up
        # print(self.target)
    
    def draw(self, surface, offset):
        """If the bullet has no image then it must be dynamically drawn"""
        raise Exception("%s has no image but the draw function is not implemented" % self.__class__)

class Shell (Bullet):
    def __init__(self, pos, velocity, size=[1,1], image=""):
        super(Shell, self).__init__()
        self.pos = pos
        self.velocity = velocity
        self.width, self.height = size
        
        self.image = image
        
        self.rect = Rect(pos[0] - self.width/2, pos[1] - self.height/2, self.width, self.height)