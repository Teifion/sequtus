from __future__ import division
import pygame
from pygame.locals import *

import vectors

class Actor (object):
    """It's intended that you sub-class this"""
    game_update_time = 10
    ai_update_time = 100
    
    image               = ""
    max_hp              = 1
    max_shields         = 0
    
    acceleration        = 0
    deceleration        = 0
    turn_speed          = 0
    drifts              = True
    max_velocity        = 0
    
    max_armour          = 0
    max_shield_armour   = 0
    
    weapons             = []
    flags               = []
    
    def __init__(self):
        super(Actor, self).__init__()
        
        self.pos = (-100, -100)# Assume we're offscreen
        
        self.next_game_update = 0 # update() hasn't been called yet.
        self.next_ai_update = 0
        
        self.velocity = [0,0]
        self.selected = False
        self.selector_rect = pygame.Rect(-10, -10, 1, 1)
        
        self.team = -1
        
        # An order is a tuple of (command_type, target)
        self.order_queue = []
        self.current_order = ("stop", None)
        
        self.hp = 0
        self._health_bar = (None, None)
    
    def health_bar(self, scroll_x, scroll_y):
        if self._health_bar[1] != self.hp:
            s = pygame.Surface((self.rect.width, 3))
            
            hp_percent = self.hp/self.max_hp
            fill_width = self.rect.width * hp_percent
            
            s.fill((0,0,0), pygame.Rect(0,0, self.rect.width, 3))
            s.fill((0,255,0), pygame.Rect(0,0, fill_width, 3))
            
            self._health_bar = (s, self.hp)
        
        hp_rect = pygame.Rect(
            self.rect.left + scroll_x,
            self.rect.top + scroll_y - 4,
            self.rect.width,
            3
        )
        
        return self._health_bar[0], hp_rect
    
    def apply_data(self, data):
        """Applies transitory data such as position and hp"""
        self.hp = data.get("hp", self.max_hp)
        self.pos = data.get("pos", self.pos)
    
    def apply_template(self, data):
        """Applies more permanent data such as max hp and move speed"""
        self.image              = data.get("image", self.image)
        
        self.max_hp             = data.get("max_hp", self.max_hp)
        self.max_shields        = data.get("max_shields", self.max_shields)
        
        self.acceleration       = data.get("acceleration", self.acceleration)
        self.deceleration       = data.get("deceleration", self.deceleration)
        self.turn_speed         = data.get("turn_speed", self.turn_speed)
        self.drifts             = data.get("drifts", self.drifts)
        self.max_velocity       = data.get("max_velocity", self.max_velocity)
        
        self.max_armour         = data.get("max_armour", self.max_armour)
        self.max_shield_armour  = data.get("max_shield_armour", self.max_shield_armour)
        
        self.weapons            = data.get("weapons", self.weapons)
        self.flags              = data.get("flags", self.flags)
    
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
                self.pos[0] - self.rect.width/2,
                self.pos[1] - self.rect.height/2
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
        
    