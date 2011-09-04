"""
Manually alter it to try several variations of the same function and see which is fastest
"""

import time
import sys

from profile_lib.autoprofiler import ProfilerEngine

from engine.libs import cli

def setup():
    p = ProfilerEngine()
    p.startup()
    
    for i in range(0, 1000):
        p.current_screen.place_actor({"type":"Blue circle","pos":[i*30, 100, 0],"team":1,"completion":100,"hp":1})
    
    return p

def _run_func(f, args, kwargs):
    p = setup()
    this_func = getattr(p.current_screen, f)
    
    start_time = time.time()
    for i in range(0, 100):
        this_func(*args, **kwargs)
    
    return time.time() - start_time

def compare():
    funcs = (("get_collisions", [], {}), ("get_collisions2", [], {}))
    results = {}
    
    # Run functions
    for f, args, kwargs in funcs:
        results[f] = _run_func(f, args, kwargs)
    
    # Print results
    for f, t in results.items():
        print(f, t)
        
