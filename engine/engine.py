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
    
    def game_logic(self):
        """
        This is called every execution loop to allow the game to execute game logic
        """
        raise Exception("{0}.game_logic() is not implemented".format(self.__class__))
    
    def quit(self, event=None):
        pygame.quit()
        sys.exit()
    
    def startup(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        
        self.display = pygame.display.set_mode((self.window_width, self.window_height))
        
        # Draw screen
        # self.update_window()
    
    def set_screen(self, s):
        # s can be a screen instance or the name of a screen in self.screens
        if s in self.screens:
            s = self.screens[s]
        
        s.engine = self
        
        pygame.display.set_caption(s.name)
        self.current_screen = s
        self.update_window()
    
    # Drawing
    def redraw(self):
        """Called every main loop cycle"""
        sprite_list = self.current_screen.sprites
        
        sprite_list.update(pygame.time.get_ticks())
        rectlist = sprite_list.draw(self.display)
        sprite_list.update(pygame.time.get_ticks())
        rectlist = sprite_list.draw(self.display)
        
        pygame.display.update(rectlist)
        sprite_list.clear(self.display, self.background)
    
    def update_window(self):
        """Used when we've changed screen or want to simply redraw everything"""
        self.background = self.current_screen.background.copy() 
        self.display.blit(self.background, pygame.Rect(0, 0, self.window_width, self.window_height))
        
        pygame.display.flip()
        
        self.redraw()
    
    # Contains main execution loop
    def start(self):
        self.startup()
        
        func_dict = {
            ACTIVEEVENT:        self.current_screen._handle_active,
            KEYDOWN:            self.current_screen._handle_keydown,
            KEYUP:              self.current_screen._handle_keyup,
            MOUSEBUTTONUP:      self.current_screen._handle_mouseup,
            MOUSEBUTTONDOWN:    self.current_screen._handle_mousedown,
            MOUSEMOTION:        self.current_screen._handle_mousemotion,
            QUIT:               self.current_screen.quit,
        }
        
        while True:
            for event in pygame.event.get():
                if event.type in func_dict:
                    func_dict[event.type](event)
                else:
                    # raise Exception("Unhanded event {0}".format(event))
                    pass
            
            self.game_logic()
            self.redraw()
            self.clock.tick(self.fps)
        
        self.quit()
    
