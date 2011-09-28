from __future__ import division

import pygame

import math

def set_fps(screen, fps):
    screen._redraw_delay = 1/fps

def get_facing_angle(angle, facings=36):
    """Takes an angle and gives the 'rounded' result"""
    angle_per_facing = 360/facings
    
    return int(math.floor(angle/angle_per_facing) * angle_per_facing)

def make_rotated_image(image, angle):
    return pygame.transform.rotate(image, -angle)

keyboards = {
    "colemak-qwerty": {
        "q": "q",
        "w": "w",
        "f": "e",
        "p": "r",
        "g": "t",
        "j": "y",
        "l": "u",
        "u": "i",
        "y": "o",
        ";": "p",
          
        "a": "a",
        "r": "s",
        "s": "d",
        "t": "f",
        "d": "g",
        "h": "h",
        "n": "j",
        "e": "k",
        "i": "l",
          
        "z": "z",
        "x": "x",
        "c": "c",
        "v": "v",
        "b": "b",
        "k": "n",
        "m": "m",
    }
}

# Make reverse dictionaries
keys = keyboards.keys()
for k in keys:
    a,b = k.split("-")
    new_key = "%s-%s" % (b,a)
    
    keyboards[new_key] = {}
    
    for k1, k2 in keyboards[k].items():
        keyboards[new_key][k2] = k1

    

def translate_keyboard(from_keyboard, to_keyboard, key):
    """User input is the from_keyboard, translating to the to_keyboard
    which we will then use."""
    
    d = "%s-%s" % (from_keyboard, to_keyboard)
    
    if d not in keyboards:
        raise KeyError("Keyboard mapping %s does not exist in the lookup table" % d)
    
    k = keyboards[d]
    
    # Lowercase first
    if key in k:
        return k[key]
    
    # It may be an uppercase character
    elif key.lower() in k:
        return k[key.lower()].upper()
    
    # Not in the list, it's assumed it matches the same
    return key
