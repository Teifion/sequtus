import pygame
import unittest
from engine.libs import ai_lib

class DummyActor (object):
    def __init__(self, *args):
        super(DummyActor, self).__init__()
        self.rect = pygame.Rect(*args)

class AILibTests(unittest.TestCase):
    def test_place_actor(self):
        vals = (
            ([DummyActor(1000, 1000, 50, 50)], pygame.Rect(1000, 1000, 50, 50), pygame.Rect(900, 950, 50, 50)),
            
            ([
                DummyActor(1000, 1000, 50, 50),
                DummyActor(900, 1000, 50, 50),
            ], pygame.Rect(1000, 1000, 50, 50), pygame.Rect(900, 1150, 50, 50)),
            
            ([
                DummyActor(1879, 1879, 41, 50),
                DummyActor(1779, 1816, 41, 50),
                DummyActor(1679, 1716, 41, 50),
                DummyActor(1779, 1816, 41, 50),
            ], pygame.Rect(1700, 1800, 50, 50), pygame.Rect(1600, 1650, 50, 50)),
        )
        
        for actor_list, new_rect, expected in vals:
            self.assertEqual(expected, ai_lib.place_actor(actor_list, new_rect, distance=100))

suite = unittest.TestLoader().loadTestsFromTestCase(AILibTests)