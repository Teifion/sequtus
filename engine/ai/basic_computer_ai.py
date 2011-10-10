import re
import traceback
import sys

from engine.ai import core_ai
from engine.libs import actor_lib, vectors

line_match = re.compile(r"(([0-9])\* )?(.*)")

class BasicComputerAI (core_ai.AICore):
    def __init__(self, *args, **kwargs):
        super(BasicComputerAI, self).__init__(*args, **kwargs)
        
        self.bases = {}
        self.needed_buildings = []
        
        self.prefs = {
            "actor_format": "dict",
        }
        
        self.enemy_actors = {}
        self.own_actors = {}
    
    def _init(self, **kwargs):
        super(BasicComputerAI, self)._init(**kwargs)
        
        if "bases" in kwargs:
            for k, v in kwargs['bases'].items():
                try:
                    self._save_base(k, v)
                except Exception as e:
                    traceback.print_exc(file=sys.stdout)
                    print("Error loading bases, abandoning loading of further bases")
    
    def _save_base(self, base_name, base_data):
        base_setup = {
            "location": base_data['location'],
            "size":     base_data['size'],
            "buildings":    []
        }
        
        for b in base_data['actors']:
            result = line_match.search(b)
            
            if not result:
                raise Exception("No match for line %s in base data %s" % (b, base_data))
            
            # Assign values from the string
            asterik, amount, actor_type = result.groups()
            if amount == None: amount = 1
            
            # Save as items ready to be mapped
            for i in range(int(amount)):
                base_setup['buildings'].append([actor_type, None])
        
        self.bases[base_name] = base_setup
    
    def inspect_bases(self):
        buildings_missing = []
        
        # First find out which buildings we are missing
        for base_name, base_data in self.bases.items():
            base_area = (
                base_data['location'][0] - base_data['size'][0],
                base_data['location'][1] - base_data['size'][1],
                
                base_data['location'][0] + base_data['size'][0],
                base_data['location'][1] + base_data['size'][1],
            )
            
            buildings_needed = set([b[0] for b in base_data['buildings']])
            
            # Get all buildings within this base
            found_buildings = {}
            total_needed = {}
            for b in buildings_needed:
                found_buildings[b] = 0
                total_needed[b] = 0
            
            for b in base_data['buildings']:
                if b[1] == None:
                    total_needed[b[0]] += 1
            
            # Loop through all actors and see what we've got
            for i, a in self.own_actors.items():
                if actor_lib.is_inside(a, base_area):
                    if a.actor_type in buildings_needed:
                        found_buildings[a.actor_type] += 1
            
            # Now find out what we are missing
            missing = {}
            for b in buildings_needed:
                m = total_needed[b] - found_buildings[b]
                if m > 0:
                    missing[b] = m
            
            # None missing? We can stop looking around now
            if missing == {}:
                print("Base complete!")
                continue
            
            # Now find out which builders we can use
            # Narrow down our list of builders so we don't later iterate over
            # non-builders more than once
            builders = []
            builders_used = []
            for aid, a in self.own_actors.items():
                if self.actor_types[a.actor_type]['can_construct']:
                    if a.current_order[0] == "stop":
                        builders.append(a)
            
            # Now we work out which buildings we can build and who is closest to it
            for building_type, amount in missing.items():
                for i in range(amount):
                    target_pos = base_data['location']
                    
                    closest_builder = None, 9999999
                    for b in builders:
                        if b in closest_builder: continue
                        if actor_lib.can_build(
                            self.actor_types[b.actor_type],
                            self.actor_types[building_type],
                            self.build_lists
                        ):
                            # If they are closest we want them to go build it
                            dist = vectors.distance(target_pos, b.pos)
                            
                            if dist < closest_builder[1]:
                                closest_builder = b, dist
                    
                    # Now remove them from the pool and issue the build order
                    if closest_builder[0] != None:
                        builders_used.append(closest_builder[0])
                        self.issue_orders(closest_builder[0].oid, cmd="build", pos=target_pos, target=building_type)
            
            
            
            
    
    def cycle(self):
        self.inspect_bases()
        
        for k in self.enemy_actors.keys(): first_enemy = k
        
        if self.actors_updated:
            if len(self.enemy_actors) > 0:
                for aid, a in self.own_actors.items():
                    if self.actor_types[a.actor_type]['does_damage']:
                        self.issue_orders(a.oid, cmd="attack", target=first_enemy)
            
            self.actors_updated = False
            


core_ai.register_ai("Basic computer", BasicComputerAI)
