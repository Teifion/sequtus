from __future__ import division
import pygame
from pygame.locals import *

from engine.libs import vectors

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
    size                = (0,0)
    
    def __init__(self):
        super(Actor, self).__init__()
        
        self.pos = [-100, -100, 0]# Assume we're offscreen
        
        self.next_game_update = 0 # update() hasn't been called yet.
        self.next_ai_update = 0
        
        self.selected = False
        self.selector_rect = pygame.Rect(-10, -10, 1, 1)
        
        self.team = -1
        
        # An order is a tuple of (command_type, target)
        self.order_queue = []
        self.micro_orders = []
        self.current_order = ["stop", -1]
        
        self.hp = 0
        self.completion = 100
        self.velocity = [0,0,0]
        
        self._health_bar = (None, None)
        self._completion_bar = (None, None)
        
        self.__is_moving = False
        
        self.dont_collide_with = {}
        
        self.aid = 0
    
    # These allow us to order actors based on their aid
    def __lt__(self, other): return self.aid < other.aid
    def __gt__(self, other): return self.aid > other.aid
    
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
        self.size               = data.get("size", self.size)
    
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
    
    def update(self):
        self.check_ai()
        self.pos = vectors.add_vectors(self.pos, self.velocity)
        
        # Set rect
        self.rect.topleft = (
            self.pos[0] - self.rect.width/2,
            self.pos[1] - self.rect.height/2
        )
        
        remove = []
        for k in self.dont_collide_with:
            self.dont_collide_with[k] -= 1
            if self.dont_collide_with[k] < 1:
                remove.append(k)
        
        for r in remove: del(self.dont_collide_with[r])
        
        self.run_ai()
    
    def issue_command(self, cmd, target):
        "This is used to override any current orders"
        self.order_queue = [(cmd, target)]
        self.next_order()
    
    def append_command(self, cmd, target):
        self.order_queue.append([cmd, target])
        
        # No current command? Lets get to work on this one
        if self.current_order[0] == "stop":
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
            self.current_order = ["stop", -1]
            return
        
        # Check the target
        target = self.current_order[1]
        if type(target) == list or type(target) == tuple:
            if len(target) == 2:
                self.current_order = [self.current_order[0], [target[0], target[1], 0]]
    
    def insert_order(self, cmd, target):
        """Pushes in a micro order from the engine itself usually something
        small so as to avoid a collision"""
        
        self.micro_orders.insert(0, [cmd, target])
    
    def insert_order_queue(self, queue):
        queue.reverse()
        self.micro_orders = []
        for cmd, target in queue:
            self.micro_orders.insert(0, [cmd, target])
    
    def pause(self, delay):
        self.insert_order("stop", delay)
    
    def reverse(self, distance=0, steps=0):
        if self.current_action()[0] == "move": return
        
        direction = [vectors.bound_angle(vectors.angle(self.velocity)[0] + 180), 0]
        
        if steps > 0:
            distance = vectors.total_velocity(self.velocity) * steps
        
        target = vectors.add_vectors(self.pos, vectors.move_to_vector(direction, distance))
        self.insert_order("move", target)
    
    def current_action(self):
        if self.micro_orders == []:
            return self.current_order
        else:
            return self.micro_orders[0]
    
    def is_moving(self):
        cmd, target = self.current_action()
        
        if cmd in ("stop", "hold position"):
            return False
        
        
        return True
    
    def get_move_target(self):
        cmd, target = self.current_order
        
        if cmd == "move":
            return target
        elif cmd == "stop":
            return None
        else:
            raise Exception("No handler for cmd type '%s'" % cmd)
    
    def check_ai(self):
        # TODO Check with sim AI holder for new orders
        if self.micro_orders == []:
            cmd, target = self.current_order
        else:
            cmd, target = self.micro_orders[0]
        
        if cmd == "stop" or cmd == "hold position":
            if target > 0:
                if self.micro_orders == []:
                    self.current_order[1] -= 1
                else:
                    self.micro_orders[0][1] -= 1
        
        elif cmd == "move" or cmd == "reverse":
            dist = vectors.distance(self.pos, target)
            
            if dist <= vectors.total_velocity(self.velocity):
                self.pos = target
                self.velocity = [0,0,0]
                self.next_order()
            
        else:
            raise Exception("No handler for cmd %s (target: %s)" % (cmd, target))
    
    def run_ai(self):
        if self.micro_orders == []:
            cmd, target = self.current_order
        else:
            cmd, target = self.micro_orders[0]
        
        if cmd == "stop" or cmd == "hold position":
            self.__is_moving = False
            self.velocity = [0,0,0]
            
            if target == 0:
                self.next_order()
        
        elif cmd == "move" or cmd == "reverse":
            self.__is_moving = True
            dist = vectors.distance(self.pos, target)
            self.velocity = vectors.move_to_vector(vectors.angle(self.pos, target), self.max_velocity)
            
            if dist <= vectors.total_velocity(self.velocity):
                self.pos = target
                self.velocity = [0,0,0]
                self.next_order()
            
        else:
            raise Exception("No handler for cmd %s (target: %s)" % (cmd, target))
        
    
