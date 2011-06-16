import sys
import time

import pygame
from pygame.locals import *

class Game_error(Exception):
    """Errors related to the game in general"""
    pass

class Illegal_move(Game_error):
    """Errors from illegal moves"""
    pass

class Game_rule_error(Game_error):
    """Errors that arise from rule issues"""
    pass

class EngineV3 (object):
    fps = 30
    window_width = 0
    window_height = 0
    
    def __init__(self):
        super(EngineV3, self).__init__()
        
        self.screens = {}
        self.current_screen = None
        self.images = {}
    
    def quit(self, event=None):
        pygame.quit()
        sys.exit()
    
    def startup(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        
        self.display = pygame.display.set_mode((self.window_width, self.window_height))
    
    def set_screen(self, s):
        # s can be a screen instance or the name of a screen in self.screens
        if s in self.screens:
            s = self.screens[s]
        elif type(s) == str:
            raise KeyError("Screen '%s' not found in screen dictionary" % s)
        
        s.engine = self
        s.display = self.display
        
        pygame.display.set_caption(s.name)
        self.current_screen = s
        self.current_screen.update_window()
    
    # Contains main execution loop
    def start(self):
        self.startup()
        
        while True:
            for event in pygame.event.get():
                if event.type == ACTIVEEVENT:       self.current_screen._handle_active(event)
                if event.type == KEYDOWN:           self.current_screen._handle_keydown(event)
                if event.type == KEYUP:             self.current_screen._handle_keyup(event)
                if event.type == MOUSEBUTTONUP:     self.current_screen._handle_mouseup(event)
                if event.type == MOUSEBUTTONDOWN:   self.current_screen._handle_mousedown(event)
                if event.type == MOUSEMOTION:       self.current_screen._handle_mousemotion(event)
                if event.type == QUIT:              self.current_screen.quit(event)
            
            # Check to see if a key has been held down
            self.current_screen._handle_keyhold()
            
            self.current_screen.update()
            self.current_screen.redraw()
            self.clock.tick(self.fps)
        
        self.quit()
    
