import pygame

import unittest
import traceback
import time
import sys

from engine.render import core
from engine.logic import battle_sim

"""
This module is designed to run black-box testing on the application's
main code base. Many parts of the game may be data-dependant and hard
to test in complete isolation. This module will take data and run the
simulation for a set number of cycles and then pass the result back to
the caller so that checks on the data can be performed.
"""

class TestEngine (core.EngineV3):
    name = "Sequtus test engine"
    fps = 100000
    window_width = 100
    window_height = 100
    
    def __init__(self):
        super(TestEngine, self).__init__()
        self.images = {
            "test_image_41":pygame.Surface((41, 41)),
            "test_image_100":pygame.Surface((100, 100))
        }

class BattleTester (battle_sim.BattleSim):
    def __init__(self, engine):
        super(BattleTester, self).__init__(engine)
        
        self.set_speed(10000)
        self.cycles = 0
        self.max_cycles = 0
        self.testing = True
    
    # We never actually want to draw anything, it's a waste of time
    def redraw(self):
        pass
    
    def run(self, max_cycles=-1, print_debug_info=True):
        if max_cycles > 0:
            self.max_cycles += max_cycles
        
        while self.cycles < self.max_cycles:
            self.cycles += 1
            
            try:
                self.logic_cycle()
            except Exception as e:
                if print_debug_info:
                    self.data_dump()
                raise

class SimTester (unittest.TestCase):
    data = ""
    
    def __init__(self, *args, **kwargs):
        super(SimTester, self).__init__(*args, **kwargs)
    
    def new_sim(self, max_cycles=0, game_state="default_state.json", config="config.json", game_data="game_data.json"):
        e = TestEngine()
        s = BattleTester(e)
        s.max_cycles = max_cycles
        s.engine = e
        
        base_path = "%s/engine/test_lib/battle_test_setups" % sys.path[0]
        
        s.load_all(
            config_path = "%s/%s" % (base_path, config),
            setup_path = "%s/%s" % (base_path, game_data),
            game_path = "%s/%s" % (base_path, game_state),
            local = False
        )
        
        
        return s
        
