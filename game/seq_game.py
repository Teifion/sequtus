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
            
            "9px_bullet":               pygame.image.load('media/9px_bullet.png'),
            "11px_bullet":              pygame.image.load('media/11px_bullet.png'),
            "15px_bullet":              pygame.image.load('media/15px_bullet.png'),
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
        self.current_screen.player_team = 1
        
        self.current_screen.load_all("data/config.json", "data/game_data.json", "data/dummy.json")
        # self.current_screen.load_all("data/config.json", "data/game_data.json", "engine/test_lib/battle_test_setups/collisions.json")
        
        self.current_screen.add_order(0, "move", [100, 800])
        self.current_screen.add_order(1, "move", [200, 800])
        self.current_screen.add_order(2, "move", [300, 800])
        self.current_screen.add_order(3, "move", [100, 900])
        self.current_screen.add_order(4, "move", [200, 900])
        self.current_screen.add_order(5, "move", [300, 900])
        
        self.current_screen.add_order(6, "move", [200, 600])
        self.current_screen.add_order(7, "move", [200, 700])
        self.current_screen.add_order(8, "move", [200, 800])
        self.current_screen.add_order(9, "move", [300, 600])
        self.current_screen.add_order(10, "move", [300, 700])
        self.current_screen.add_order(11, "move", [300, 800])
        
        for i in range(0, 5):
            for j in range(0, 5):
                self.current_screen.place_actor({"type":"Red circle","pos":[i*50, j*50,0],"team":1,"completion":100,"hp":10})
                self.current_screen.add_order(len(self.current_screen.actors)-1, "move", [400, 1000])
        
        for i in range(0, 5):
            for j in range(0, 5):
                self.current_screen.place_actor({"type":"Blue circle","pos":[i*50+500, j*50+500,0],"team":2,"completion":100,"hp":10})
                self.current_screen.add_order(len(self.current_screen.actors)-1, "move", [100, 700])
        
        self.current_screen.set_speed(30)
