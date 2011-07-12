import pygame

from engine.logic import battle_sim
from engine.render import panels

class Battle (battle_sim.BattleSim):
    def __init__(self, engine):
        super(Battle, self).__init__(engine)
        
        self.panels["build"] = panels.TabularMenu(self,
            size = (200, engine.window_height-200),
            grid_size = (100, 100),
            position = (engine.window_width - 200, 200)
        )
        
        self.panels["minimap"] = panels.MiniMap(self,
            size = (200, 200),
            position = (engine.window_width - 200, 0)
        )
    
    def rebuild_build_menu(self):
        # image_name, callback, args in self.buttons
        buttons = []
        
        
        
        self.panels["build"].buttons = buttons
        self.panels["build"].changed = True
    
    def selection_changed(self):
        # Allows us to re-build the panels
        
        pass
    
