from __future__ import division
import time

import pygame
from pygame.locals import *

import screen

UP_ARROW = 273
DOWN_ARROW = 274
RIGHT_ARROW = 275
LEFT_ARROW = 276

class BattleScreen (screen.Screen):
    def __init__(self, dimensions):
        super(BattleScreen, self).__init__(dimensions)
        
        self.background = None
        self.scroll_x, self.scroll_y = 0, 0
        self.have_scrolled = False
        
        self.scroll_speed = 15
        
        self.scroll_up_key = UP_ARROW
        self.scroll_down_key = DOWN_ARROW
        self.scroll_right_key = RIGHT_ARROW
        self.scroll_left_key = LEFT_ARROW
        
        self.allow_mouse_scroll = False
        
        # Defines how far we can scroll in any direction
        self.scroll_boundaries = (-100, -100, 0, 0)
        
        self.scroll_boundary = 100
        
        self.selected_actors = []
    
    def redraw(self):
        """Overrides the basic redraw as it's intended to be used with more animation"""
        for a in self.actors: a.update(pygame.time.get_ticks())
        
        # Draw background taking into account scroll
        surf = self.engine.display
        surf.blit(self.background_image, pygame.Rect(
            self.scroll_x, self.scroll_y,
            self.engine.window_width, self.engine.window_height)
        )
        
        for a in self.actors:
            surf.blit(a.image, a.rect)
            
            if a.selected:
                surf.blit(a.selector_image, a.selector_rect)
        
        pygame.display.flip()
    
    def handle_keyhold(self):
        # Up/Down
        if self.scroll_up_key in self.keys_down:
            self.scroll_up()
        elif self.scroll_down_key in self.keys_down:
            self.scroll_down()
        
        # Right/Left
        if self.scroll_right_key in self.keys_down:
            self.scroll_right()
        elif self.scroll_left_key in self.keys_down:
            self.scroll_left()
        
        super(BattleScreen, self).handle_keyhold()
    
    def handle_mouseup(self, event, drag=False):
        keys = self.get_control_keys()
        
        if event.button == 1:
            if "shift" not in keys:
                self.unselect_all_actors()
            
            for a in self.actors:
                if a.contains_point(event.pos):
                    self.left_click_actor(a)
                
    def left_click_actor(self, a):
        # keys = self.get_control_keys()
        
        if a.selected:
            self.unselect_actor(a)
        else:
            self.select_actor(a)
    
    def handle_mousedragup(self, event, drag_rect):
        pass
    
    def unselect_all_actors(self):
        for a in self.selected_actors[:]:
            del(self.selected_actors[self.selected_actors.index(a)])
            a.selected = False
    
    def unselect_actor(self, a):
        del(self.selected_actors[self.selected_actors.index(a)])
        a.selected = False
    
    def select_actor(self, a):
        self.selected_actors.append(a)
        a.selected = True
    
    def update(self):
        # It might be that the mouse is scrolling
        # but we only use this if there are no arrow keys held down
        if self.allow_mouse_scroll:
            if self.scroll_up_key not in self.keys_down:
                if self.scroll_down_key not in self.keys_down:
                    if self.scroll_right_key not in self.keys_down:
                        if self.scroll_left_key not in self.keys_down:
                            # None of our scroll keys are down, we can mouse scroll
                            self.check_mouse_scroll()
    
    def check_mouse_scroll(self):
        left_val = self.scroll_boundary - (self.engine.window_width - self.mouse[0])
        right_val = self.scroll_boundary - self.mouse[0]
        
        up_val = self.scroll_boundary - (self.engine.window_height - self.mouse[1])
        down_val = self.scroll_boundary - self.mouse[1]
        
        # Scroll based on how far it is
        if down_val > 0:
            self.scroll_down(down_val/self.scroll_boundary)
        elif up_val > 0:
            self.scroll_up(up_val/self.scroll_boundary)
        
        if left_val > 0:
            self.scroll_left(left_val/self.scroll_boundary)
        elif right_val > 0:
            self.scroll_right(right_val/self.scroll_boundary)
        
    
    def scroll_right(self, rate = 1):
        last_pos = self.scroll_x
        
        self.scroll_x -= rate * self.scroll_speed
        self.scroll_x = max(self.scroll_boundaries[0], self.scroll_x)
        
        amount = self.scroll_x - last_pos
        if amount != 0:
            self.have_scrolled = True
            for a in self.actors:
                a.rect.left += amount
                

    def scroll_left(self, rate = 1):
        last_pos = self.scroll_x
        
        self.scroll_x += rate * self.scroll_speed
        self.scroll_x = min(self.scroll_boundaries[2], self.scroll_x)
        
        amount = self.scroll_x - last_pos
        if amount != 0:
            self.have_scrolled = True
            for a in self.actors:
                a.rect.left += amount
        
    def scroll_down(self, rate = 1):
        last_pos = self.scroll_y
        
        self.scroll_y -= rate * self.scroll_speed
        self.scroll_y = max(self.scroll_boundaries[1], self.scroll_y)
        
        amount = self.scroll_y - last_pos
        if amount != 0:
            self.have_scrolled = True
            for a in self.actors:
                a.rect.top += amount
        
    def scroll_up(self, rate = 1):
        last_pos = self.scroll_y
        
        self.scroll_y += rate * self.scroll_speed
        self.scroll_y = min(self.scroll_boundaries[3], self.scroll_y)
        
        amount = self.scroll_y - last_pos
        if amount != 0:
            self.have_scrolled = True
            for s in self.actors:
                s.rect.top += amount
    
    def add_actor(self, a):
        self.actors.append(a)

