from __future__ import division

"""
BattleSim is the subclass that runs the battle itself.
The sim is expected to be subclassed so as to program in the game rules.
"""

import pygame
import time
import sys
import json
import pdb

from engine.libs import actor_lib, vectors, geometry, pathing
from engine.logic import actor_subtypes, ai
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
        
        self.set_speed(100)
        
        self.running = True
        self.loaded = False
        
        self.actor_types = {}
        self.ability_types = {}
        
        self.ais = {}
        self.cycle_count = [0, 0]
    
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
            data.append("dont_collide: %s" % a.dont_collide_with)
        
        data.append("\n**** Collisions **** ")
        data.append(str(self.get_collisions()))
        
        data = "\n".join(data)
        
        # Output
        if file_path == None:
            print(data)
            print("")
        else:
            with open(file_path, "w") as f:
                f.write(data)
        
        
    def set_speed(self, cycles_per_second):
        self.cycles_per_second = cycles_per_second
        self._cycle_delay = 1/self.cycles_per_second
    
    def issue_orders(self):
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
        
        # Main logic execution loop
        # if time.time() > self.next_cycle:
        #     self.logic_cycle()
        
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
    
    def logic_cycle(self):
        if int(time.time()) != self.cycle_count[1]:
            # print("CPS: %s" % self.cycle_count[0])
            self.cycle_count = [0, int(time.time())]
        
        self.tick += 1
        
        self.orders[self.tick + self.tick_jump] = []
        self.q_orders[self.tick + self.tick_jump] = []
        self.issue_orders()
        
        # This will warn us if the sim is lagging behind how fast it's meant to be
        time_over = time.time() - self.next_cycle
        if time_over > 0.25:
            print("Logic lag of %ss" % time_over)
        
        # Update the AIs
        for t, a in self.ais.items():
            a.update()
        
        # Update the actors themselves
        to_remove = []
        for i, a in enumerate(self.actors):
            a.update()
            
            if a.hp <= 0: to_remove.insert(0, i)
        for i in to_remove: del(self.actors[i])
        
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
            collisions = self.get_collisions()
            
            # We now have a list of all the collisions
            for obj1, obj2 in collisions:
                # We order them based on aid, this way we always deal with the same
                # actor in the same way and the order the collison was found is
                # irrelevant
                actor_lib.handle_pathing_collision(min(obj1, obj2), max(obj1, obj2))
        
        # Set next cycle time
        self.next_cycle = time.time() + self._cycle_delay
        self.cycle_count[0] += 1
    
    def get_collisions(self):
        collisions = []
        collided = set()
        for i, a in enumerate(self.actors):
            for j, b in enumerate(self.actors):
                if j in collided: continue
                if i == j: continue
                if geometry.rect_collision(a.rect, b.rect, True):
                    collisions.append((a,b))
                    
                    collided.add(i)
                    collided.add(j)
        
        return collisions
    
    def place_actor_from_click(self, event, drag, actor_data):
        self.place_image = None
        actor_data['pos'] = [event.pos[0] - self.draw_margin[0], event.pos[1] - self.draw_margin[1], 0]
        
        return self.place_actor(actor_data)
    
    def place_actor(self, actor_data):
        """Called when there's a click while in placement mode"""
        class_type = self.actor_types[actor_data['type']]['type']
        aclass = actor_subtypes.types[class_type]
        
        a = aclass()
        a.apply_template(self.actor_types[actor_data['type']])
        a.apply_data(actor_data)
        
        # Assume 0 completion
        a.completion = actor_data.get("completion", 0)
        
        for ability in self.actor_types[actor_data['type']]['abilities']:
            a.add_ability(self.ability_types[ability])
        
        # If AI's exist, assign the actor to one
        if a.team in self.ais:
            a.ai = self.ais[a.team]
            
        
        self.add_actor(a)
    
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
    
    def load_game(self, data):
        teams = set()
        
        # Load AIs (AIs are optional)
        for ai_team, ai_data in data.get('ais', {}).items():
            print(ai_team, ai_data)
        
        # Load actors
        for actor_data in data['actors']:
            # Assume it's complete
            actor_data['completion'] = actor_data.get("completion", 100)
            self.place_actor(actor_data)
            teams.add(actor_data['team'])
        
        # Any team without a specifically chosen AI gets the default one
        for t in teams:
            if t not in self.ais:
                self.ais[t] = ai.AI(self, t)
        
        # Now assign the AIs
        for a in self.actors:
            a.ai = self.ais[a.team]
        
        self.loaded = True

