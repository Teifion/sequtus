from __future__ import division

from engine.libs import geometry

def set_speed(sim, cycles_per_second):
    sim.cycles_per_second = cycles_per_second
    sim._cycle_delay = 1 / cycles_per_second

def get_collisions(actors):
    collisions = []
    collided = set()
    for i, a in enumerate(actors):
        for j, b in enumerate(actors):
            if j in collided: continue
            if i == j: continue
            if geometry.rect_collision(a.rect, b.rect, True):
                collisions.append((a,b))
        
        collided.add(i)
    
    return collisions

def test_possible_collision(actors, new_rect):
    """
    Used to test if a potential actor will collide with anything else
    returns True if there will be a collision
    """
    
    for a in actors:
        if geometry.rect_collision(a.rect, new_rect, True):
            return True
    
    return False

