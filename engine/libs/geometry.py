from __future__ import division
import pygame
import math
import vectors

def rect_collision(r1, r2, convert=False):
    """
    r1 and r2 are 4 length sequences of (left, top, right, bottom)
    or at least something that can be used as such.
    
    If the convert flag is set then the function assumes the rects are
    position and size and converts them to position and position pairs.
    """
    
    if convert:
        r1 = (r1.left, r1.top, r1.right, r1.bottom)
        r2 = (r2.left, r2.top, r2.right, r2.bottom)
    
    left1, top1, right1, bottom1 = r1
    left2, top2, right2, bottom2 = r2
    
    # Horrizontal
    if right1 < left2: return False
    if left1 > right2: return False
    
    # Vertical
    if bottom1 < top2: return False
    if top1 > bottom2: return False
    
    return True

def rect_collision_angle(a1, a2, convert=False):
    """
    each argument is assumed to be the angle of position and movement
    for each actor, if convert is called as true then it is assumed that
    the arguments are velocities and need to be converted into angles.
    """
    
    if convert:
        a1 = a1.pos, vectors.angle([0,0,0], a1.velocity)
        a2 = a2.pos, vectors.angle([0,0,0], a2.velocity)
    
    pos1, angle1 = a1
    pos2, angle2 = a2
    
    angle_1_to_2 = vectors.angle(pos1, pos2)
    angle_2_to_1 = vectors.angle(pos2, pos1)
    
    # This is not the correct answer
    return 180 - angle_1_to_2 - angle_2_to_1