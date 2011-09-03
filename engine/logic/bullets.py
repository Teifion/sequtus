from __future__ import division
import pygame
from pygame.locals import *

from engine.logic import object_base, effects
from engine.libs import vectors, actor_lib

def _linear(percent):
    return percent

def _square(percent):
    return percent * percent

def _cubic(percent):
    return percent * percent * percent

dissipation_lookup = {
    "linear":   _linear,
    "square":   _square,
    "cubic":    _cubic,
}

def dissipate(damage, distance, max_distance, func):
    # Recursion for dictionary
    if type(damage) == dict:
        new_damage = {}
        for k, v in damage.items():
            new_damage[k] = dissipate(v, distance, max_distance, func)
        
        return new_damage
    
    # Raw number
    # Percent is how much of the distance is left
    percent = 1 - (distance/max_distance)
    
    if func in dissipation_lookup:
        return dissipation_lookup[func](percent) * damage
    
    else:
        raise KeyError("No dissipation function by the name of '%s'" % func)

class Bullet (object_base.ObjectBase):
    """It's intended that you sub-class this"""
    
    acceleration        = 0
    deceleration        = 0
    turn_speed          = 0
    drifts              = True
    max_velocity        = 0
    fall_rate           = 0.1
    
    def __init__(self, blast_radius=0, damage={}, dissipation_func="linear"):
        super(Bullet, self).__init__()
        
        self.team = -1
        self.dead = False
        
        self.blast_radius = blast_radius
        self.damage = damage
        self.dissipation_func = dissipation_func
    
    def update(self):
        self.velocity[2] -= self.fall_rate
        
        super(Bullet, self).update()
        
        # Ideally we'll work out if this is within terrain
        # but in the meantime we'll just assume the terrain is flat
        if self.pos[2] < 0:
            self.dead = True
    
    def draw(self, surface, offset):
        """If the bullet has no image then it must be dynamically drawn"""
        raise Exception("%s has no image but the draw function is not implemented" % self.__class__)
    
    def generate_effect(self):
        """Sometimes the bullet will explode, this is the way to return the effect"""
        return None
    
    def explode(self, actors):
        for a in actors:
            if vectors.distance(self.pos, a.pos) <= self.blast_radius:
                actor_lib.apply_damage(a, dissipate(
                    self.damage, vectors.distance(self.pos, a.pos),
                    self.blast_radius, self.dissipation_func)
                )
        return self.generate_effect()
    
    
class Shell (Bullet):
    def __init__(self, pos, velocity, size=[1,1], image="", blast_radius=0, damage={}, dissipation_func="linear"):
        super(Shell, self).__init__(blast_radius, damage, dissipation_func)
        self.pos = pos
        self.velocity = velocity
        self.width, self.height = size
        
        self.image = image
        
        self.rect = Rect(pos[0] - self.width/2, pos[1] - self.height/2, self.width, self.height)
    
    def generate_effect(self):
        duration = 20
        radius_change = self.blast_radius / duration
        
        e = effects.Explosion(
            center=self.pos,
            colour=(50,0,0),
            radius=0,
            colour_change=(10,0,0),
            radius_change=radius_change,
            duration=duration,
        )
        
        return e