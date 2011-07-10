# import pygame

# from engine import battle_screen, controls, actors
# from game import image_composition
# from game.battle_lib import battle_sim

# class Dummy (actors.Actor):
#     def __init__(self, screen, position=[0,0], velocity=[0,0]):
#         super(Dummy, self).__init__(screen, position, velocity)

# class Battle (battle_screen.BattleScreen):
#     def __init__(self, seq_game, sim):
#         super(Battle, self).__init__((seq_game.window_width, seq_game.window_height), sim)
#         self.engine = seq_game
#         
#         self.scroll_boundaries = (seq_game.window_width-2000, seq_game.window_height-2000, 0, 0)
#         
#         self.name = "Sequtus"
#         
#         self.background_image = seq_game.images['battlefield'].copy()
#         
#         self.bs = battle_sim.BattleSim(self)
#     
#     def update(self):
#         super(Battle, self).update()
#         
#         for i, s in enumerate(self.actors):
#             if i == 0:
#                 s.rect.top += 1
#     
#     def handle_keyhold(self):
#         super(Battle, self).handle_keyhold()
#     
#     def activate(self):
#         dummy = actors.Actor(self)
#         dummy.new_image(pygame.image.load('media/red_rune.png').copy())
#         dummy.selector_image = pygame.image.load('media/selector.png').copy()
#         dummy.selector_size = 50, 50
#         dummy.selector_offset = 5, 5
#         dummy.pos = 450, 450
#         self.add_actor(dummy)
#         
#         dummy.hp = 7
#         self.select_actor(dummy)
#         
#         dummy = actors.Actor(self)
#         dummy.new_image(pygame.image.load('media/blue_rune.png').copy())
#         dummy.selector_image = pygame.image.load('media/selector.png').copy()
#         dummy.selector_size = 50, 50
#         dummy.selector_offset = 5, 5
#         dummy.pos = 500, 500
#         
#         dummy.hp = 9
#         
#         self.add_actor(dummy)
#         
#         self.scroll_right(rate=10)
#         self.scroll_down(rate=10)