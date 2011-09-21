from __future__ import division

import weakref

import pygame
from pygame.locals import *

from engine.libs import vectors
from engine.logic import object_base, abilities

class Actor (object_base.ObjectBase):
    """It's intended that you sub-class this"""
    ai_update_time = 100
    
    accepted_orders = [
        "move",
        "stop",
        "hold",
        "attack",
        "aid",
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
    
    optimum_attack_range    = 100
    max_attack_range        = 100
    
    optimum_heal_range    = 100
    max_heal_range        = 100
    
    repair_rate             = 1
    
    def __init__(self):
        super(Actor, self).__init__()
        
        self.next_ai_update = 0
        self.ai = None
        
        self.selected = False
        self.selector_rect = pygame.Rect(-10, -10, 1, 1)
        
        self.team = -1
        
        # An order is a tuple of (command_type, target)
        self.order_queue = []
        self.rally_orders = []# List of orders given to new units created by this actor
        self.micro_orders = []
        self.current_order = ["stop", -1, -1]
        
        self.hp = 0
        self.construction_rate = 1
        self.completion = 100
        
        self._health_bar = (None, None)
        self._completion_bar = (None, None)
        
        self.build_offset = [0,0]
        
        # These are passed down to the screen, we hold onto them for only a moment
        self.effects = []
        self.bullets = []
        
        # A list of all potential enemy targets as picked by the AI
        self.enemy_targets = []
        
        # A list of preferred targets in order of priority
        self.priority_targets = []
        
        # Flags for order abilities
        self.offence_flags = set()
        self.defence_flags = set()
        
        self.frame = 0
        self.build_queue = []
    
    def health_bar(self, scroll_x, scroll_y):
        """Define width if the actor will be a non-standard
        size (such as if it's rotated)"""
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
        """Define width if the actor will be a non-standard
        size (such as if it's rotated)"""
        if self._completion_bar[1] != self.completion:
            s = pygame.Surface((self.rect.width, 3))
            
            comp_percent = self.completion/100
            fill_width = width * comp_percent
            
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
    
    def selection_rect(self):
        return pygame.Rect(
                self.rect.left - 3,
                self.rect.top - 3,
                self.rect.width + 6,
                self.rect.height + 6,
        )
    
    def apply_data(self, data):
        """Applies transitory data such as position and hp"""
        self.actor_type = data["type"]
        
        self.hp = data.get("hp", self.max_hp)
        self.pos = data.get("pos", self.pos)
        self.velocity = data.get("velocity", self.velocity)
        self.facing = data.get("facing", self.facing)
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
        
        self.build_offset       = data.get("build_offset", self.build_offset)
        
        # self.abilities          = data.get("abilities", self.abilities)
        self.flags              = data.get("flags", self.flags)
        self.size               = data.get("size", self.size)
        
        self.max_attack_range       = data.get("max_attack_range", self.max_attack_range)
        self.optimum_attack_range   = data.get("optimum_attack_range", self.optimum_attack_range)
        
        self.max_heal_range         = data.get("max_heal_range", self.max_heal_range)
        self.optimum_heal_range     = data.get("optimum_heal_range", self.optimum_heal_range)
        
        self.construction_rate          = data.get("construction_rate", self.construction_rate)
        self.construction_heal_rate     = self.construction_rate/100 * self.max_hp
        
        self.abilities = []
    
    def update(self):
        super(Actor, self).update()
        if self.completion < 100: return
        
        self.check_ai()
        
        for a in self.abilities:
            a.update()
        
        self.run_ai()
    
    def can_build(self, item_data, build_lists):
        """Discovers if this actor has the pre-reqs to build the item"""
        
        # Check for tech requirements
        if item_data.get('required_techs', []) != []:
            raise Exception("No handler for required techs in a unit")
        
        # Now we go through all the build lists we have and see if our build
        # request is in one of them
        for f in self.flags:
            if f in build_lists:
                if item_data['name'] in build_lists[f]:
                    return True
        
        return False
    
    def add_ability(self, ability_data):
        atype = ability_data['type']
        the_ability = abilities.lookup[atype](self, ability_data)
        
        for f in the_ability.offence_flags: self.offence_flags.add(f)
        for f in the_ability.defence_flags: self.defence_flags.add(f)
        
        self.abilities.append(the_ability)
    
    def issue_command(self, cmd, pos=None, target=None):
        "This is used to override any current orders"
        if cmd in self.accepted_orders:
            self.order_queue = [(cmd, pos, target)]
            self.next_order()
    
    def append_command(self, cmd, pos=None, target=None):
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
        self.next_ai_update -= 1
        
        # TODO Check with sim AI holder for new orders
        if self.micro_orders == []:
            cmd, pos, target = self.current_order
        else:
            cmd, pos, target = self.micro_orders[0]
        
        if type(target) not in (list, tuple, int) and target != None:
            if target.hp <= 0:
                self.next_order()
        
        if cmd == "stop" or cmd == "hold position":
            if target > 0:
                if self.micro_orders == []:
                    self.current_order[2] -= 1
                else:
                    self.micro_orders[0][2] -= 1
        
        elif cmd == "move":
            pass
            
        elif cmd == "attack":
            if len(self.priority_targets) == 0 or self.priority_targets[0] != target:
                if target in self.priority_targets:
                    i = self.priority_targets.index(target)
                    # del(self.priority_targets[i])
                
                self.priority_targets.insert(0, target)
        
        elif cmd == "aid":
            
            # Can we aid them?
            can_aid = False
            if "construct" in self.defence_flags:
                if target.completion < 100:
                    can_aid = True
            
            if "repair" in self.defence_flags:
                if target.hp < target.max_hp:
                    can_aid = True
            
            if not can_aid:
                self.next_order()
                return self.check_ai()
            
            if len(self.priority_targets) == 0 or self.priority_targets[0] != target:
                if target in self.priority_targets:
                    i = self.priority_targets.index(target)
                    del(self.priority_targets[i])
                
                self.priority_targets.insert(0, target)
        
        else:
            raise Exception("No handler for cmd %s (target: %s)" % (cmd, target))
        
        # Update our objectives etc
        if self.ai != None and self.next_ai_update < 1:
            self.ai.update_actor(self)
            self.next_ai_update = 10
    
    def run_ai(self):
        if self.micro_orders == []:
            cmd, pos, target = self.current_order
        else:
            cmd, pos, target = self.micro_orders[0]
        
        self._attack_ai()
        self._help_ai()
        
        if cmd == "stop" or cmd == "hold position":
            self.velocity = [0,0,0]
            
            if target == 0:
                self.next_order()
        
        elif cmd == "move":
            self._move_ai(pos)
            
            if vectors.distance(self.pos, pos) <= vectors.total_velocity(self.velocity):
                self.pos = pos
                self.velocity = [0,0,0]
                self.next_order()
            
            # dist = vectors.distance(self.pos, pos)
            # self.velocity = vectors.move_to_vector(vectors.angle(self.pos, pos), self.max_velocity)
            # 
            # if dist <= vectors.total_velocity(self.velocity):
            #     self.pos = pos
            #     self.velocity = [0,0,0]
            #     self.next_order()
        
        elif cmd == "attack":
            target = self.get_first_target()
            
            # If we have a target, lets move closer to it
            if target != None:
                attack_pos = vectors.get_midpoint(self.pos, target.pos, self.optimum_attack_range)
                
                self._move_ai(attack_pos)
                
                if vectors.distance(self.pos, attack_pos) <= vectors.total_velocity(self.velocity):
                    self.pos = attack_pos
                    self.velocity = [0,0,0]
                
                # dist = vectors.distance(self.pos, target.pos)
                # 
                # if dist > self.optimum_attack_range:
                #     target_pos = vectors.get_midpoint(self.pos, target.pos, self.optimum_attack_range)
                #     self.velocity = vectors.move_to_vector(vectors.angle(self.pos, target_pos), self.max_velocity)
                # else:
                #     self.velocity = [0,0,0]
                
        
        elif cmd == "aid":
            if target == None:
                target = self.get_first_ally()
            
            # If we have a target, lets move closer to it
            if target != None:
                dist = vectors.distance(self.pos, target.pos)
                
                if dist > self.optimum_heal_range:
                    target_pos = vectors.get_midpoint(self.pos, target.pos, self.optimum_heal_range)
                    self.velocity = vectors.move_to_vector(vectors.angle(self.pos, target_pos), self.max_velocity)
                else:
                    self.velocity = [0,0,0]
            
        else:
            raise Exception("No handler for cmd %s (pos: %s, target: %s)" % (cmd, pos, target))
        
        # Do we have something to build?
        if self.build_queue != []:
            pass
    
    def get_first_target(self):
        if len(self.priority_targets) > 0:
            for a in self.priority_targets:
                if a.team != self.team:
                    return a
        
        if len(self.enemy_targets) > 0:
            return self.enemy_targets[0]
        
        return None
    
    def get_first_ally(self):
        if len(self.priority_targets) > 0:
            for a in self.priority_targets:
                if a.team == self.team:
                    return a
        
        return None
    
    def _move_ai(self, target):
        # First we turn
        if self._turn_ai(target):
            
            # And if facing the right way we accelerate
            self._accelerate_ai(target)
    
    def _turn_ai(self, target):
        target_angle = vectors.angle(self.pos, target)
        
        if vectors.angle_diff(self.facing, target_angle) < self.turn_speed:
            self.facing = target_angle
            return True
        
        # Waiting for vectors.angle_direction to be ready
        if vectors.angle_direction(self.facing[0], target_angle):
            raise Exception("Not implimented")
        else:
            raise Exception("Not implimented")
        
        return False
    
    def _accelerate_ai(self, target):
        dist = vectors.distance(self.pos, target)
        
        if dist > self.max_velocity:
            self.velocity = vectors.move_to_vector(vectors.angle(self.pos, target), self.max_velocity)
        else:
            self.velocity = vectors.move_to_vector(vectors.angle(self.pos, target), dist)
    
    def _help_ai(self):
        """AI handling the process of helping allies"""
        target = None
        for a in self.priority_targets:
            if a.team == self.team:
                target = a
                break
        
        # No ally found, skip this function
        if target == None:
            return
        
        for a in self.abilities:
            if a.can_use(target):
                a.use(target)
    
    def _attack_ai(self):
        """AI handling the process of attacking"""
        
        target = self.get_first_target()
        
        if target == None: return
        
        for a in self.abilities:
            if a.can_use(target):
                a.use(target)
            
        
    
