import pygame

from engine import screen, controls

from game import image_composition

def make_bg_image(buttons):
    s = pygame.Surface((1000, 1000))
    
    r = s.fill((100, 100, 100), pygame.Rect(200, 100, 600, 800))
    
    # Draw on buttons
    i = -1
    for b_text, b_func, b_args in buttons:
        i += 1
        
        # Test for invisible buttons
        # r = s.fill((100, 0, 0), pygame.Rect(300, 110 + i*60, 400, 40))
        
        # Centre the text
        font_obj = pygame.font.SysFont("Helvetica", 24)
        left_margin = (600 - font_obj.size(b_text)[0])/2
        button_pos = (200 + left_margin, 120 + i*60)
        
        controls.draw_text(s, b_text, button_pos, colour=(255,255,255), font_obj = font_obj)
    
    return s

class MainMenu (screen.Screen):
    def __init__(self, seq_game):
        super(MainMenu, self).__init__()
        self.engine = seq_game
        
        buttons = (
            ("Quick start", seq_game.set_screen,    ["Battle screen"]),
            # ("Campaign",    None,   []),
            ("Quit",        seq_game.quit, []),
        )
        
        self.name = "Sequtus main menu"
        self.background_image = make_bg_image(buttons)
        
        i = -1
        for b_text, b_func, b_args in buttons:
            i += 1
            
            c = controls.InvisibleButton((300, 110 + i*60), (400, 40))
            
            c.button_up = b_func
            c.button_up_args = b_args
            
            self.add_button(c)
    
    def update(self):
        pass