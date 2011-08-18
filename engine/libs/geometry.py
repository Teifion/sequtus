from __future__ import division
import pygame
import math
import vectors

def _convert(r):
    # Takes a pos, pos, size, size rect and returns a pos, pos, pos, pos rect
    return (r[0], r[1], r[2] + r[0], r[3] + r[1])

# 2D Function
def rect_collision(r1, r2, convert=False):
    """
    r1 and r2 are 4 length sequences of (left, top, right, bottom)
    or at least something that can be used as such.
    
    If the convert flag is set then the function assumes the rects are
    position and size and converts them to position and position pairs.
    """
    
    if convert:
        if type(r1) == tuple or type(r1) == list:
            r1 = _convert(r1)
        else:
            r1 = (r1.left, r1.top, r1.right, r1.bottom)
        
        if type(r2) == tuple or type(r2) == list:
            r2 = _convert(r2)
        else:
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

# 2D Function
def inside_angles(a1, a2):
    """Takes two pairs and calculates the inside angles of A and B.
    Each pair is the position and angle towards C.
    """
    
    # Get the angles for point to point, using these we can
    # calculate the inside angles
    AC = a1[1][0]
    BC = a2[1][0]
    
    # Convert positions into angles
    AB = vectors.angle(a1[0], a2[0])[0]
    BA = vectors.angle(a2[0], a1[0])[0]
    
    # A
    if abs(AC - AB) > 180:
        if AC > AB:
            A = (360 - AC) + AB
        else:
            A = (360 - AB) + AC
    elif AB > AC:
        A = AB - AC
    else:
        A = AC - AB
    
    # B
    if abs(BC - BA) > 180:
        if BC > BA:
            B = (360 - BC) + BA
        else:
            B = (360 - BA) + BC
    elif BA > BC:
        B = BA - BC
    else:
        B = BC - BA
    
    # C
    C = 180 - A - B
    
    return A, B, C

# 2D Function
def rect_collision_distance(a1, a2, testing=False):
    """
    Returns a pair of distances moving a1 and a2 to the point of collision
    when testing is set to true it will return the internal variables used
    to ensure that all parts of the function are working correctly.
    
    Each argument is assumed to be the angle of position and movement
    for each actor.
    
    We have a triangle of A, B and C where A and B are the two actors
    and C is the point of collision. a, b and c are the edges opposite
    their respective angle.
    
    Our first problem is to find A and B. We have Angle to C and Angle to A/B
    to start with and can work out the inside angle from those.
    """
    
    # Calcuate angles
    A, B, C = inside_angles(a1, a2)
    
    # Now for the sides, we can start with c using just pythagoras
    c = vectors.distance(a1[0], a2[0])
    
    try:
        a = c/math.sin(math.radians(C)) * math.sin(math.radians(A))
        b = c/math.sin(math.radians(C)) * math.sin(math.radians(B))
    except Exception as e:
        print("a1 = %s" % a1)
        print("a2 = %s" % a2)
        print("A: %s, B: %s, C: %s" % (A, B, C))
        raise
    
    if testing:
        return A, B, C, a, b, c
    else:
        return a, b
    
