import unittest
from engine.libs import math_lib

class MathTests(unittest.TestCase):
    pass
    # def test_suvat(self):
    #     vals = (
    #         # Distance
    #         ("v1", {}, 0),
    #     )
    #     
    #     for target, kwargs, expected in vals:
    #         self.assertEqual(expected, math_lib.suvat(target, **kwargs))

suite = unittest.TestLoader().loadTestsFromTestCase(MathTests)