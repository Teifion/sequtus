import pygame
from pygame.locals import *

# Used to define a section of the screen used for build options
# unit commands, resources etc etc
class Panel (object):
    def __init__(self):
        super(Panel, self).__init__()
        
        # When set to true the menu will scroll with the screen
        # much like an actor will
        self.scrolls = False
        
        self.visible = True
        
        # Used for caching images as panels don't change that often
        self.changed = False
        self._image = None
    
    def image(self):
        # Try to use the cached version
        if self._image != None and not self.changed:
            return self._image
        
        # Draw the iamge
        
        return self._image
    

# Used to draw a grid of information much like the build
# menus from TA or C&C
class TabularMenu (Panel):
    def __init__(self):
        super(Tabular, self).__init__()
    
    
        