from __future__ import division

"""
BattleSim is the subclass that runs the battle itself.
The sim is expected to be subclassed so as to program in the game rules.
"""

import pygame
import time
import sys
import json
import actor_subtypes

from engine.libs import actor_lib, vectors, geometry
from engine.render import battle_screen

class BattleSim (battle_screen.BattleScreen):
    def __init__(self, engine):
        super(BattleSim, self).__init__(engine)
        
        self.next_cycle = time.time()
        
        self.set_speed(100)
        
        self.running = True
        self.loaded = False
        
        self.actor_types = {}
        self.cycle_count = [0, 0]
    
    def set_speed(self, cycles_per_second):
        self.cycles_per_second = cycles_per_second
        self._cycle_delay = 1/self.cycles_per_second
    
    def issue_orders(self):
        for a, cmd, target in self.orders[self.tick]:
            a.issue_command(cmd, target)
        
        for a, cmd, target in self.q_orders[self.tick]:
            a.append_command(cmd, target)
        
        del(self.orders[self.tick])
        del(self.q_orders[self.tick])
    
    def redraw(self):
        # If we've not loaded anything yet then we won't need to cycle
        if not self.loaded:
            super(BattleSim, self).redraw()
            return
        
        # Main logic execution loop
        if time.time() > self.next_cycle:
            self.logic_cycle()
        
        # Now to potentially draw the screen
        super(BattleSim, self).redraw()
    
    def logic_cycle(self):
        if int(time.time()) != self.cycle_count[1]:
            # print("CPS: %s" % self.cycle_count[0])
            self.cycle_count = [0, int(time.time())]
        
        self.tick += 1
        self.orders[self.tick + self.tick_jump] = []
        self.q_orders[self.tick + self.tick_jump] = []
        self.issue_orders()
        
        # This will warn us if the sim is lagging behind how fast it's meant to be
        time_over = time.time() - self.next_cycle
        if time_over > 0.25:
            print("Logic lag of %ss" % time_over)
        
        # Update the actors themselves
        for a in self.actors:
            a.update()
        
        # Check for collisions
        collisions = []
        collided = set()
        for i, a in enumerate(self.actors):
            # If it's moving it might collide
            if a.velocity != [0,0,0] and a.velocity != (0,0,0):
                for j, b in enumerate(self.actors):
                    if i == j: continue
                    if j in collided: continue
                    if geometry.rect_collision(a.rect, b.rect, True):
                        collisions.append((a,b))
                        
                        collided.add(i)
                        collided.add(j)
        
        # We now have a list of all the collisions
        for obj1, obj2 in collisions:
            # We order them based on aid, this way we always deal with the same
            # actor in the same way and the order the collison was found is
            # irrelevant
            a1 = min(obj1, obj2)
            a2 = max(obj1, obj2)
            
            # Now we tell a1 to reverse and a2 to pause a moment while a1 gets
            # out of the way
            a1.reverse(0, 15)
            a2.pause(2)
        
        # Set next cycle time
        self.next_cycle = time.time() + self._cycle_delay
        self.cycle_count[0] += 1
    
    def place_actor(self, event, drag, actor_type, actor_data = {}):
        """Called when there's a click while in placement mode"""
        self.place_image = None
        real_mouse_pos = (event.pos[0] - self.draw_margin[0], event.pos[1] - self.draw_margin[1])
        
        aclass = actor_subtypes.types[actor_type['type']]
        
        a = aclass()
        a.apply_template(actor_type)
        a.apply_data(actor_data)
        
        # It's a new unit so it's 0% complete so far
        a.completion = 0
        
        if "pos" not in actor_data:
            a.pos[0], a.pos[1] = real_mouse_pos
        self.add_actor(a)
    
    def load_all(self, config_path, setup_path, game_path):
        """Uses a local path for each of the 3 load types"""
        
        with open("{0}/{1}".format(sys.path[0], config_path)) as f:
            data = json.loads(f.read())
            self.load_config(data)
        
        with open("{0}/{1}".format(sys.path[0], setup_path)) as f:
            data = json.loads(f.read())
            self.load_setup(data)
        
        with open("{0}/{1}".format(sys.path[0], game_path)) as f:
            data = json.loads(f.read())
            self.load_game(data)
    
    def load_config(self, data):
        pass
    
    def load_setup(self, data):
        # Load types
        for type_name, type_data in data['types'].items():
            actor_lib.build_template_cache(type_data, self.engine)
            self.actor_types[type_name] = type_data
    
    def load_game(self, data):
        # Load actors
        for actor_data in data['actors']:
            atemplate   = self.actor_types[actor_data['type']]
            aclass      = actor_subtypes.types[atemplate['type']]
            
            a = aclass()
            a.apply_template(atemplate)
            a.apply_data(actor_data)
            self.add_actor(a)
        
        self.loaded = True

