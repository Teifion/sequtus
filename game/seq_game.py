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
    
    window_width = 1000
    window_height = 1000
    
    def __init__(self):
        super(Sequtus, self).__init__()
        
        self.images = {
            "background":       image_composition.starfield(),
            
            "battlefield":      pygame.image.load('media/battlefield.png'),
            
            "red_rune":         pygame.image.load('media/red_rune.png'),
            "blue_rune":        pygame.image.load('media/blue_rune.png'),
            
            "red_building_menu":      pygame.image.load('media/red_building_menu.png'),
            "blue_building_menu":     pygame.image.load('media/blue_building_menu.png'),
            
            "red_building":         pygame.image.load('media/red_building.png'),
            "blue_building":        pygame.image.load('media/blue_building.png'),
            
            "red_building_placement":       pygame.image.load('media/red_building_placement.png'),
            "blue_building_placement":      pygame.image.load('media/blue_building_placement.png'),
        }
    
    def startup(self):
        super(Sequtus, self).startup()
        
        self.screens['Main menu'] = main_menu.MainMenu(self)
        self.screens['Game setup'] = game_setup.build(self)
        self.screens['Battle screen'] = battle.Battle
        
        self.set_screen('Main menu')
        self.new_game()
    
    def new_game(self, file_path=""):
        self.set_screen('Battle screen')
        
        self.current_screen.name = "Sequtus"
        self.current_screen.scroll_boundaries = (self.window_width-2000, self.window_height-2000, 0, 0)
        self.current_screen.background_image = self.images['battlefield'].copy()
        
        # self.current_screen.load_all("data/config.json", "data/game_data.json", "data/dummy.json")
        self.current_screen.load_all("data/config.json", "data/game_data.json", "engine/test_lib/battle_test_setups/collisions.json")
        
        self.current_screen.actors[0].issue_command("move", [200, 200])
        self.current_screen.actors[1].issue_command("move", [200, 200])
        
        self.current_screen.actors[2].issue_command("move", [400, 100])
        self.current_screen.actors[3].issue_command("move", [400, 100])
        
