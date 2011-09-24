"""Autotarget AI is very crude and is designed to run on a player team
so that the actors have basic intelligence. It's not designed to handle
strategic actions or anything beyond handling simple micromanagement.

It is designed to have a direct link to the simulation and not perform
long-running calculations."""

import weakref

from engine.libs import vectors

class Autotargeter (object):
    def __init__(self, sim, team):
        super(Autotargeter, self).__init__()
        
        self.sim = sim
        self.team = team
        
        self.next_update = 0
        
        self.enemy_actors = []
    
    def update(self):
        self.next_update -= 1
        if self.next_update > 0: return
        
        self.enemy_actors = []
        
        for a in self.sim.actors:
            if a.team != self.team:
                self.enemy_actors.append(weakref.ref(a)())
        
        self.next_update = 10
    
    def update_actor(self, the_actor):
        the_actor.enemy_targets = []
        
        for a in self.enemy_actors:
            dist = vectors.distance(a.pos, the_actor.pos)
            
            if dist <= the_actor.max_attack_range:
                the_actor.enemy_targets.append(a)
