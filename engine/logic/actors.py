from __future__ import division
import pygame
from pygame.locals import *

import object_base
from engine.libs import vectors

class Actor (object_base.ObjectBase):
    """It's intended that you sub-class this"""
    ai_update_time = 100
    
    accepted_orders = [
        "move",
        "stop",
        "hold",
        "attack",
        "defend",
        "patrol",
    ]
    
    max_hp              = 1
    max_shields         = 0
    
    acceleration        = 0
    deceleration        = 0
    turn_speed          = 0
    drifts              = True
    max_velocity        = 0
    
    max_armour          = 0
    max_shield_armour   = 0
    
    abilities           = []
    
    def __init__(self):
        super(Actor, self).__init__()
        
        self.next_ai_update = 0
        
        self.selected = False
        self.selector_rect = pygame.Rect(-10, -10, 1, 1)
        
        self.team = -1
        
        # An order is a tuple of (command_type, target)
        self.order_queue = []
        self.micro_orders = []
        self.current_order = ["stop", -1, -1]
        
        self.hp = 0
        self.completion = 100
        
        self._health_bar = (None, None)
        self._completion_bar = (None, None)
        
        self.dont_collide_with = {}
    
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
    
    def completion_bar(self, scroll_x, scroll_y):
        if self._completion_bar[1] != self.completion:
            s = pygame.Surface((self.rect.width, 3))
            
            comp_percent = self.completion/100
            fill_width = self.rect.width * comp_percent
            
            s.fill((0,0,0), pygame.Rect(0,0, self.rect.width, 3))
            s.fill((200,200,255), pygame.Rect(0,0, fill_width, 3))
            
            self._completion_bar = (s, self.completion)
        
        comp_rect = pygame.Rect(
            self.rect.left + scroll_x,
            self.rect.top + scroll_y - 8,
            self.rect.width,
            3
        )
        
        return self._completion_bar[0], comp_rect
    
    def apply_data(self, data):
        """Applies transitory data such as position and hp"""
        self.hp = data.get("hp", self.max_hp)
        self.pos = data.get("pos", self.pos)
        self.velocity = data.get("velocity", self.velocity)
        self.team = data.get("team", self.team)
        
        self.completion = data.get("completion", self.completion)
        
        self.actor_type = data["type"]
    
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
        
        # self.abilities          = data.get("abilities", self.abilities)
        self.flags              = data.get("flags", self.flags)
        self.size               = data.get("size", self.size)
        
        self.abilities = []
    
    def selection_rect(self):
        return pygame.Rect(
                self.rect.left - 3,
                self.rect.top - 3,
                self.rect.width + 6,
                self.rect.height + 6,
        )
    
    def update(self):
        super(Actor, self).update()
        
        self.check_ai()
        
        remove = []
        for k in self.dont_collide_with:
            self.dont_collide_with[k] -= 1
            if self.dont_collide_with[k] < 1:
                remove.append(k)
        
        for r in remove: del(self.dont_collide_with[r])
        
        self.run_ai()
    
    def issue_command(self, cmd, pos, target=None):
        "This is used to override any current orders"
        if cmd in self.accepted_orders:
            self.order_queue = [(cmd, pos, target)]
            self.next_order()
    
    def append_command(self, cmd, pos, target=None):
        if cmd in self.accepted_orders:
            self.order_queue.append([cmd, pos, target])
            
            # No current command? Lets get to work on this one
            if self.current_order[0] == "stop":
                if self.current_order[1] <= 0:
                    self.next_order()
    
    def next_order(self):
        # Make it update right away
        self.next_ai_update = 0
        
        "When an order is completed this is called"
        if self.micro_orders != []:
            del(self.micro_orders[0])
        
        elif self.order_queue != []:
            self.current_order = self.order_queue.pop(0)
        
        elif self.order_queue == []:
            self.current_order = ["stop", -1, -1]
            return
        
        # Check the target of our order, it might be a 2D vector, we need
        # to make it a 3D vector
        pos = self.current_order[1]
        if type(pos) == list or type(pos) == tuple:
            if len(pos) == 2:
                self.current_order = [
                    self.current_order[0],
                    [pos[0], pos[1], self.pos[2]],
                    self.current_order[2]
                ]
    
    def insert_order(self, cmd, pos, target=None):
        """Pushes in a micro order from the engine itself usually something
        small so as to avoid a collision"""
        
        self.micro_orders.insert(0, [cmd, pos, target])
    
    def insert_order_queue(self, queue):
        queue.reverse()
        self.micro_orders = []
        for cmd, pos, target in queue:
            self.micro_orders.insert(0, [cmd, pos, target])
    
    def current_action(self):
        if self.micro_orders == []:
            return self.current_order
        else:
            return self.micro_orders[0]
    
    def is_moving(self):
        cmd, pos, target = self.current_action()
        
        if cmd in ("stop", "hold position"):
            return False
        
        return True
    
    def check_ai(self):
        # TODO Check with sim AI holder for new orders
        if self.micro_orders == []:
            cmd, pos, target = self.current_order
        else:
            cmd, pos, target = self.micro_orders[0]
        
        if cmd == "stop" or cmd == "hold position":
            if target > 0:
                if self.micro_orders == []:
                    self.current_order[2] -= 1
                else:
                    self.micro_orders[0][2] -= 1
        
        elif cmd == "move" or cmd == "reverse":
            pass
            
        else:
            raise Exception("No handler for cmd %s (target: %s)" % (cmd, target))
    
    def run_ai(self):
        print(self.abilities)
        
        if self.micro_orders == []:
            cmd, pos, target = self.current_order
        else:
            cmd, pos, target = self.micro_orders[0]
        
        if cmd == "stop" or cmd == "hold position":
            self.velocity = [0,0,0]
            
            if target == 0:
                self.next_order()
        
        elif cmd == "move" or cmd == "reverse":
            dist = vectors.distance(self.pos, pos)
            self.velocity = vectors.move_to_vector(vectors.angle(self.pos, pos), self.max_velocity)
            
            if dist <= vectors.total_velocity(self.velocity):
                self.pos = pos
                self.velocity = [0,0,0]
                self.next_order()
            
        else:
            raise Exception("No handler for cmd %s (pos: %s, target: %s)" % (cmd, pos, target))
        
    
