from __future__ import division
import pygame
from pygame.locals import *

from engine.libs import vectors

class ObjectBase (object):
    """Actors, bullets and any other active object in the game inherits
    from this class"""
    ai_update_time = 100
    
    image               = ""
    flags               = []
    size                = (0,0)
    
    def __init__(self):
        super(ObjectBase, self).__init__()
        
        self.pos        = [-100, -100, 0]# Assume we're offscreen
        self.velocity   = [0,0,0]
        self.facing     = [0,0]# XY, Z
        
        self.oid = 0
    
    # These allow us to order actors based on their aid
    def __lt__(self, other): return self.oid < other.oid
    def __gt__(self, other): return self.oid > other.oid
    
    def new_image(self, img):
        self.image = img
        self.rect = self.image.get_rect()

    def update(self):
        self.pos = vectors.add_vectors(self.pos, self.velocity)
        
        # Set rect
        self.rect.topleft = (
            self.pos[0] - self.rect.width/2,
            self.pos[1] - self.rect.height/2
        )
    
