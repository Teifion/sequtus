import sys
import time
import math
import traceback

import pygame
from pygame.locals import *

from engine.libs import vectors

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
    
    def set_screen(self, s, *args, **kwargs):
        # s can be a screen instance or the name of a screen in self.screens
        if s in self.screens:
            s = self.screens[s]
        elif type(s) == str:
            raise KeyError("Screen '%s' not found in screen dictionary" % s)
        
        # Is it an instance or a class? If the latter we make a new instance of it
        # if "__call__" in dir(s):
        if type(s) == type:
            try:
                s = s(self, *args, **kwargs)
            except Exception as e:
                print("Args: %s" % str(args))
                print("Kwargs: %s" % str(kwargs))
                raise
        
        s.engine = self
        s.display = self.display
        
        pygame.display.set_caption(s.name)
        self.current_screen = s
        self.current_screen.activate()
        self.current_screen.update_window()
    
    # Contains main execution loop
    def start(self):
        self.startup()
        
        try:
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

                if not self.current_screen.self_regulate:
                    self.clock.tick(self.fps)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            self.current_screen.quit()
            raise
        
        self.quit()

class Animation (object):
    """An object that takes a picture and cuts it up into separate frames
    so that we can animate certain objects"""
    
    def __init__(self, filepath, columns=1, rows=1, animation_rate = 0.5, rotate_about=None):
        super(Animation, self).__init__()
        
        if columns < 1:
            raise Exception("Cannot have fewer than 1 column in an animation")
        
        if rows < 1:
            raise Exception("Cannot have fewer than 1 row in an animation")
        
        self.images = []
        self.animation_rate = animation_rate
        
        img = pygame.image.load(filepath)
        r = img.get_rect()
        
        # Break it down into tiles, save the tiles
        tile_width = r.width / columns
        tile_height = r.height / rows
        
        for y in range(rows):
            for x in range(columns):
                tile = pygame.Surface((tile_width, tile_height), SRCALPHA)
                tile.blit(img, (0,0), (x * tile_width, y * tile_height, tile_width, tile_height))
                
                self.images.append(tile)
        
        # Default the rotate about point
        if rotate_about == None:
            rotate_about = 0, 0, 0
        
        # centre_offset is a distance and angle
        self.centre_offset = (
            vectors.distance(rotate_about),
            vectors.angle(rotate_about),
        )
    
    def get_rect(self):
        return self.images[0].get_rect()
    
    def get_rotated_offset(self, angle):
        if self.centre_offset == (0, 0):
            return 0, 0
        
        # Get the actual angle to use
        offset_angle = vectors.bound_angle(
            vectors.add_vectors(self.centre_offset[1], angle)
        )
        
        return vectors.move_to_vector(offset_angle, self.centre_offset[0])
        
    
    def real_frame(self, frame):
        """If the frame count is too high, we need to bring it back
        to the correct number"""
        return frame % len(self.images)
    
    def get(self, img_number=0):
        img_number = int(math.floor(self.animation_rate * img_number))
        img_number = self.real_frame(img_number)
        
        return self.images[img_number]
    
    def __getitem__(self, key):
        if key in self.images: return self.images[key]
        return self.get(key)



