import pygame

from engine.logic import battle_sim
from engine.render import panels

class Battle (battle_sim.BattleSim):
    def __init__(self, engine):
        super(Battle, self).__init__(engine)
        
        self.panels["build"] = panels.TabularMenu(engine,
            size = (200, engine.window_height-200),
            grid_size = (100, 100),
            position = (engine.window_width - 200, 200)
        )
        
        self.panels["minimap"] = panels.MiniMap(engine,
            size = (200, 200),
            position = (engine.window_width - 200, 0)
        )
        
        self.rebuild_build_menu()
    
    def rebuild_build_menu(self):
        buttons = []
        
        if self.actor_types == {}:
            return
        
        buttons.append(("red_building_menu", self.place_actor_mode, [self.actor_types["Red building"]]))
        buttons.append(("blue_building_menu", self.place_actor_mode, [self.actor_types["Blue building"]]))
        
        self.panels["build"].buttons = buttons
        self.panels["build"].changed = True
    
    def selection_changed(self):
        self.rebuild_build_menu()
        
