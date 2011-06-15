import time

import pygame
from pygame.locals import *

class Screen (object):
    def __init__(self):
        super(Screen, self).__init__()
        
        self.sprites = pygame.sprite.RenderUpdates()
        self.name = ""
        
        self.buttons = []
        
        self.scrollx, self.scrolly = 0, 0
        self.mouse_is_down = False
        self.keys_down = {}
        self.mouse = [0,0]
        
        self.engine = None
    
    def add_button(self, b):
        self.buttons.append(b)
    
    
    # Event handlers
    # Internal version allows us to sub-class without requiring a super call
    # makes the subclass cleaner
    def _handle_active(self, event):
        self.handle_active(event)
    
    def handle_active(self, event):
        pass
    
    def _handle_keydown(self, event):
        self.keys_down[event.key] = time.time()
        self.test_for_keyboard_commands()
        self.handle_keydown(event)
    
    def handle_keydown(self, event):
        pass
    
    def _handle_keyup(self, event):
        del(self.keys_down[event.key])
        self.handle_keyup(event)
    
    def handle_keyup(self, event):
        pass
    
    def _handle_mousedown(self, event):
        for b in self.buttons:
            if b.button_down != None:
                if b.contains(event.pos):
                    b.button_down(*b.button_down_args, **b.button_down_kwargs)
        
        self.mouse_is_down = True
        self.handle_mousedown(event)
    
    def handle_mousedown(self, event):
        pass
    
    def _handle_mouseup(self, event):
        for b in self.buttons:
            if b.button_up != None:
                if b.contains(event.pos):
                    try:
                        b.button_up(*b.button_up_args, **b.button_up_kwargs)
                    except Exception as e:
                        print("Func: %s" % b.button_up)
                        print("Args: %s" % b.button_up_args)
                        print("Kwargs: %s" % b.button_up_kwargs)
                        raise
        
        self.mouse_is_down = False
        self.handle_mouseup(event)
    
    def handle_mouseup(self, event):
        pass
    
    def _handle_mousemotion(self, event):
        self.mouse = event.pos
        self.handle_mousemotion(event)
        
        if self.mouse_is_down:
            self._handle_mousedrag(event)
        
    def handle_mousemotion(self, event):
        pass
    
    def _handle_mousedrag(self, event):
        self.handle_mousedrag(event)
    
    def handle_mousedrag(self, event):
        pass
    
    def quit(self, event=None):
        self.engine.quit()
    
    def test_for_keyboard_commands(self):
        # Cmd + Q
        if 113 in self.keys_down and 310 in self.keys_down:
            if self.keys_down[310] <= self.keys_down[113]:# Cmd has to be pushed first
                self.quit()
    
