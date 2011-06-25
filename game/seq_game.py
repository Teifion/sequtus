import json
import math
import random
import time

import pygame

from engine import engine
from game import image_composition
from game_screens import main_menu, game_setup, battle

class Sequtus (engine.EngineV3):
    name = "Sequtus"
    
    fps = 30
    
    menu_width = 470
    
    window_width = 1000
    window_height = 1000
    
    def __init__(self):
        super(Sequtus, self).__init__()
        
        self.images = {
            "background":       image_composition.starfield(),
            
            "battlefield":      pygame.image.load('media/battlefield.png'),
        }
    
    def startup(self):
        super(Sequtus, self).startup()
        
        self.screens['Main menu'] = main_menu.MainMenu(self)
        self.screens['Game setup'] = game_setup.build(self)
        self.screens['Battle screen'] = battle.Battle
        
        # self.set_screen('Main menu')
        self.set_screen('Battle screen')
    
