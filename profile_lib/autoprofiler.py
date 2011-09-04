"""
A set of functions and setups to profile the code using time taken. Alter
the code and re-run the autoprofiler and compare results.
"""

import time
import sys

from game import seq_game
from game.game_screens import battle

from engine.libs import cli

class ProfilerBattle (battle.Battle):
    def __init__(self, *args, **kwargs):
        super(ProfilerBattle, self).__init__(*args, **kwargs)
        self.max_age = 1000
        self.age = 0
    
    def logic_cycle(self):
        if self.tick > self.max_age:
            raise StopIteration("")
        
        super(ProfilerBattle, self).logic_cycle()

class ProfilerEngine (seq_game.Sequtus):
    def __init__(self, *args, **kwargs):
        super(ProfilerEngine, self).__init__(*args, **kwargs)
        
        self.images['test_image_100'] = self.images['red_building']
        self.images['test_image_41'] = self.images['red_rune']
    
    def startup(self):
        # The Sequtus implimentation has stuff we want to skip
        super(seq_game.Sequtus, self).startup()
        
        self.screens['main'] = ProfilerBattle
        self.set_screen('main')
        
        self.current_screen.load_all(
            "%s/engine/test_lib/battle_test_setups/config.json" % sys.path[0],
            "%s/engine/test_lib/battle_test_setups/game_data.json" % sys.path[0],
            "%s/engine/test_lib/battle_test_setups/empty_game.json" % sys.path[0],
            local=False,
        )
        
def _profile(p, name, iterations, *args, **kwargs):
    start_time = time.time()
    
    for i in cli.progressbar(range(0, iterations), "%s: " % name, 60):
        p(*args, **kwargs)
    
    return round(time.time() - start_time, 2)

def no_collision_test():
    p = ProfilerEngine()
    p.startup()
    
    # No overlapping
    for i in range(0, 300):
        p.current_screen.place_actor({"type":"Blue circle","pos":[i*100, 100, 0],"team":1,"completion":100,"hp":1})
    
    return "No collisions", _profile(p.current_screen.get_collisions, "No collisions", 250)

def pair_collision_test():
    p = ProfilerEngine()
    p.startup()
    
    # Overlapping with the one either side
    for i in range(0, 300):
        p.current_screen.place_actor({"type":"Blue circle","pos":[i*30, 100, 0],"team":1,"completion":100,"hp":1})
    
    return "Pair collisions", _profile(p.current_screen.get_collisions, "Pair collisions", 250)

def all_collision_test():
    p = ProfilerEngine()
    p.startup()
    
    # All in the same spot
    for i in range(0, 300):
        p.current_screen.place_actor({"type":"Blue circle","pos":[100, 100, 0],"team":1,"completion":100,"hp":1})
    
    return "All collisions", _profile(p.current_screen.get_collisions, "All collisions", 250)

def mass_no_collision_test():
    p = ProfilerEngine()
    p.startup()
    
    # All in the same spot
    for i in range(0, 1000):
        p.current_screen.place_actor({"type":"Blue circle","pos":[i*100, 100, 0],"team":1,"completion":100,"hp":1})
    
    return "Mass no collisions", _profile(p.current_screen.get_collisions, "Mass no collisions", 30)

def mass_pair_collision_test():
    p = ProfilerEngine()
    p.startup()
    
    # All in the same spot
    for i in range(0, 1000):
        p.current_screen.place_actor({"type":"Blue circle","pos":[i*30, 100, 0],"team":1,"completion":100,"hp":1})
    
    return "Mass pair collisions", _profile(p.current_screen.get_collisions, "Mass pair collisions", 30)

def mass_all_collision_test():
    p = ProfilerEngine()
    p.startup()
    
    # All in the same spot
    for i in range(0, 1000):
        p.current_screen.place_actor({"type":"Blue circle","pos":[100, 100, 0],"team":1,"completion":100,"hp":1})
    
    return "Mass all collisions", _profile(p.current_screen.get_collisions, "Mass all collisions", 30)

profilers = (
    # Collisions
    no_collision_test, pair_collision_test, all_collision_test,
    
    # Mass collisions
    mass_no_collision_test, mass_pair_collision_test, mass_all_collision_test,
)

def run():
    results = {}
    
    # Run functions
    for p in profilers:
        f,t = p()
        
        results[f] = t
    
    # Print results
    print("\n\n-----------\n\n")
    print("Collisions: %s" % sum((
        results["No collisions"],
        results["Pair collisions"],
        results["All collisions"],
    )))
    print("Mass collisions: %s" % sum((
        results["Mass no collisions"],
        results["Mass pair collisions"],
        results["Mass all collisions"],
    )))
