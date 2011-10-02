from engine.render import screen

class GameDataEditor (screen.Screen):
    """A utility to make managing game data files easier"""
    
    def __init__(self, game_engine):
        super(GameDataEditor, self).__init__((game_engine.window_width, game_engine.window_height))
        
        # self.engine = seq_game
        # 
        # buttons = (
        #     ("Quick start", seq_game.new_game,    []),
        #     # ("Campaign",    None,   []),
        #     ("Quit",        seq_game.quit, []),
        # )
        # 
        # self.name = "Sequtus main menu"
        # self.background_image = make_bg_image(buttons)
        # 
        # i = -1
        # for b_text, b_func, b_args in buttons:
        #     i += 1
        #     
        #     c = controls.InvisibleButton((300, 110 + i*60), (400, 40))
        #     
        #     c.button_up = b_func
        #     c.button_up_args = b_args
        #     
        #     self.add_button(c)
