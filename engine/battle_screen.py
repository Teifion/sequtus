import time

import pygame
from pygame.locals import *

import screen

class BattleScreen (screen.Screen):
    def __init__(self):
        super(BattleScreen, self).__init__()
        
        self.background = None
        self.scroll_x, self.scroll_y = 0, 0
        self.last_scroll_x, self.last_scroll_y = -1, -1
    
    def redraw(self):
        if self.last_scroll_x != self.scroll_x or self.last_scroll_y != self.scroll_y:
            self.display.blit(self.background, pygame.Rect(
                self.scroll_x, self.scroll_y,
                self.engine.window_width, self.engine.window_height)
            )
            
            self.last_scroll_x, self.last_scroll_y = self.scroll_x, self.scroll_y
            pygame.display.flip()
        
        super(BattleScreen, self).redraw()
    
    

