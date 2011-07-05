from __future__ import division
import pygame
from pygame.locals import *

import vectors

class Actor (object):
    """It's intended that you sub-class this"""
    game_update_time = 10
    ai_update_time = 100
    
    image           = pygame.Surface((0,0))
    selector_image  = pygame.Surface((0,0))
    selector_offset = (-0, -0)
    selector_size = 0, 0
    
    speed = 5
    
    max_hp = 10
    
    def __init__(self, screen):
        super(Actor, self).__init__()
        
        self.screen = screen
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (-100, -100)# Start offscreen
        self.pos = (-100, -100)
        
        self.next_game_update = 0 # update() hasn't been called yet.
        self.next_ai_update = 0
        
        self.velocity = [0,0]
        self.selected = False
        self.selector_rect = pygame.Rect(-10, -10, 1, 1)
        
        self.team = -1
        
        # An order is a tuple of (command_type, target)
        self.order_queue = []
        self.current_order = ("stop", None)
        
        self.hp = 10
        self._health_bar = (None, None)
    
    def health_bar(self):
        if self._health_bar[1] != self.hp:
            s = pygame.Surface((self.rect.width, 3))
            
            hp_percent = self.hp/self.max_hp
            fill_width = self.rect.width * hp_percent
            
            s.fill((0,0,0), pygame.Rect(0,0, self.rect.width, 3))
            s.fill((0,255,0), pygame.Rect(0,0, fill_width, 3))
            
            self._health_bar = (s, self.hp)
        
        hp_rect = pygame.Rect(
            self.rect.left,
            self.rect.top - 4,
            self.rect.width,
            3
        )
        
        return self._health_bar[0], hp_rect
    
    def selection_rect(self):
        return pygame.Rect(
                self.rect.left - 3,
                self.rect.top - 3,
                self.rect.width + 6,
                self.rect.height + 6,
        )
    
    def contains_point(self, point):
        """Point is a length 2 sequence X, Y"""
        left = self.pos[0] - self.rect.width/2
        right = self.pos[0] + self.rect.width/2
        
        top = self.pos[1] - self.rect.height/2
        bottom = self.pos[1] + self.rect.height/2
        
        if left <= point[0] <= right:
            if top <= point[1] <= bottom:
                return True
    
    def inside(self, rect):
        if rect[0] <= self.pos[0] <= rect[2]:
            if rect[1] <= self.pos[1] <= rect[3]:
                return True
    
    def new_image(self, img):
        self.image = img
        self.rect = self.image.get_rect()
    
    def update(self, current_time):
        if self.next_game_update < current_time:
            self.check_ai()
            self.pos = vectors.add_vectors(self.pos, self.velocity)
            self.next_game_update = current_time + self.game_update_time
            
            # Set rect
            self.rect.topleft = (
                self.pos[0] + self.screen.scroll_x - self.rect.width/2,
                self.pos[1] + self.screen.scroll_y - self.rect.height/2
            )
            
            # Selector rect
            self.selector_rect = pygame.Rect(
                self.rect.left - self.selector_offset[0], self.rect.top - self.selector_offset[1],
                self.selector_size[0], self.selector_size[1]
            )
        
        if self.next_ai_update < current_time:
            self.next_ai_update = current_time + self.ai_update_time
            self.run_ai()
    
    def issue_command(self, cmd, target):
        "This is used to override any current orders"
        self.order_queue = [(cmd, target)]
        self.next_order()
    
    def append_command(self, cmd, target):
        self.order_queue.append((cmd, target))
        
        # No current command? Lets get to work on this one
        if self.current_order[0] == "stop":
            self.next_order()
    
    def next_order(self):
        # Make it update right away
        self.next_ai_update = 0
        
        "When an order is completed this is called"
        if len(self.order_queue) == 0:
            self.current_order = ("stop", None)
            return
        
        self.current_order = self.order_queue.pop(0)
    
    def check_ai(self):
        cmd, target = self.current_order
        
        if cmd == "stop":
            pass
        
        elif cmd == "move":
            dist = vectors.distance(self.pos, target)
            
            if dist <= vectors.total_velocity(self.velocity):
                self.pos = target
                self.velocity = [0,0]
                self.next_order()
            
        else:
            raise Exception("No handler for cmd %s (target: %s)" % (cmd, target))
    
    def run_ai(self):
        cmd, target = self.current_order
        
        if cmd == "stop":
            self.velocity = [0,0]
        
        elif cmd == "move":
            dist = vectors.distance(self.pos, target)
            self.velocity = vectors.move_to_vector(vectors.angle(self.pos, target), self.speed)
            
            if dist <= vectors.total_velocity(self.velocity):
                self.pos = target
                self.velocity = [0,0]
                self.next_order()
            
        else:
            raise Exception("No handler for cmd %s (target: %s)" % (cmd, target))
        
    
