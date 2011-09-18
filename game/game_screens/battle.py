import pygame

from engine.logic import battle_sim
from engine.render import panels

class Battle (battle_sim.BattleSim):
    def __init__(self, engine):
        super(Battle, self).__init__(engine)
        
        self.panels["build"] = panels.TabularMenu(engine,
            screen = self,
            size = (200, engine.window_height-200),
            grid_size = (100, 100),
            position = (0, 200),
        )
        
        self.panels["minimap"] = panels.MiniMap(engine,
            size = (200, 200),
            map_size = (2000, 2000),
            position = (0, 0)
        )
        
        self.panels["resources"] = panels.InfoBox(engine,
            size = (engine.window_width - 200, 50),
            position = (200, 0),
            fill_colour = (0,0,50),
        )
        
        # May not be needed
        # self.panels["unit_info"] = panels.InfoBox(engine,
        #     size = (engine.window_width - 200, 75),
        #     position = (0, engine.window_height - 75),
        #     fill_colour = (0,0,0),
        # )
        
        self.rebuild_build_menu()
        
        self.draw_area = (200, 50, engine.window_width, engine.window_height)
        
        self.post_init()
    
    def logic_cycle(self):
        super(Battle, self).logic_cycle()
        
        if self.signal_menu_rebuild:
            self.rebuild_build_menu()
            self.signal_menu_rebuild = False
            
    
    def rebuild_build_menu(self):
        if self.actor_types == {}:
            return
        
        self.panels["build"].build_from_actor_list()
    
    def selection_changed(self):
        self.rebuild_build_menu()
        
