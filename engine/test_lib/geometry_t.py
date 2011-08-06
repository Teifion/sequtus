import pygame
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
            ((279, 779, 279+41, 779+41), (279, 779, 279+41, 779+41), True),# Exact same size
            
            ((394, 79, 435, 435), (317, 79, 358, 120), False),
            
            ((10, 10, 30, 30), (15, 15, 25, 25), True),# R1 is bigger
            ((15, 15, 25, 25), (10, 10, 30, 30), True),# R2 is bigger
            
            # Different types
            ((5, 15, 15, 25), pygame.Rect(10, 10, 20, 20), True),
            ((2, 15, 8, 25), pygame.Rect(10, 10, 20, 20), False),
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
    
    # To generated these values I created a lot of triangles with different
    # positions for A, B and C to ensure a range of angles. I then used
    # https://github.com/Teifion/Mini-tools/blob/master/vectors.html
    # to calcuate the various raw angles and with pen+paper calcuated the
    # approximate angles and sizes. If the code was close then I knew
    # it was right as my workings had a lot of rounding errors, if it was
    # not close then something was wrong with either my paper workings
    # or the code.
    collision_vals = (
        # answers = A, B, C, a, b, c
        (([10,5,0], vectors.angle([3,1,0])), ([13,10,0], vectors.angle([2,-1,0])),
            (40.601, 94.398, 45.0,      5.366, 8.22, 5.83)),
        (([5,10,0], vectors.angle([3,-1,0])), ([10,1,0], vectors.angle([1,1,0])),
            (42.51, 74.05, 63.43,       7.778, 11.067, 10.295)),
        (([10,3,0], vectors.angle([1,0,0])), ([0,14,0], vectors.angle([1,-0.5,0])),
            (132.27, 21.16, 26.565,     24.596, 12.0, 14.866)),
        (([5,10,0], vectors.angle([2,-1,0])), ([1,1,0], vectors.angle([1,1,0])),
            (87.4, 21.037, 71.57,       10.370, 3.726, 9.848)),
        
        (([6,1,0], vectors.angle([-1,1,0])), ([15,10,0], vectors.angle([-3,-1,0])),
            (90.0, 26.57, 63.43,        14.230, 6.363, 12.727)),
        (([10,10,0], vectors.angle([-1,-1,0])), ([17,2,0], vectors.angle([-2,0,0])),
            (86.185, 48.814, 45.0,      15.0, 11.313, 10.63)),
        (([20,3,0], vectors.angle([-2,1,0])), ([5,15,0], vectors.angle([-1,-0.5,0])),
            (12.09, 114.78, 53.13,      5.031, 21.801, 19.209)),
        (([12,10,0], vectors.angle([-7,-1,0])), ([3,3,0], vectors.angle([-1,0,0])),
            (29.74, 142.13, 8.13,       40.0, 49.497, 11.401)),
        
        (([5,10,0], vectors.angle([-1,-1,0])), ([10,11,0], vectors.angle([-1.5,-1,0])),
            (146.309, 22.381, 11.309,   14.422, 9.899, 5.099)),
    )
    
    def test_inside_angle(self):
        for act1, act2, expected in self.collision_vals:
            A, B, C, a, b, c = expected
            ansA, ansB, ansC = geometry.inside_angles(act1, act2)
            
            try:
                self.assertAlmostEqual(A, ansA, places=2)
                self.assertAlmostEqual(B, ansB, places=2)
                self.assertAlmostEqual(C, ansC, places=2)
            except Exception as e:
                print("Failure with inputs of A=%s, B=%s" % (act1, act2))
                raise
    
    # This will overlap with the test_inside_angle function but the above
    # will remain incase the functionality is moved around
    def test_collision_angle(self):
        for act1, act2, expected in self.collision_vals:
            A, B, C, a, b, c = expected
            ansA, ansB, ansC, ansa, ansb, ansc = geometry.rect_collision_distance(act1, act2, testing=True)
            
            try:
                self.assertAlmostEqual(A, ansA, places=2)
                self.assertAlmostEqual(B, ansB, places=2)
                self.assertAlmostEqual(C, ansC, places=2)
            except Exception as e:
                print("Failure on angles with inputs of A=%s, B=%s" % (act1, act2))
                raise
            
            try:
                self.assertAlmostEqual(a, ansa, places=2)
                self.assertAlmostEqual(b, ansb, places=2)
                self.assertAlmostEqual(c, ansc, places=2)
            except Exception as e:
                print("Failure on sides with inputs of A=%s, B=%s" % (act1, act2))
                raise
            
        
    



suite = unittest.TestLoader().loadTestsFromTestCase(GeometryTests)