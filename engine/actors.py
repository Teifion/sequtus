import pygame
from pygame.locals import *

import vectors

class Actor (pygame.sprite.Sprite):
    """It's intended that you sub-class this"""
    game_update_time = 10
    ai_update_time = 100
    
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        
        self.screen = screen
        
        self.image = pygame.Surface((0,0))
        self.rect = self.image.get_rect()
        self.rect.topleft = (-100, -100)# Start offscreen
        
        self.next_game_update = 0 # update() hasn't been called yet.
        self.next_ai_update = 0
        
        self.velocity = [0,0]
    
    def new_image(self, img):
        self.image = img
        self.rect = self.image.get_rect()
    
    def update(self, current_time):
        if self.next_game_update < current_time:
            self.rect.topleft = vectors.add_vectors(self.rect.topleft, self.velocity)
            self.next_game_update = current_time + self.game_update_time
        
        if self.next_ai_update < current_time:
            self.next_ai_update = current_time + self.ai_update_time
    
    def run_ai(self):
        pass
    
