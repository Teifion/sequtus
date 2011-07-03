import pygame
from pygame.locals import *

import vectors

class Actor (object):
    """It's intended that you sub-class this"""
    game_update_time = 10
    ai_update_time = 100
    
    image           = pygame.Surface((0,0))
    selector_image  = pygame.Surface((0,0))
    selector_offset = (-0, -0)
    selector_size = 0, 0
    
    def __init__(self, screen):
        super(Actor, self).__init__()
        
        self.screen = screen
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (-100, -100)# Start offscreen
        
        self.next_game_update = 0 # update() hasn't been called yet.
        self.next_ai_update = 0
        
        self.velocity = [0,0]
        self.selected = False
        self.selector_rect = pygame.Rect(-10, -10, 1, 1)
    
    def contains_point(self, point):
        """Point is a length 2 sequence X, Y"""
        if self.rect.left <= point[0] <= self.rect.right:
            if self.rect.top <= point[1] <= self.rect.bottom:
                return True
        
    
    def new_image(self, img):
        self.image = img
        self.rect = self.image.get_rect()
    
    def update(self, current_time):
        if self.next_game_update < current_time:
            self.rect.topleft = vectors.add_vectors(self.rect.topleft, self.velocity)
            self.next_game_update = current_time + self.game_update_time
            
            self.selector_rect = pygame.Rect(
                self.rect.left - self.selector_offset[0], self.rect.top - self.selector_offset[1],
                self.selector_size[0], self.selector_size[1]
            )
        
        if self.next_ai_update < current_time:
            self.next_ai_update = current_time + self.ai_update_time
    
    def run_ai(self):
        pass
    
