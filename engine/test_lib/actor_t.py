import unittest
from engine.logic import actors

class ActorTester(unittest.TestCase):
    def test_turn_ai(self):
        vals = (
            ([0,0], [10, 10, 0], 90, [90,0]),
            ([90,0], [10, 10, 0], 90, [135,0]),
        )
        
        for current_facing, target_pos, turn_speed, expected in vals:
            # Setup Actor
            the_actor = actors.Actor()
            the_actor.turn_speed = turn_speed
            the_actor.facing = current_facing
            
            # Turn it
            the_actor._turn_ai(target_pos)
            
            # Test it
            try:
                self.assertEqual(expected, the_actor.facing)
            except Exception as e:
                print(current_facing, target_pos, turn_speed, expected)
                raise
            

suite = unittest.TestLoader().loadTestsFromTestCase(ActorTester)