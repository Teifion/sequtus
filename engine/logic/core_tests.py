import unittest
from engine.test_lib import *

def run():
    unittest.TextTestRunner(verbosity=1).run(ai_lib_t.suite)
    unittest.TextTestRunner(verbosity=1).run(actor_t.suite)
    unittest.TextTestRunner(verbosity=1).run(vector_t.suite)
    unittest.TextTestRunner(verbosity=1).run(geometry_t.suite)
    # unittest.TextTestRunner(verbosity=1).run(battle_t.suite)
    unittest.TextTestRunner(verbosity=1).run(math_lib_t.suite)
    unittest.TextTestRunner(verbosity=1).run(screen_lib_t.suite)
    unittest.TextTestRunner(verbosity=1).run(object_base_t.suite)
