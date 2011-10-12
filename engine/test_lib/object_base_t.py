from __future__ import division

import pygame
import unittest
from engine.logic import object_base
from engine.libs import actor_lib

def new_base(pos=[0,0,0], velocity=[0,0], facing=[0,0], size=[10,10]):
    ob = object_base.ObjectBase()
    
    ob.pos = pos
    ob.velocity = velocity
    ob.facing = facing
    ob.size = size
    
    ob.rect = pygame.Rect(
        pos[0] - size[0]/2,
        pos[1] - size[1]/2,
        size[0],
        size[1],
    )
    
    return ob

class ObjectBaseTests(unittest.TestCase):
    def test_contains_point(self):
        test_data = (
            ((93, 761), new_base(pos=[100, 100, 0], size=[41, 41]), None),
            ((93, 761), new_base(pos=[200, 100, 0], size=[41, 41]), None),
            
            ((95, 682), new_base(pos=[100, 677, 0], size=[41, 41]), True),
        )
        
        for point, ob, expected in test_data:
            result = actor_lib.contains_point(ob, point)
            
            self.assertEqual(result, expected)

suite = unittest.TestLoader().loadTestsFromTestCase(ObjectBaseTests)
