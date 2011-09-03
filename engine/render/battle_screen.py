from __future__ import division

"""
BattleScreen is a screen with added functionality for handling things such as
scrolling all of it's information comes from the sim that it connects to
none of the game logic is implemented in the battle_screen at all.

The screen is also used to read in commands such as mouse-clicks.
BattleScreen itself is subclassed by BattleSim so as to keep the logic
code separate from the display/interface code.
"""

import multiprocessing
import time

import pygame
from pygame.locals import *

import screen

NUMBERS = range(K_0, K_9+1)

class BattleScreen (screen.Screen):
    self_regulate = True
    
    def __init__(self, engine):
        super(BattleScreen, self).__init__((engine.window_width, engine.window_height))
        
        # Used to translate key pushes into orders (e.g. M for move)
        # Note: These are the keyboard locations, not the letters
        # it will work with the same buttons (not letters) on a Dvorak as 
        # it will on a Qwerty
        self.hotkeys = {
            K_m: "move",
            K_s: "stop",
            K_a: "attack",
            K_a: "defend",
            K_h: "hold",
            K_p: "patrol",
            K_b: "build",
        }
        
        # Used to modify the order given when the mouse it clicked
        self.key_mod = None
        
        # Defaults to drawing to the screen sizes
        # we can override this if we want to
        self.draw_top, self.draw_left = 0, 0
        self.draw_area = (0, 0, engine.window_width, engine.window_height)
        self.draw_margin = [0, 0]
        
        self.background_image = pygame.Surface((1,1))
        self.background = pygame.Surface((1,1))
        self.have_scrolled = False
        
        self.scroll_speed = 15
        
        self.scroll_up_key = K_UP
        self.scroll_down_key = K_DOWN
        self.scroll_right_key = K_RIGHT
        self.scroll_left_key = K_LEFT
        
        self.allow_mouse_scroll = False
        
        # Defines how far we can scroll in any direction
        self.scroll_boundaries = (-100, -100, 0, 0)
        
        # Ctrl + N to assign, N to select
        self.control_groups = {}
        for i in NUMBERS:
            self.control_groups[i] = []
        
        self.scroll_boundary = 100
        
        self.selected_actors = []
        self.drag_rect = None
        
        self._next_redraw = time.time()
        self._redraw_delay = 0
        self.set_fps(40)
        
        self.terrain = {}
        self.bullets = []
        self.effects = []
        
        # Used to store orders for X steps later
        # http://www.gamasutra.com/view/feature/3094/1500_archers_on_a_288_network_.php
        self.orders = {}
        self.q_orders = {}# Orders that get added to the actor's order queue
        self.tick = 0
        self.tick_jump = 3
        
        for i in range(self.tick_jump+1):
            self.orders[i] = []
            self.q_orders[i] = []
        
        self.place_image = None
        self.mouseup_callback = None
        self.mouseup_callback_args = []
        self.panels = {}
        
        self.redraw_count = [0, 0]
        
        self.next_scroll = 0
        self.scroll_delay = 0.01
        
        self._current_actor_id = 0
    
    def post_init(self):
        self.draw_margin = [self.scroll_x + self.draw_area[0], self.scroll_y + self.draw_area[1]]
    
    def set_fps(self, fps):
        self._redraw_delay = 1/fps
    
    def add_order(self, the_actor, command, pos=None, target=None):
        if type(the_actor) == int:
            the_actor = self.actors[the_actor]
        self.orders[self.tick + self.tick_jump].append((the_actor, command, pos, target))
    
    def queue_order(self, the_actor, command, pos=None, target=None):
        if type(the_actor) == int:
            the_actor = self.actors[the_actor]
        self.q_orders[self.tick + self.tick_jump].append((the_actor, command, pos, target))
    
    def redraw(self):
        if time.time() < self._next_redraw:
            return
        
        if int(time.time()) != self.redraw_count[1]:
            # print("FPS: %s" % self.redraw_count[0])
            self.redraw_count = [0, int(time.time())]
        
        """Overrides the basic redraw as it's intended to be used with more animation"""
        # Draw background taking into account scroll
        surf = self.engine.display
        surf.blit(self.background_image, pygame.Rect(
            self.draw_margin[0], self.draw_margin[1],
            self.draw_area[2], self.draw_area[3],
        ))
        
        # Actors
        for a in self.actors:
            actor_img = self.engine.images[a.image]
            r = pygame.Rect(actor_img.get_rect())
            r.left = a.pos[0] + self.draw_margin[0] - r.width/2
            r.top = a.pos[1] + self.draw_margin[1] - r.height/2
            
            # Only draw actors within the screen
            if r.right > self.draw_area[0] and r.left < self.draw_area[2]:
                if r.bottom > self.draw_area[1] and r.top < self.draw_area[3]:
                    surf.blit(actor_img, r)
                    
                    # Selection box?
                    if a.selected:
                        r = a.selection_rect()
                        r.left += self.draw_margin[0]
                        r.top += self.draw_margin[1]
                        pygame.draw.rect(surf, (255, 255, 255), r, 1)
                        
                        surf.blit(*a.health_bar(self.draw_margin[0], self.draw_margin[1]))
                        
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
            
            bullet_img = self.engine.images[b.image]
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
            surf.blit(img, pygame.Rect(
                self.mouse[0] - r.width/2, self.mouse[1] - r.height/2,
                r.width, r.height,
            ))
        
        # Panels
        for i, p in self.panels.items():
            surf.blit(*p.image())
        
        # Dragrect
        if self.drag_rect != None:
            # draw.rect uses a origin and size arguments, not topleft and bottomright
            line_rect = (
                self.drag_rect[0] + self.draw_margin[0],
                self.drag_rect[1] + self.draw_margin[1],
                self.drag_rect[2] - self.drag_rect[0],
                self.drag_rect[3] - self.drag_rect[1],
            )
            
            pygame.draw.rect(surf, (255, 255, 255), line_rect, 1)
        
        pygame.display.flip()
        self._next_redraw = time.time() + self._redraw_delay
        self.redraw_count[0] += 1
    
    def handle_keyup(self, event):
        mods = pygame.key.get_mods()
        
        # Number key? Select or assign a control group
        if event.key in NUMBERS:
            if KMOD_CTRL & mods:
                self.assign_control_group(event.key)
            else:
                self.select_control_group(event.key)
            
            return
        
        # Make sure it's just one button being pushed
        if len(self.keys_down) == 0:
            if event.key in self.hotkeys:
                self.key_mod = self.hotkeys[event.key]
            else:
                self.key_mod = None
            
    
    def handle_keyhold(self):
        if time.time() < self.next_scroll:
            return
        
        self.next_scroll = time.time() + self.scroll_delay
        
        # Up/Down
        if self.scroll_up_key in self.keys_down:
            self.scroll_up()
        elif self.scroll_down_key in self.keys_down:
            self.scroll_down()
        
        # Right/Left
        if self.scroll_right_key in self.keys_down:
            self.scroll_right()
        elif self.scroll_left_key in self.keys_down:
            self.scroll_left()
        
        super(BattleScreen, self).handle_keyhold()
    
    def handle_mouseup(self, event, drag=False):
        if self.mouseup_callback:
            callback_func, args = self.mouseup_callback, self.mouseup_callback_args
            
            # Set these to nothing now incase we want to make a new callback
            # in the current callback
            self.mouseup_callback = None
            self.mouseup_callback_args = []
            
            return callback_func(event, drag, *args)
        
        mods = pygame.key.get_mods()
        real_mouse_pos = (event.pos[0] - self.draw_margin[0], event.pos[1] - self.draw_margin[1])
        
        # First check panels
        for i, p in self.panels.items():
            if p.contains(event.pos):
                if p.handle_mouseup(event, drag):
                    return
                else:
                    break
        
        if event.button == 1:# Left click
            if not drag:
                if self.key_mod:
                    actor_target = None
                    for a in self.actors:
                        if a.contains_point(real_mouse_pos):
                            actor_target = a
                            break
                    
                    if KMOD_SHIFT & mods:
                        for a in self.selected_actors:
                            self.queue_order(a, self.key_mod, pos=real_mouse_pos, target=actor_target)
                    else:
                        for a in self.selected_actors:
                            self.add_order(a, self.key_mod, pos=real_mouse_pos, target=actor_target)
                    
                else:
                    if not KMOD_SHIFT & mods:
                        self.unselect_all_actors()
                
                    for a in self.actors:
                        if a.contains_point(real_mouse_pos):
                            self.left_click_actor(a)
                            break
            elif drag:
                self.key_mod = None
        
        elif event.button == 3:# Right click
            actor_target = None
            for a in self.actors:
                if a.contains_point(real_mouse_pos):
                    actor_target = a
                    break
            
            # Now issue the command
            if not actor_target:
                for a in self.selected_actors:
                    if KMOD_SHIFT & mods:
                        self.queue_order(a, "move", real_mouse_pos)
                    else:
                        self.add_order(a, "move", real_mouse_pos)
                        
            else:
                if actor_target.team != self.selected_actors[0].team:
                    for a in self.selected_actors:
                        if KMOD_SHIFT & mods:
                            self.queue_order(a, "attack", actor_target)
                        else:
                            self.add_order(a, "attack", actor_target)
                else:
                    for a in self.selected_actors:
                        if KMOD_SHIFT & mods:
                            self.queue_order(a, "defend", actor_target)
                        else:
                            self.add_order(a, "defend", actor_target)
            
        else:
            print("battle_screen.handle_mouseup: event.button = %s" % event.button)
    
    def handle_doubleclick(self, first_click, second_click):
        # First check panels
        for i, p in self.panels.items():
            if p.contains(first_click.pos) and p.contains(second_click.pos):
                if p.handle_doubleclick(first_click, second_click):
                    return
                else:
                    break
        
        first_real_mouse_pos = (
            first_click.pos[0] - self.draw_margin[0],
            first_click.pos[1] - self.draw_margin[1]
        )
        
        second_real_mouse_pos = (
            second_click.pos[0] - self.draw_margin[0],
            second_click.pos[1] - self.draw_margin[1]
        )
        
        # Now check actors
        for a in self.actors:
            if a.contains_point(first_real_mouse_pos) and a.contains_point(second_real_mouse_pos):
                self.double_left_click_actor(a)
                break
    
    def left_click_actor(self, act):
        if act.selected:
            self.unselect_actor(act)
        else:
            self.select_actor(act)
    
    def double_left_click_actor(self, act):
        mods = pygame.key.get_mods()
        actors_to_select = []
        
        scr_rect = (
            -self.scroll_x + self.draw_area[0],
            -self.scroll_y + self.draw_area[1],
            -self.scroll_x + self.draw_area[2],
            -self.scroll_y + self.draw_area[3]
        )
        
        for a in self.actors:
            if a.actor_type == act.actor_type:
                if a.inside(scr_rect):
                    actors_to_select.append(a)
        
        if KMOD_SHIFT & mods:
            # Add to current selection
            for a in actors_to_select:
                self.select_actor(a)
        else:
            self.selected_actors = []
            
            # Set as current selection
            for a in actors_to_select:
                self.select_actor(a)
        
        self.selection_changed()
    
    def handle_mousedrag(self, event, drag_rect):
        if event.buttons[0] == 1:
            self.drag_rect = drag_rect
            
            self.drag_rect = (
                drag_rect[0] - self.draw_margin[0],
                drag_rect[1] - self.draw_margin[1],
                drag_rect[2] - self.draw_margin[0],
                drag_rect[3] - self.draw_margin[1],
            )
    
    def handle_mousedragup(self, event, drag_rect):
        mods = pygame.key.get_mods()
        self.drag_rect = None
        
        # Correct for margins
        drag_rect = (
            drag_rect[0] - self.draw_margin[0],
            drag_rect[1] - self.draw_margin[1],
            drag_rect[2] - self.draw_margin[0],
            drag_rect[3] - self.draw_margin[1],
        )
        
        if event.button == 1:
            if not KMOD_SHIFT & mods:
                self.unselect_all_actors()
                
            for a in self.actors:
                if a.inside(drag_rect):
                    self.select_actor(a)
    
    def unselect_all_actors(self):
        for a in self.selected_actors[:]:
            del(self.selected_actors[self.selected_actors.index(a)])
            a.selected = False
            self.selection_changed()
    
    def unselect_actor(self, a):
        del(self.selected_actors[self.selected_actors.index(a)])
        a.selected = False
        self.selection_changed()
    
    def select_actor(self, a):
        self.selected_actors.append(a)
        a.selected = True
        self.selection_changed()
    
    def update(self):
        # It might be that the mouse is scrolling
        # but we only use this if there are no arrow keys held down
        if self.allow_mouse_scroll:
            if self.scroll_up_key not in self.keys_down:
                if self.scroll_down_key not in self.keys_down:
                    if self.scroll_right_key not in self.keys_down:
                        if self.scroll_left_key not in self.keys_down:
                            # None of our scroll keys are down, we can mouse scroll
                            self.check_mouse_scroll()
    
    def check_mouse_scroll(self):
        left_val = self.scroll_boundary - (self.engine.window_width - self.mouse[0])
        right_val = self.scroll_boundary - self.mouse[0]
        
        up_val = self.scroll_boundary - (self.engine.window_height - self.mouse[1])
        down_val = self.scroll_boundary - self.mouse[1]
        
        # Scroll based on how far it is
        if down_val > 0:
            self.scroll_down(down_val/self.scroll_boundary)
        elif up_val > 0:
            self.scroll_up(up_val/self.scroll_boundary)
        
        if left_val > 0:
            self.scroll_left(left_val/self.scroll_boundary)
        elif right_val > 0:
            self.scroll_right(right_val/self.scroll_boundary)
    
    def assign_control_group(self, key):
        self.control_groups[key] = self.selected_actors[:]
    
    def select_control_group(self, key):
        if len(self.control_groups[key]) > 0:
            self.unselect_all_actors()
            for a in self.control_groups[key][:]:
                self.select_actor(a)
            
            self.selection_changed()
    
    def selection_changed(self):
        pass
    
    def scroll_right(self, rate = 1):
        last_pos = self.scroll_x
        
        self.scroll_x -= rate * self.scroll_speed
        self.scroll_x = max(self.scroll_boundaries[0], self.scroll_x)
        
        self.draw_margin[0] = self.scroll_x + self.draw_area[0]
    
    def scroll_left(self, rate = 1):
        last_pos = self.scroll_x
        
        self.scroll_x += rate * self.scroll_speed
        self.scroll_x = min(self.scroll_boundaries[2], self.scroll_x)
        
        self.draw_margin[0] = self.scroll_x + self.draw_area[0]
        
    def scroll_down(self, rate = 1):
        last_pos = self.scroll_y
        
        self.scroll_y -= rate * self.scroll_speed
        self.scroll_y = max(self.scroll_boundaries[1], self.scroll_y)
        
        self.draw_margin[1] = self.scroll_y + self.draw_area[1]
        
    def scroll_up(self, rate = 1):
        last_pos = self.scroll_y
        
        self.scroll_y += rate * self.scroll_speed
        self.scroll_y = min(self.scroll_boundaries[3], self.scroll_y)
        
        self.draw_margin[1] = self.scroll_y + self.draw_area[1]
    
    def place_actor_mode(self, actor_type):
        """Used to enter placement mode where an icon hovers beneath the
        cursor and when clicked is built or suchlike"""
        
        self.place_image = actor_type['placement_image']
        
        self.mouseup_callback = self.place_actor
        self.mouseup_callback_args = [actor_type]
    
    def add_actor(self, a):
        a.rect = self.engine.images[a.image].get_rect()
        a.oid = self._current_actor_id
        self._current_actor_id += 1
        self.actors.append(a)

