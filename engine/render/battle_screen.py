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

from engine.render import screen
from engine.libs import screen_lib, actor_lib, vectors

NUMBERS = range(K_0, K_9+1)

class BattleScreen (screen.Screen):
    self_regulate = True
    player_team = None
    facings = 360/4# The number of different angles we'll draw
    
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
            # K_a: "aid",
            K_h: "hold",
            K_p: "patrol",
            K_b: "build",
            53: "unselect"# 53 = esc
        }
        
        self.image_cache = {}
        
        # Used to modify the order given when the mouse it clicked
        self.key_mod = None
        
        # Defaults to drawing to the screen sizes, this gets overriden later
        # it's used to work out what size rectangle to draw to for the
        # battlefield (so taking into account panels and menus)
        self.draw_area = (0, 0, engine.window_width, engine.window_height)
        
        # The margins that are used for things like menus and panels, we don't
        # want to draw battlefield stuff to these
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
        screen_lib.set_fps(self, 40)
        
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
        
        # This is switched instead of a function call because it's possible
        # that we may alter the selection several times in a row and it would
        # be a waste to rebuild menus several times
        self._selection_has_changed = False
    
    def post_init(self):
        self.draw_margin = [self.scroll_x + self.draw_area[0], self.scroll_y + self.draw_area[1]]
    
    def add_order(self, the_actor, command, pos=None, target=None):
        if type(the_actor) == int:
            the_actor = self.actors[the_actor]
        self.orders[self.tick + self.tick_jump].append((the_actor, command, pos, target))
    
    def queue_order(self, the_actor, command, pos=None, target=None):
        if type(the_actor) == int:
            the_actor = self.actors[the_actor]
        self.q_orders[self.tick + self.tick_jump].append((the_actor, command, pos, target))
    
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
        
        super(BattleScreen, self).handle_keyhold()
    
    def handle_mousedown(self, event):
        # If it's in a panel we don't want to allow a drag option
        for i, p in self.panels.items():
            if p.contains(event.pos):
                self.mouse_down_at = None
    
    def handle_mouseup(self, event, drag=False):
        # We are no longer dragging, lets get rid of this rect
        self.drag_rect = None
        
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
                result = p.handle_mouseup(event, drag)
                
                if result == True:# Panel has handled it
                    return
                elif result == False or result == None:# Panel has not handled it
                    break
                else:
                    # Panel has sent us back a new event
                    # we re-run this function with the new event
                    return self.handle_mouseup(result, drag)
        
        if event.button == 1:# Left click
            if not drag:
                if self.key_mod:
                    actor_target = None
                    for a in self.actors:
                        if a.contains_point(real_mouse_pos):
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
                        if a.contains_point(real_mouse_pos):
                            self.left_click_actor(a)
                            break
            elif drag:
                self.key_mod = None
        
        elif event.button == 3:# Right click
            actor_target = None
            for a in self.actors:
                if a.contains_point(real_mouse_pos):
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
                if a.inside(drag_rect):
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

