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

from engine.libs import actor_lib
from engine.render import battle_screen

class BattleSim (battle_screen.BattleScreen):
    def __init__(self, engine):
        super(BattleSim, self).__init__(engine)
        
        self.next_cycle = time.time()
        
        self.set_speed(50)
        
        self.running = True
        self.loaded = False
        
        self.actor_types = {}
    
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
            
            # Set next cycle time
            self.next_cycle = time.time() + self._cycle_delay
        
        # Now to potentially draw the screen
        super(BattleSim, self).redraw()
    
    def place_actor(self, event, drag, actor_type, actor_data = {}):
        """Called when there's a click while in placement mode"""
        self.place_image = None
        real_mouse_pos = (event.pos[0] - self.scroll_x, event.pos[1] - self.scroll_y)
        
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

