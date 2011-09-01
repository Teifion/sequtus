from __future__ import division
import math

# Thought I would need these, turns out I don't (yet)
# """
# http://en.wikipedia.org/wiki/Equations_of_motion
# http://www.youtube.com/watch?v=hD0ineZXpcw&feature=related
# 1) d = ((v1 + v2)/2) * t
# 2) v2 = (v1 + a * t)
# 3) d = (v1 * t + (a * t^2)/2)
# 4) d = (v2 * t - (a * t^2)/2)
# 5) v2^2 = v1^2 + 2 * a * d
# """
# 
# def suvat(wanted, a = None, v1 = None, v2 = None, d = None, t = None):
#     if wanted == "v1":
#         pass
#     else:
#         raise Exception("No handler for wanted option of '%s', possible options are ['a', 'v1', 'v2', 'd', 't']" % wanted)
    
def calc_trajectory(gravity, target_distance, velocity, initial_height=0):
    """Gravity refers to the speed at which the projectile will
    accelerate downwards.
    target_distance is the distance that we wish to travel
    velocity is the speed at which we move towards our target
    
    V = DG/2"""
    
    steps_to_target = target_distance/velocity
    
    if initial_height == 0:
        return (steps_to_target * gravity)/2
    else:
        raise Exception("Not implemented where initial_height is non-zero")
        # return (2 * target_distance/velocity) - X