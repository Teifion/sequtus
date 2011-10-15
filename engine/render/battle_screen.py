from __future__ import division

"""
BattleScreen is a screen with added functionality for handling things such as
scrolling all of it's information comes from the sim that it connects to
none of the game logic is implemented in the battle_screen at all.

The screen is also used to read in commands such as mouse-clicks.
BattleScreen itself is subclassed by BattleSim so as to keep the logic
code separate from the display/interface code.
"""

import time
import weakref

import pygame
from pygame.locals import *

from engine.render import battle_io
from engine.libs import screen_lib, actor_lib, vectors

class BattleScreen (battle_io.BattleIO):
    self_regulate = True
    player_team = None
    facings = 360/4# The number of different angles we'll draw
    
    def __init__(self, engine):
        super(BattleScreen, self).__init__(engine)
        
        self.image_cache = {}
        
        # Defaults to drawing to the screen sizes, this gets overriden later
        # it's used to work out what size rectangle to draw to for the
        # battlefield (so taking into account panels and menus)
        self.draw_area = (0, 0, engine.window_width, engine.window_height)
        
        # The margins that are used for things like menus and panels, we don't
        # want to draw battlefield stuff to these
        self.draw_margin = [0, 0]
        
        self.background_image = pygame.Surface((1,1))
        self.background = pygame.Surface((1,1))
        
        self.selected_actors = []
        
        self._next_redraw = time.time()
        self._redraw_delay = 0
        screen_lib.set_fps(self, 40)
        
        self.terrain = {}
        self.bullets = []
        self.effects = []
        
        self.place_image = None
        self.panels = {}
        
        self.redraw_count = [0, 0]
        self._current_actor_id = 0
        
        # This is switched instead of a function call because it's possible
        # that we may alter the selection several times in a row and it would
        # be a waste to rebuild menus several times
        self._selection_has_changed = False
    
    def post_init(self):
        self.draw_margin = [self.scroll_x + self.draw_area[0], self.scroll_y + self.draw_area[1]]
    
    def redraw(self):
        """Overrides the basic redraw as it's intended to be used with more animation"""
        if time.time() < self._next_redraw:
            return
        
        if self._selection_has_changed:
            self.selection_changed()
            self._selection_has_changed = False
        
        if int(time.time()) != self.redraw_count[1]:
            # print("FPS: %s" % self.redraw_count[0])
            self.redraw_count = [0, int(time.time())]
        
        # Draw background taking into account scroll
        surf = self.engine.display
        surf.blit(self.background_image, pygame.Rect(
            self.draw_margin[0], self.draw_margin[1],
            self.draw_area[2], self.draw_area[3],
        ))
        
        # Actors
        for a in self.actors:
            rounded_facing = screen_lib.get_facing_angle(a.facing[0], self.facings)
            
            a.frame += 1
            img_name = "%s_%s_%s" % (
                a.image,
                self.engine.images[a.image].real_frame(a.frame),
                rounded_facing
            )
            
            if img_name not in self.image_cache:
                self.image_cache[img_name] = screen_lib.make_rotated_image(
                    image = self.engine.images[a.image].get(a.frame),
                    angle = rounded_facing
                )
            
            # Get the actor's image and rectangle
            actor_img = self.image_cache[img_name]
            r = pygame.Rect(actor_img.get_rect())
            r.left = a.pos[0] + self.draw_margin[0] - r.width/2
            r.top = a.pos[1] + self.draw_margin[1] - r.height/2
            
            # Only draw actors within the screen
            if r.right > self.draw_area[0] and r.left < self.draw_area[2]:
                if r.bottom > self.draw_area[1] and r.top < self.draw_area[3]:
                    surf.blit(actor_img, r)
                    
                    # Abilities
                    for ab in a.abilities:
                        if ab.image != None:
                            # First we want to get the image
                            ab_rounded_facing = screen_lib.get_facing_angle(ab.facing[0], self.facings)
                            ab_img_name = "%s_%s_%s" % (
                                ab.image,
                                self.engine.images[ab.image].real_frame(a.frame),
                                ab_rounded_facing
                            )
                            
                            if ab_img_name not in self.image_cache:
                                self.image_cache[ab_img_name] = screen_lib.make_rotated_image(
                                    image = self.engine.images[ab.image].get(a.frame),
                                    angle = ab_rounded_facing
                                )
                            
                            # We now need to work out our relative coordinates
                            rel_pos = ab.get_offset_pos()
                            
                            # Now we actually draw it
                            centre_offset = self.engine.images[ab.image].get_rotated_offset(ab_rounded_facing)
                            ability_img = self.image_cache[ab_img_name]
                            r = pygame.Rect(ability_img.get_rect())
                            r.left = a.pos[0] + self.draw_margin[0] - r.width/2 + centre_offset[0] + rel_pos[0]
                            r.top = a.pos[1] + self.draw_margin[1] - r.height/2 + centre_offset[1] + rel_pos[1]
                            surf.blit(ability_img, r)
                    
                    # Selection box?
                    if a.selected:
                        """Removed selection boxes for now as I'm not sure how I want them to work
                        with rotated actors"""
                        # selection_r = pygame.transform.rotate(a.selection_rect(), -rounded_facing)
                        # pygame.draw.rect(surf, (255, 255, 255), selection_r, 1)
                        
                        surf.blit(*a.health_bar(self.draw_margin[0], self.draw_margin[1]))
                        
                    # Draw completion box anyway
                    if a.completion < 100:
                        surf.blit(*a.completion_bar(self.draw_margin[0], self.draw_margin[1]))
            
            # Pass effects from the actor to the battle screen
            # this means that if the actor dies the effect still lives on
            while len(a.effects) > 0:
                self.effects.append(a.effects.pop())
            
            # Do same with bullets
            while len(a.bullets) > 0:
                self.bullets.append(a.bullets.pop())
        
        # Bullets
        for b in self.bullets:
            # --- Using code similar to Actors ---
            
            bullet_img = self.engine.images[b.image].get()
            r = pygame.Rect(bullet_img.get_rect())
            r.left = b.pos[0] + self.draw_margin[0] - b.width/2
            r.top = b.pos[1] + self.draw_margin[1] - b.height/2
            
            # Only draw bullets within the screen
            if r.right > self.draw_area[0] and r.left < self.draw_area[2]:
                if r.bottom > self.draw_area[1] and r.top < self.draw_area[3]:
                    if b.image == "":
                        # Bullet is dynamically drawn
                        b.draw(surf, self.draw_margin)
                    else:
                        # Bullet has an image
                        surf.blit(bullet_img, r)
                
        # Draw effects last
        for i, e in enumerate(self.effects):
            r = pygame.Rect(e.rect)
            r.left = e.rect.left + self.draw_margin[0]
            r.top = e.rect.top + self.draw_margin[1]
            
            # Only draw effects within the screen
            if r.right > self.draw_area[0] and r.left < self.draw_area[2]:
                if r.bottom > self.draw_area[1] and r.top < self.draw_area[3]:
                    e.draw(surf, self.draw_margin)
        
        # Placement (such as placing a building)
        if self.place_image:
            img = self.engine.images[self.place_image]
            r = img.get_rect()
            surf.blit(img.get(), pygame.Rect(
                self.mouse[0] - r.width/2, self.mouse[1] - r.height/2,
                r.width, r.height,
            ))
        
        # Panels
        for i, p in self.panels.items():
            surf.blit(*p.image())
        
        # Dragrect
        if self.drag_rect != None:
            # draw.rect uses a origin and size arguments, not topleft and bottomright
            line_rect = [
                self.drag_rect[0] + self.draw_margin[0] + self.scroll_x,
                self.drag_rect[1] + self.draw_margin[1] + self.scroll_y,
                self.drag_rect[2] - self.drag_rect[0],
                self.drag_rect[3] - self.drag_rect[1],
            ]
            
            # line_rect[0] = max(line_rect[0], self.draw_margin[0])
            
            pygame.draw.rect(surf, (255, 255, 255), line_rect, 1)
        
        pygame.display.flip()
        self._next_redraw = time.time() + self._redraw_delay
        self.redraw_count[0] += 1
    
    def place_actor_mode(self, actor_type):
        """Used to enter placement mode where an icon hovers beneath the
        cursor and when clicked is built or suchlike"""
        
        self.place_image = self.actor_types[actor_type]['placement_image']
        
        self.mouseup_callback = self.place_actor_from_click
        self.mouseup_callback_args = [{"type":actor_type}]
    
    def add_actor(self, a):
        a.rect = self.engine.images[a.image].get_rect()
        a.oid = self._current_actor_id
        self._current_actor_id += 1
        self.actors.append(a)

