from __future__ import division

"""
BattleSim is the subclass that runs the battle itself.
The sim is expected to be subclassed so as to program in the game rules.
"""

import pygame
import time
import actor_subtypes

from engine.render import battle_screen

class BattleSim (battle_screen.BattleScreen):
    def __init__(self, engine):
        super(BattleSim, self).__init__(engine)
        
        self.next_cycle = time.time()
        
        self.set_speed(1000)
        
        self.running = True
        self.loaded = False
        
        self.actor_types = {}
    
    def set_speed(self, cycles_per_second):
        self.cycles_per_second = cycles_per_second
        self._cycle_delay = 1/self.cycles_per_second
    
    def redraw(self):
        # If we've not loaded anything yet then we won't need to cycle
        if not self.loaded:
            super(BattleSim, self).redraw()
            return
        
        # Main logic execution loop
        if time.time() > self.next_cycle:
            
            # This will warn us if the sim is lagging behind how fast it's meant to be
            time_over = time.time() - self.next_cycle
            if time_over > 0.25:
                print("Logic lag of %ss" % time_over)
            
            # Update the actors themselves
            for a in self.actors:
                a.update(pygame.time.get_ticks())
            
            # Set next cycle time
            self.next_cycle = time.time() + self._cycle_delay
        
        # Now to potentially draw the screen
        super(BattleSim, self).redraw()
    
    def load(self, data):
        # Load types
        for type_name, type_data in data['types'].items():
            self.actor_types[type_name] = type_data
        
        # Load actors
        for actor_data in data['actors']:
            atemplate   = self.actor_types[actor_data['type']]
            aclass      = actor_subtypes.types[atemplate['type']]
            
            a = aclass()
            a.apply_template(atemplate)
            a.apply_data(actor_data)
            self.add_actor(a)
        
        self.loaded = True

