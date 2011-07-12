import json
import math
import random
import time

import sys
import pygame

from engine.render import core
from engine.logic import battle_sim
from game import image_composition, seq_sim
from game_screens import main_menu, game_setup, battle

import json

class Sequtus (core.EngineV3):
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
            "red_rune":         pygame.image.load('media/red_rune.png'),
            "blue_rune":        pygame.image.load('media/blue_rune.png'),
        }
    
    def startup(self):
        super(Sequtus, self).startup()
        
        self.screens['Main menu'] = main_menu.MainMenu(self)
        self.screens['Game setup'] = game_setup.build(self)
        self.screens['Battle screen'] = battle.Battle
        
        self.set_screen('Main menu')
        self.new_game()
    
    def new_game(self, file_path=""):
        if file_path == "":
            file_path = "%s/data/dummy.json" % sys.path[0]
        
        with open(file_path) as f:
            sim_data = json.loads(f.read())
        
        self.set_screen('Battle screen')
        
        self.current_screen.name = "Sequtus"
        self.current_screen.scroll_boundaries = (self.window_width-2000, self.window_height-2000, 0, 0)
        self.current_screen.background_image = self.images['battlefield'].copy()
        
        self.current_screen.load(sim_data)
        self.current_screen.select_actor(self.current_screen.actors[0])
        
