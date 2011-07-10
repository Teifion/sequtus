import pygame

from engine.render import screen, controls

from game import image_composition

def p_func(*args):
    for a in args:
        print(a)

def background(buttons):
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

def build(seq_game):
    s = screen.Screen((seq_game.window_width, seq_game.window_height))
    
    buttons = (
        ("Start game",  seq_game.set_screen,    ["Battle screen"]),
        ("Back",        seq_game.set_screen,    ["Main menu"]),
    )
    
    s.name = "Quick start"
    s.background = background(buttons)
    
    i = -1
    for b_text, b_func, b_args in buttons:
        i += 1
        
        c = controls.InvisibleButton((300, 110 + i*60), (400, 40))
        
        c.button_up = b_func
        c.button_up_args = b_args
        
        s.add_button(c)
    
    return s