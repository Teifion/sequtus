from __future__ import division
import pygame
import math

def rect_collision(r1, r2, convert=False):
    """
    r1 and r2 are 4 length sequences of (left, top, right, bottom)
    or at least something that can be used as such.
    
    If the convert flag is set then the function assumes the rects are
    position and size and converts them to position and position pairs.
    """
    
    if convert: r1 = (r1.left, r1.top, r1.right, r1.bottom)
    if convert: r2 = (r2.left, r2.top, r2.right, r2.bottom)
    
    left1, top1, right1, bottom1 = r1
    left2, top2, right2, bottom2 = r2
    
    # Horrizontal
    if right1 < left2: print("A"); return False
    if left1 > right2: print("B"); return False
    
    # Vertical
    if bottom1 < top2: print("C"); return False
    if top1 > bottom2: print("D"); return False
    
    return True
