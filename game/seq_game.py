import json
import math
import random
import time

import sys
import pygame

from engine.render import core
from engine.logic import battle_sim
from engine.libs import sim_lib
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
            "battlefield":      core.Animation('media/battlefield.png'),
            
            "red_rune":         core.Animation("media/red_rune_anim.png", 9, 1),
            "red_rune_menu":         core.Animation('media/red_rune_menu.png'),
            
            "red_square":       core.Animation('media/red_square.png'),
            "red_square_menu":       core.Animation('media/red_square_menu.png'),
            
            "blue_rune":        core.Animation('media/blue_rune_anim.png', 3, 3, 0.2),
            
            "red_building_menu":      core.Animation('media/red_building_menu.png'),
            "blue_building_menu":     core.Animation('media/blue_building_menu.png'),
            
            "red_building":         core.Animation('media/red_building.png'),
            "blue_building":        core.Animation('media/blue_building.png'),
            
            "red_building_placement":       core.Animation('media/red_building_placement.png'),
            "blue_building_placement":      core.Animation('media/blue_building_placement.png'),
            
            "9px_bullet":               core.Animation('media/9px_bullet.png'),
            "11px_bullet":              core.Animation('media/11px_bullet.png'),
            "15px_bullet":              core.Animation('media/15px_bullet.png'),
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
        self.current_screen.background_image = self.images['battlefield'].get().copy()
        self.current_screen.player_team = 1
        
        self.current_screen.load_all("data/config.json", "data/game_data.json", "data/dummy.json")
        # self.current_screen.load_all("data/config.json", "data/game_data.json", "engine/test_lib/battle_test_setups/collisions.json")
        
        # self.current_screen.select_actor(self.current_screen.actors[0])
        # self.current_screen.queue_order(0, "aid", target=self.current_screen.actors[1])
        # self.current_screen.queue_order(0, "aid", target=self.current_screen.actors[2])
        
        sim_lib.set_speed(self.current_screen, 30)
