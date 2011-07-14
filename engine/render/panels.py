import math

import pygame
from pygame.locals import *

# Used to define a section of the screen used for build options
# unit commands, resources etc etc
class Panel (object):
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
        if self._image != None and not self.changed:
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
    def __init__(self, engine, size, grid_size, position):
        super(TabularMenu, self).__init__(engine)
        
        self.size       = size
        self.grid_size  = grid_size
        
        self.position.topleft = position
        
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
    
    def handle_mouseup(self, event, drag=False):
        relative_pos = (event.pos[0] - self.position.left, event.pos[1] - self.position.top)
        
        col = relative_pos[0]/self.grid_size[0]
        row = relative_pos[1]/self.grid_size[1]
        col_count = int(math.floor(self.size[0]/self.grid_size[0]))
        
        index = (col_count * row) + col
        
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
    def __init__(self, engine, size, position):
        super(MiniMap, self).__init__(engine)
        
        self.size       = size
        
        self.position.topleft = position
        
        """actors is a dictionary, the keys are the team colours and the value is a list
        of tuples: (x, y, size).
        Size is in pixels"""
        self.actors = {}
    
    def draw(self):
        self._image = pygame.Surface(self.size)
        self._image.fill((100, 255, 100), pygame.Rect(0, 0, self.size[0], self.size[1]))
        
        for team_colour, actor_list in self.actors.items():
            for x, y, size in actor_list:
                self._image.fill(team_colour, pygame.Rect(x,y, size, size))
        
        self.position.size = self.size
    

