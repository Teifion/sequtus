import unittest
from engine.libs import vectors, geometry

class GeometryTests(unittest.TestCase):
    def test_rectangle_collision(self):
        vals = (
            # R1 is up and to the left of R2
            ((5, 5, 15, 15), (10, 10, 20, 20), True),
            ((2, 2, 8, 8), (10, 10, 20, 20), False),
            
            # R1 is up of R2
            ((10, 5, 20, 15), (10, 10, 20, 20), True),
            ((10, 2, 20, 8), (10, 10, 20, 20), False),
            
            # R1 is up and to the right of R2
            ((15, 5, 25, 15), (10, 10, 20, 20), True),
            ((15, 2, 25, 8), (10, 10, 20, 20), False),
            
            # R1 is left of R2
            ((5, 10, 15, 20), (10, 10, 20, 20), True),
            ((2, 10, 8, 20), (10, 10, 20, 20), False),
            
            # R1 is right of R2
            ((15, 10, 25, 20), (10, 10, 20, 20), True),
            ((25, 10, 30, 20), (10, 10, 20, 20), False),
            
            # R1 is down and to the left of R2
            ((5, 15, 15, 25), (10, 10, 20, 20), True),
            ((2, 15, 8, 25), (10, 10, 20, 20), False),
            
            # R1 is down of R2
            ((10, 15, 20, 25), (10, 10, 20, 20), True),
            ((10, 22, 20, 28), (10, 10, 20, 20), False),
            
            # R1 is down and to the right of R2
            ((15, 15, 25, 25), (10, 10, 20, 20), True),
            ((22, 15, 28, 25), (10, 10, 20, 20), False),
            
            # Overlapping
            ((15, 15, 25, 25), (15, 15, 25, 25), True),# Exact same size
            ((10, 10, 30, 30), (15, 15, 25, 25), True),# R1 is bigger
            ((15, 15, 25, 25), (10, 10, 30, 30), True),# R2 is bigger
        )
        
        for r1, r2, expected in vals:
            # We want to make sure that it'll work for inputs regardless of order
            try:
                self.assertEqual(expected, geometry.rect_collision(r1, r2))
            except Exception as e:
                print("Failed on first pass of %s, %s" % (str(r1), str(r2)))
                raise
            
            try:
                self.assertEqual(expected, geometry.rect_collision(r2, r1))
            except Exception as e:
                print("Failed on second pass of %s, %s" % (str(r1), str(r2)))
                raise
    
    def ttest_inside_angle(self):
        vals = (
            # A is top left, B is bottom middle and C is middle right
            # (([10,5,0], vectors.angle([3,1,0])), ([13,10,0], vectors.angle([2,-1,0])), (40.60, 0)),
            
            # A is bottom left, B is top middle and C is middle right
            (([10,10,0], vectors.angle([3,-1,0])), ([13,3,0], vectors.angle([2,1,0])), (0, 0)),
        )
        
        for A, B, expected in vals:
            answer = geometry.inside_angles(A, B)
            
            try:
                self.assertAlmostEqual(expected[0], answer[0], places=2)
                # self.assertAlmostEqual(expected[1], answer[1], places=2)
            except Exception as e:
                print("Failure with inputs of A=%s, B=%s" % (A, B))
                raise
    
    def ttest_collision_angle(self):
        vals = (
            (([10,5,0], [3,1,0]), ([13,10,0], [2,-1,0]), 0),
        )
        
        for a1, a2, expected in vals:
            self.assertEqual(expected, geometry.rect_collision_angle(a1, a2))



suite = unittest.TestLoader().loadTestsFromTestCase(GeometryTests)