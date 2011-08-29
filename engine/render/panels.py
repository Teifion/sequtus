from __future__ import division

import math

import pygame
from pygame.locals import *

# Used to define a section of the screen used for build options
# unit commands, resources etc etc
class Panel (object):
    always_redraw = False
    accepts_keydown = False
    
    def __init__(self, engine):
        super(Panel, self).__init__()
        
        self.engine = engine
        
        # When set to true the menu will scroll with the screen
        # much like an actor will
        self.scrolls = False
        
        self.visible = True
        
        # Used for caching images as panels don't change that often
        self.changed = False
        self._image = None
        
        self.position = pygame.Rect(0,0,0,0)
    
    def contains(self, point):
        if self.position.left <= point[0] <= self.position.right:
            if self.position.top <= point[1] <= self.position.bottom:
                return True
    
    def image(self):
        # Try to use the cached version
        if self._image != None and not self.changed and not self.always_redraw:
            return self._image, self.position
        
        # Draw the iamge
        self.draw()
        
        return self._image, self.position
    
    def draw(self):
        raise Exception("{0}.draw() is not implemented".format(self.__class__))
    
    def handle_mouseup(self, event, drag=False):
        # Return True to signal that the click was handled
        raise Exception("{0}.handle_mouseup() is not implemented".format(self.__class__))

# Used to draw a grid of information much like the build
# menus from TA or C&C
class TabularMenu (Panel):
    accepts_keyup = True
    
    def __init__(self, engine, size, grid_size, position):
        super(TabularMenu, self).__init__(engine)
        
        self.size       = size
        self.grid_size  = grid_size
        
        self.position.topleft = position
        self.key_map = {}
        
        """
        Buttons is a list of tuples: (image_name, callback, args)
        """
        self.buttons = []
    
    def draw(self):
        self._image = pygame.Surface(self.size)
        self._image.fill((100, 100, 100), pygame.Rect(0, 0, self.size[0], self.size[1]))
        
        col_count = math.floor(self.size[0]/self.grid_size[0])
        
        col, row = 0, 0
        for image_name, callback, args in self.buttons:
            img = self.engine.images[image_name]
            
            self._image.blit(img, pygame.Rect(
                col * self.grid_size[0], row * self.grid_size[1],
                self.grid_size[0], self.grid_size[1],
            ))
            
            col += 1
            if col > col_count:
                col = 0
                row += 1
        
        self.position.size = self.size
        self.changed = False
    
    def handle_keyup(self, event):
        print(event)
    
    def handle_mouseup(self, event, drag=False):
        relative_pos = (event.pos[0] - self.position.left, event.pos[1] - self.position.top)
        
        col = math.floor(relative_pos[0]/self.grid_size[0])
        row = math.floor(relative_pos[1]/self.grid_size[1])
        col_count = int(math.floor(self.size[0]/self.grid_size[0]))
        
        index = int((col_count * row) + col)
        
        # No button there? Ignore the click but they clicked the menu
        # so we don't want to pass this back to the screen
        if index >= len(self.buttons):
            return True
        
        # Get the information for the button
        image_name, callback, args = self.buttons[index]
        
        # Perform callback
        callback(*args)
        
        return True
    

# Used to draw the map
class MiniMap (Panel):
    always_redraw = True
    
    def __init__(self, engine, size, position, map_size):
        super(MiniMap, self).__init__(engine)
        
        self.size       = size
        self.map_size   = map_size
        
        self.position.topleft = position
        
        """actors is a dictionary, the keys are the team colours and the value is a list
        of tuples: (x, y, size).
        Size is in pixels"""
        self.actors = {}
    
    def draw(self):
        self._image = pygame.Surface(self.size)
        self._image.fill((100, 255, 100), pygame.Rect(0, 0, self.size[0], self.size[1]))
        
        xratio = self.map_size[0] / self.size[0]
        yratio = self.map_size[1] / self.size[1]
        
        for a in self.engine.current_screen.actors:
            x,y = a.pos[0] / xratio, a.pos[1] / yratio
            xsize, ysize = a.size[0] / xratio, a.size[1] / yratio, 
            
            self._image.fill((0,0,0), pygame.Rect(x, y, xsize, ysize))
        
        # for team_colour, actor_list in self.actors.items():
        #     for x, y, size in actor_list:
        #         self._image.fill(team_colour, pygame.Rect(x,y, size, size))
        
        self.position.size = self.size


# Used to display text upon a blank background
class InfoBox (Panel):
    def __init__(self, engine, size, position, fill_colour = (0, 0, 0), text_colour = (255, 255, 255)):
        super(InfoBox, self).__init__(engine)
        
        self.size               = size
        self.position.topleft   = position
        self.fill_colour        = fill_colour
        self.text_colour        = text_colour
        
        self.texts = {}
    
    def draw(self):
        self._image = pygame.Surface(self.size)
        self._image.fill(self.fill_colour, pygame.Rect(0, 0, self.size[0], self.size[1]))
        
        for k, t in self.texts.items():
            pass
        
        self.position.size = self.size
    
