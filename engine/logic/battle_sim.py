from __future__ import division

"""
BattleSim is the subclass that runs the battle itself.
The sim is expected to be subclassed so as to program in the game rules.
"""

import pygame
from pygame.locals import *

import time
import sys
import json
import pdb
import weakref

from engine.libs import actor_lib, vectors, geometry, pathing, sim_lib
from engine.logic import actor_subtypes
from engine.ai import autotargeter, core_ai
from engine.render import battle_screen

def handle_number(v):
    if type(v) not in (int, float):
        raise Exception("%s (%s) is not of type int or float yet is meant to be cast as a number" % (
            v, type(v)
        ))
    
    return v

def handle_boolean(v):
    if type(v) != bool:
        raise Exception("%s (%s) is not a boolean but needs to be cast as one" % (
            v, type(v)
        ))
    
    return v

attribute_handlers = {
    "number":   handle_number,
    "boolean":  handle_boolean,
}

attribute_list = (
    ("collision_interval",  "_collision_interval", "number"),
    ("scroll_speed",        "scroll_speed", "number"),
    ("allow_mouse_scroll",  "allow_mouse_scroll", "boolean"),
    ("scroll_delay",        "scroll_delay", "number"),
)


for a, b, t in attribute_list:
    if t not in attribute_handlers:
        raise Exception("Error initialising battle_sim.py: attribute %s maps to a type %s but there is no handler for that type" % (
            a, t
        ))


class BattleSim (battle_screen.BattleScreen):
    def __init__(self, engine):
        # How many cycles between collision checks
        self._collision_interval = 5
        self._collision_inverval_count = 0
        
        super(BattleSim, self).__init__(engine)
        
        self.next_cycle = time.time()
        
        sim_lib.set_speed(self, 100)
        
        self.running = True
        self.loaded = False
        
        self.actor_types = {}
        self.ability_types = {}
        self.build_lists = {}
        self.tech_trees = {}
        
        self.autotargeters = {}
        self.out_queues = {}
        self.in_queues = {}
        self.cycle_count = [0, 0]
        
        # Used to signal that we may need to update a menu
        self.signal_menu_rebuild = False
        
        self.next_ai_update = 0
    
    def quit(self, event=None):
        for k, q in self.out_queues.items():
            q.put({"cmd":"quit"})
        
        super(BattleSim, self).quit(event)
    
    def data_dump(self, file_path=None):
        """Dumps data for debugging purposes"""
        
        data = []
        
        data.append("Tick: %d" % self.tick)
        
        data.append("\n**** Actors ****")
        for a in self.actors:
            data.append("\nAID: %s, ID: %s" % (a.oid, str(a)))
            data.append("pos: %s" % a.pos)
            data.append("rect: %s" % a.rect)
            data.append("velocity: %s" % a.velocity)
        
        data.append("\n**** Collisions **** ")
        data.append(str(sim_lib.get_collisions(self.actors)))
        
        data = "\n".join(data)
        
        # Output
        if file_path == None:
            print(data)
            print("")
        else:
            with open(file_path, "w") as f:
                f.write(data)
    
    def issue_orders(self):
        """Issues the orders that have been stored in the delayed storage"""
        for a, cmd, pos, target in self.orders[self.tick]:
            a.issue_command(cmd, pos, target)
        
        for a, cmd, pos, target in self.q_orders[self.tick]:
            a.append_command(cmd, pos, target)
        
        del(self.orders[self.tick])
        del(self.q_orders[self.tick])
    
    def redraw(self):
        # If we've not loaded anything yet then we won't need to cycle
        if not self.loaded:
            super(BattleSim, self).redraw()
            return
        
        # Now to potentially draw the screen
        super(BattleSim, self).redraw()
    
    def update(self):
        super(BattleSim, self).update()
        
        if time.time() > self.next_cycle:
            try:
                self.logic_cycle()
            except Exception as e:
                self.data_dump()
                raise
    
    def read_ai_queues(self):
        for t, q in self.in_queues.items():
            while not q.empty():
                print("AI -> Sim: %s" % q.get())
            
    
    def update_ai_queues(self):
        data = []
        
        data.append({
            "cmd":          "actors",
            "actor_list":   [actor_lib.strip_actor(a) for a in self.actors],
        })
        
        for t, q in self.out_queues.items():
            for d in data:
                q.put(d)
    
    def logic_cycle(self):
        """The core function of the sim, this is where the 'magic happens'"""
        if int(time.time()) != self.cycle_count[1]:
            self.cycle_count = [0, int(time.time())]
        
        self.next_ai_update -= 1
        if self.next_ai_update <= 0:
            self.update_ai_queues()
            self.next_ai_update = 30
        
        self.read_ai_queues()
        
        self.tick += 1
        
        self.orders[self.tick + self.tick_jump] = []
        self.q_orders[self.tick + self.tick_jump] = []
        self.issue_orders()
        
        # This will warn us if the sim is lagging behind how fast it's meant to be
        time_over = time.time() - self.next_cycle
        if time_over > 0.25:
            print("Logic lag of %ss" % time_over)
        
        # Update the AIs
        for t, a in self.autotargeters.items():
            a.update()
        
        # Update the actors themselves
        to_remove = []
        to_add = []
        for i, a in enumerate(self.actors):
            a.update()
            
            # Is the actor trying to place a new unit?
            # We only check as often as we check for collisions, this gives a cycle
            # for an already started actor to be given a position as it defaults to 0,0
            # and this has an impact on it's rect
            if self._collision_inverval_count < 2:
                if a.build_queue != []:
                    a_type = self.actor_types[a.build_queue[0]]
                
                    new_rect_pos = vectors.add_vectors(a.pos, a.build_offset)
                    new_rect = pygame.Rect(new_rect_pos[0], new_rect_pos[1], a_type['size'][0], a_type['size'][1])
                
                    if not sim_lib.test_possible_collision(self.actors, new_rect):
                        to_add.append((a, {
                            "type": a.build_queue[0],
                            "pos":  new_rect_pos,
                            "team": a.team,
                            "order_queue": list(a.rally_orders),
                        }))
                        self.signal_menu_rebuild = True
                        del(a.build_queue[0])
            
            if a.hp <= 0: to_remove.insert(0, i)
        for i in to_remove: del(self.actors[i])
        for builder, new_actor in to_add:
            new_target = self.place_actor(new_actor)
            builder.issue_command("aid", target=new_target)
            
        
        # Bullets too
        to_delete = []
        for i, b in enumerate(self.bullets):
            b.update()
            
            if b.dead:
                new_effect = b.explode(self.actors)
                if new_effect != None:
                    self.effects.append(new_effect)
                to_delete.insert(0, i)
        for i in to_delete:
            del(self.bullets[i])
        
        # And lastly effects
        to_delete = []
        for i, e in enumerate(self.effects):
            e.update()
            if e.dead:
                to_delete.insert(0, i)
                continue
        
        # Delete any uneeded effects
        for i in to_delete:
            del(self.effects[i])
        
        # Check for collisions
        self._collision_inverval_count -= 1
        
        if self._collision_inverval_count < 1:
            self._collision_inverval_count = self._collision_interval
            collisions = sim_lib.get_collisions(self.actors)
            
            # We now have a list of all the collisions
            for obj1, obj2 in collisions:
                # We order them based on aid, this way we always deal with the same
                # actor in the same way and the order the collison was found is
                # irrelevant
                actor_lib.handle_pathing_collision(min(obj1, obj2), max(obj1, obj2))
        
        # Set next cycle time
        self.next_cycle = time.time() + self._cycle_delay
        self.cycle_count[0] += 1
    
    def place_actor_from_click(self, event, drag, actor_data):
        self.place_image = None
        actor_data['pos'] = [event.pos[0] - self.draw_margin[0], event.pos[1] - self.draw_margin[1], 0]
        actor_data['team'] = self.player_team
        
        # If holding the shift key, allow them to continue placing
        mods = pygame.key.get_mods()
        if KMOD_SHIFT & mods:
            self.place_actor_mode(actor_data['type'])
        
        return self.place_actor(actor_data)
    
    def place_actor(self, actor_data):
        """Called when there's a click while in placement mode.
        Returns a weakref to the actor just created"""
        class_type = self.actor_types[actor_data['type']]['type']
        aclass = actor_subtypes.types[class_type]
        
        a = aclass()
        a.apply_template(self.actor_types[actor_data['type']])
        a.apply_data(actor_data)
        
        # Assume 0 completion
        a.completion    = actor_data.get("completion", 0)
        a.hp            = actor_data.get("hp", 0.1)
        
        if a.hp == None:
            a.hp = a.max_hp
        
        a.order_queue   = actor_data.get('order_queue', [])
        
        for ability in self.actor_types[actor_data['type']]['abilities']:
            a.add_ability(self.ability_types[ability])
        
        # If AI's exist, assign the actor to one
        if a.team in self.autotargeters:
            a.autotargeter = self.autotargeters[a.team]
        
        self.add_actor(a)
        
        return weakref.ref(a)()
    
    def load_all(self, config_path, setup_path, game_path, local=True):
        """Uses a local path for each of the 3 load types"""
        
        if local:
            config_path = "{0}/{1}".format(sys.path[0], config_path)
            setup_path = "{0}/{1}".format(sys.path[0], setup_path)
            game_path = "{0}/{1}".format(sys.path[0], game_path)
        
        with open(config_path) as f:
            data = json.loads(f.read())
            self.load_config(data)
        
        with open(setup_path) as f:
            data = json.loads(f.read())
            self.load_setup(data)
        
        with open(game_path) as f:
            data = json.loads(f.read())
            self.load_game(data)
    
    def load_config(self, data):
        for name, maps_to, data_type in attribute_list:
            if name not in data: continue
            
            v = attribute_handlers[data_type](data[name])
            
            setattr(self, maps_to, v)
    
    def load_setup(self, data):
        # Load abilities
        for type_name, type_data in data['abilities'].items():
            self.ability_types[type_name] = type_data
        
        # Load actors
        for type_name, type_data in data['actors'].items():
            actor_lib.build_template_cache(type_data, self.engine)
            self.actor_types[type_name] = type_data
            self.actor_types[type_name]['name'] = type_name
        
        # Load tech trees
        for tree_name, tree_data in data['tech_trees'].items():
            self.tech_trees[tree_name] = tree_data
        
        # Load build dicts
        for build_name, build_list in data['build_lists'].items():
            self.build_lists[build_name] = build_list
    
    def load_game(self, data):
        teams = set()
        
        # Load AIs (AIs are optional)
        for ai_team, ai_data in data.get('ais', {}).items():
            # Annoyingly we need to convert it from a unicode dict
            # into a standard one
            new_data = {}
            for k, v in ai_data.items():
                new_data[str(k)] = v
            
            new_data['team'] = ai_team
            out_queue, in_queue = core_ai.make_ai(new_data['type'])
            
            self.out_queues[ai_team] = out_queue
            self.in_queues[ai_team] = in_queue
            
        self.out_queues[ai_team].put({"cmd":"init","data":new_data})
        
        # Load actors
        for actor_data in data['actors']:
            # Assume it's complete
            actor_data['completion']    = actor_data.get("completion", 100)
            actor_data['hp']            = actor_data.get("hp", None)
            a = self.place_actor(actor_data)
            teams.add(actor_data['team'])
        
        # Any team without a specifically chosen AI gets the default one
        for t in teams:
            if t not in self.autotargeters:
                self.autotargeters[t] = autotargeter.Autotargeter(self, t)
        
        # Now assign the AIs
        for a in self.actors:
            a.autotargeter = self.autotargeters[a.team]
        
        self.loaded = True

