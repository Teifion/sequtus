import pygame

from engine import battle_screen, controls

from game import image_composition

class Battle (battle_screen.BattleScreen):
    def __init__(self, seq_game):
        super(Battle, self).__init__()
        self.engine = seq_game
        
        self.name = "Sequtus"
        
        self.background_image = seq_game.images['battlefield'].copy()
    
    def update(self):
        pass
    
    def handle_keyhold(self):
        # Up arrow
        if 273 in self.keys_down: self.scroll_y -= 10
        
        # Down arrow
        if 274 in self.keys_down: self.scroll_y += 10
        
        # Right arrow
        if 275 in self.keys_down: self.scroll_x += 10
        
        # Left arrow
        if 276 in self.keys_down: self.scroll_x -= 10
    