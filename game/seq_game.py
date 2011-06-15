import json
import math
import random
import time

import pygame

from engine import engine
from game import image_composition
from game_screens import main_menu, game_setup

class Sequtus (engine.EngineV3):
    name = "Sequtus"
    
    fps = 30
    
    menu_width = 470
    
    window_width = 1000
    window_height = 1000
    
    def __init__(self):
        super(Sequtus, self).__init__()
        
        self.images = {
            "background":     image_composition.starfield(),
        }
    
    def startup(self):
        super(Sequtus, self).startup()
        
        self.screens['Main menu'] = main_menu.build(self)
        self.screens['Game setup'] = game_setup.build(self)
        
        self.set_screen('Main menu')
    
    def game_logic(self):
        pass
    