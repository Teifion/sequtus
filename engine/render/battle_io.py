from __future__ import division

"""
BattleIO is a screen with added functionality for handling the IO side of things.
BattleScreen handles the rendering
"""

import time
import weakref

import pygame
from pygame.locals import *

from engine.render import screen
from engine.libs import screen_lib, actor_lib, vectors

NUMBERS = range(K_0, K_9+1)

class BattleIO (screen.Screen):
    def __init__(self, engine):
        super(BattleIO, self).__init__((engine.window_width, engine.window_height))
        
        # Used to translate key pushes into orders (e.g. M for move)
        # Note: These are the keyboard locations, not the letters
        # it will work with the same buttons (not letters) on a Dvorak as 
        # it will on a Qwerty
        self.hotkeys = {
            K_m: "move",
            K_s: "stop",
            K_a: "attack",
            # K_a: "aid",
            K_h: "hold",
            K_p: "patrol",
            K_b: "build",
            53: "unselect"# 53 = esc
        }
        
        # Used to modify the order given when the mouse it clicked
        self.key_mod = None
        
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
        
        self.drag_rect = None
        
        self._next_redraw = time.time()
        self._redraw_delay = 0
        screen_lib.set_fps(self, 40)
        
        # Used to store orders for X steps later
        # http://www.gamasutra.com/view/feature/3094/1500_archers_on_a_288_network_.php
        self.orders = {}
        self.q_orders = {}# Orders that get added to the actor's order queue
        self.tick = 0
        self.tick_jump = 3
        
        for i in range(self.tick_jump+1):
            self.orders[i] = []
            self.q_orders[i] = []
        
        self.mouseup_callback = None
        self.mouseup_callback_args = []
        
        self.next_scroll = 0
        self.scroll_delay = 0.01
        
        # This is switched instead of a function call because it's possible
        # that we may alter the selection several times in a row and it would
        # be a waste to rebuild menus several times
        self._selection_has_changed = False
    
    def add_order(self, the_actor, command, pos=None, target=None):
        if type(the_actor) == int:
            the_actor = self.actors[the_actor]
        self.orders[self.tick + self.tick_jump].append((the_actor, command, pos, target))
    
    def queue_order(self, the_actor, command, pos=None, target=None):
        if type(the_actor) == int:
            the_actor = self.actors[the_actor]
        self.q_orders[self.tick + self.tick_jump].append((the_actor, command, pos, target))
    
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
        
        if event.key in self.hotkeys:
            if len(self.selected_actors) > 0:
                if self.hotkeys[event.key] == "move":
                    pass
                if self.hotkeys[event.key] == "stop":
                    for a in self.selected_actors:
                        if a.team == self.player_team:
                            if KMOD_SHIFT & mods:
                                self.queue_order(a, "stop")
                            else:
                                self.add_order(a, "stop")
                if self.hotkeys[event.key] == "attack":
                    pass
                if self.hotkeys[event.key] == "hold":
                    pass
                if self.hotkeys[event.key] == "patrol":
                    pass
                if self.hotkeys[event.key] == "build":
                    pass
            
    
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
        
        super(BattleIO, self).handle_keyhold()
    
    def handle_mousedown(self, event):
        # If it's in a panel we don't want to allow a drag option
        for i, p in self.panels.items():
            if p.contains(event.pos):
                self.mouse_down_at = None
    
    def handle_mouseup(self, event, drag=False):
        # We are no longer dragging, lets get rid of this rect
        self.drag_rect = None
        
        # First check panels
        for i, p in self.panels.items():
            if p.contains(event.pos):
                result = p.handle_mouseup(event, drag)
                
                if result == True:# Panel has handled it
                    return
                elif result == False or result == None:# Panel has not handled it
                    break
                else:
                    # Panel has sent us back a new event
                    # we re-run this function with the new event
                    return self.handle_mouseup(result, drag)
        
        if self.mouseup_callback:
            callback_func, args = self.mouseup_callback, self.mouseup_callback_args
            
            # Set these to nothing now incase we want to make a new callback
            # in the current callback
            self.mouseup_callback = None
            self.mouseup_callback_args = []
            
            return callback_func(event, drag, *args)
        
        mods = pygame.key.get_mods()
        real_mouse_pos = (event.pos[0] - self.draw_margin[0], event.pos[1] - self.draw_margin[1])
        
        if event.button == 1:# Left click
            if not drag:
                if self.key_mod:
                    actor_target = None
                    for a in self.actors:
                        if actor_lib.contains_point(a, real_mouse_pos):
                            actor_target = weakref.ref(a)()
                            break
                    
                    if KMOD_SHIFT & mods:
                        for a in self.selected_actors:
                            if a.team == self.player_team:
                                self.queue_order(a, self.key_mod, pos=real_mouse_pos, target=actor_target)
                    else:
                        for a in self.selected_actors:
                            if a.team == self.player_team:
                                self.add_order(a, self.key_mod, pos=real_mouse_pos, target=actor_target)
                    
                else:
                    if not KMOD_SHIFT & mods:
                        self.unselect_all_actors()
                
                    for a in self.actors:
                        if actor_lib.contains_point(a, real_mouse_pos):
                            self.left_click_actor(a)
                            break
            elif drag:
                self.key_mod = None
        
        elif event.button == 3:# Right click
            if len(self.selected_actors) == 0:
                return
        
            actor_target = None
            for a in self.actors:
                if actor_lib.contains_point(a, real_mouse_pos):
                    actor_target = weakref.ref(a)()
                    break
            
            # No actor clicked, this means we're moving
            if not actor_target:
                for a in self.selected_actors:
                    if a.team == self.player_team:
                        if KMOD_SHIFT & mods:
                            self.queue_order(a, "move", pos=real_mouse_pos)
                        else:
                            self.add_order(a, "move", pos=real_mouse_pos)
                        
            # An actor was clicked
            else:
                if actor_target.team != self.selected_actors[0].team:
                    for a in self.selected_actors:
                        if a.team == self.player_team:
                            if KMOD_SHIFT & mods:
                                self.queue_order(a, "attack", target=actor_target)
                            else:
                                self.add_order(a, "attack", target=actor_target)
                else:
                    for a in self.selected_actors:
                        if a.team == self.player_team:
                            if KMOD_SHIFT & mods:
                                self.queue_order(a, "aid", target=actor_target)
                            else:
                                self.add_order(a, "aid", target=actor_target)
            
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
            if actor_lib.contains_point(a, first_real_mouse_pos) and actor_lib.contains_point(a, second_real_mouse_pos):
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
                if actor_lib.inside(a, scr_rect):
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
        
        self._selection_has_changed = True
    
    def handle_mousedrag(self, event, drag_rect):
        # First check panels, but only if the dragging started within a panel
        if drag_rect == None:
            for i, p in self.panels.items():
                if p.contains(event.pos):
                    p.handle_mousedrag(event)
            
            return
        
        if event.buttons[0] == 1:
            # We don't want to be able to drag over the panels
            drag_rect = list(drag_rect)
            drag_rect[0] = max(drag_rect[0], self.draw_margin[0])
            drag_rect[1] = max(drag_rect[1], self.draw_margin[1])
            
            self.drag_rect = drag_rect
            
            self.drag_rect = (
                drag_rect[0] - self.draw_margin[0],
                drag_rect[1] - self.draw_margin[1],
                drag_rect[2] - self.draw_margin[0],
                drag_rect[3] - self.draw_margin[1],
            )
    
    def handle_mousedragup(self, event, drag_rect):
        if drag_rect == None: return
        
        mods = pygame.key.get_mods()
        self.drag_rect = None
        
        # Correct for margins and scroll
        drag_rect = (
            drag_rect[0] - self.draw_margin[0] + self.scroll_x,
            drag_rect[1] - self.draw_margin[1] + self.scroll_y,
            drag_rect[2] - self.draw_margin[0] + self.scroll_x,
            drag_rect[3] - self.draw_margin[1] + self.scroll_y,
        )
        
        contains_friendly = False
        short_list = []
        if event.button == 1:
            if not KMOD_SHIFT & mods:
                self.unselect_all_actors()
            
            # First see if there are friendlies there
            # if the selection contains friendlies then we
            # should only select the friendlies
            for a in self.actors:
                if actor_lib.inside(a, drag_rect):
                    if a.team == self.player_team:
                        contains_friendly = True
                    short_list.append(a)
            
            # contains_friendly
            for a in short_list:
                if contains_friendly:
                    if a.team == self.player_team:
                        self.select_actor(a)
                else:
                    self.select_actor(a)
    
    def unselect_all_actors(self):
        for a in self.selected_actors[:]:
            del(self.selected_actors[self.selected_actors.index(a)])
            a.selected = False
            self._selection_has_changed = True
    
    def unselect_actor(self, a):
        try:
            a.selected = False
            del(self.selected_actors[self.selected_actors.index(a)])
        except Exception as e:
            print("""! battle_screen.unselect_actor had an exception trying
to delete an actor from the list of selected actors.""")
        
        a.selected = False
        self._selection_has_changed = True
    
    def select_actor(self, a):
        self.selected_actors.append(a)
        a.selected = True
        self._selection_has_changed = True
    
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
            
            self._selection_has_changed = True
    
    def selection_changed(self):
        pass
    
    def scroll_right(self, rate = 1):
        self.scroll_x -= rate * self.scroll_speed
        self.scroll_x = max(self.scroll_boundaries[0], self.scroll_x)
        
        self.draw_margin[0] = self.scroll_x + self.draw_area[0]
    
    def scroll_left(self, rate = 1):
        self.scroll_x += rate * self.scroll_speed
        self.scroll_x = min(self.scroll_boundaries[2], self.scroll_x)
        
        self.draw_margin[0] = self.scroll_x + self.draw_area[0]
        
    def scroll_down(self, rate = 1):
        self.scroll_y -= rate * self.scroll_speed
        self.scroll_y = max(self.scroll_boundaries[1], self.scroll_y)
        
        self.draw_margin[1] = self.scroll_y + self.draw_area[1]
        
    def scroll_up(self, rate = 1):
        self.scroll_y += rate * self.scroll_speed
        self.scroll_y = min(self.scroll_boundaries[3], self.scroll_y)
        
        self.draw_margin[1] = self.scroll_y + self.draw_area[1]
    
    def scroll_to_coords(self, x, y):
        """Scroll so that the coords x,y are at the centre of the view"""
        
        self.scroll_x = - x + self.engine.window_width/2
        self.scroll_y = - y + self.engine.window_height/2
        
        # Boundaries
        self.scroll_x = min(self.scroll_boundaries[2], max(self.scroll_boundaries[0], self.scroll_x))
        self.scroll_y = min(self.scroll_boundaries[3], max(self.scroll_boundaries[1], self.scroll_y))
        
        # Alter draw margin
        self.draw_margin[0] = self.scroll_x + self.draw_area[0]
        self.draw_margin[1] = self.scroll_y + self.draw_area[1]

