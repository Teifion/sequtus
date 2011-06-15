import pygame

def starfield():
    s = pygame.Surface((400, 400))
    
    r = s.fill((255, 100, 100), pygame.Rect(0, 0, 100, 100))
    
    return s
