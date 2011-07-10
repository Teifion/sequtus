import pygame
from pygame.locals import *

def draw_text(surface, text, position, colour=(0,0,0),
    font="Helvetica", size=20, antialias=1, bold=False, italic=False,
    font_obj=None):
    
    if not font_obj:
        font_obj = pygame.font.SysFont(font, size)
        
        font_obj.set_bold(bold)
        font_obj.set_italic(italic)
    
    textobj = font_obj.render(text, antialias, colour)
    textrect = textobj.get_rect()
    textrect.topleft = position
    surface.blit(textobj, textrect)

class TextDisplay (pygame.sprite.Sprite):
    def __init__(self, position, text, font_name="Helvetica", font_size=20, colour=(255,0,0)):
        pygame.sprite.Sprite.__init__(self)
        
        self.font = pygame.font.SysFont(font_name, font_size)
        
        self.position = position
        
        self.colour = colour
        self.text = text
        self._last_text = ""
        
        self.bold = False
        self.italic = False
        
        if list(colour) == [255,255,255]:
            self.fill_colour = (0,0,0,0)
        else:
            self.fill_colour = (255,255,255,255)
        
        self.update()
    
    def update(self, *args, **kwargs):
        if self._last_text != self.text:
            self._last_text = self.text
            
            if self.text == "":
                self.rect = pygame.Rect(-100, -100, 0, 0)
                return
            
            self.image = pygame.Surface(self.font.size(self.text), SRCALPHA)
            self.image.fill(self.fill_colour)
            self.image.set_colorkey(self.fill_colour)
            
            area = Rect(33,33,33,33)
            self.image.fill((255,255,255,255), area, BLEND_RGBA_SUB)
            
            # self.image = pygame.Surface(self.font.size(self.text))
            self.rect = self.image.get_rect()
            self.rect.topleft = self.position
            
            textobj = self.font.render(self.text, 1, self.colour)
            textrect = textobj.get_rect()
            textrect.topleft = (0, 0)
            # self.image.blit(textobj, textrect)

class Button (pygame.sprite.Sprite):
    def __init__(self, position, image):
        pygame.sprite.Sprite.__init__(self)
        
        self.image = image.copy()
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        
        self.has_updated = False
        self.button_down = None
        self.button_up = None
        
        self.button_up_args = []
        self.button_down_args = []
        
        self.button_up_kwargs = {}
        self.button_down_kwargs = {}
    
    def contains(self, pos):
        if self.rect.left <= pos[0] <= self.rect.right:
            if self.rect.top <= pos[1] <= self.rect.bottom:
                return True
        
        return False
    
    def update(self, *args, **kwargs):
        pass

class InvisibleButton (object):
    """Used when we don't want to draw a button
    e.g. it's part of the background or something"""
    def __init__(self, position, size):
        super(InvisibleButton, self).__init__()
        
        self.left, self.top = position
        self.right = self.left + size[0]
        self.bottom = self.top + size[1]
        
        self.button_down = None
        self.button_up = None
        
        self.button_up_args = []
        self.button_down_args = []
        
        self.button_up_kwargs = {}
        self.button_down_kwargs = {}
    
    def contains(self, pos):
        if self.left <= pos[0] <= self.right:
            if self.top <= pos[1] <= self.bottom:
                return True
        
        return False


