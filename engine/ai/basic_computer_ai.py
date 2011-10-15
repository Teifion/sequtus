import re
import traceback
import sys
import random

from engine.ai import core_ai
from engine.libs import actor_lib, vectors

line_match = re.compile(r"(([0-9])\* )?(.*)")

buildings_in_progress_ttl = 1000

random.seed()

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
            "location":     base_data['location'],
            "size":         base_data['size'],
            "attacks":      {},
            "buildings":    [],
            
            "current_attack":           None,
            "current_buildings":        [],
            
            # Used to track buildings about to be started
            "buildings_in_progress":    [],
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
                base_setup['buildings'].append(actor_type)
            
        # Now do the same for the attacks
        for attack_id, attack in enumerate(base_data['attacks']):
            base_setup['attacks'][attack_id] = []
            for a in attack:
                result = line_match.search(a)
                
                if not result:
                    raise Exception("No match for line %s in base data %s" % (a, base_data))
                
                # Assign values from the string
                asterik, amount, actor_type = result.groups()
                if amount == None: amount = 1
                
                # Save as items ready to be mapped
                for i in range(int(amount)):
                    base_setup['attacks'][attack_id].append(actor_type)
        
        self.bases[base_name] = base_setup
    
    def inspect_bases(self):
        # First find out which buildings we are missing
        for base_name, base_data in self.bases.items():
            base_area = (
                base_data['location'][0] - base_data['size'][0],
                base_data['location'][1] - base_data['size'][1],
                
                base_data['location'][0] + base_data['size'][0],
                base_data['location'][1] + base_data['size'][1],
            )
            
            buildings_needed = set(base_data['buildings'])
            
            # Reset this now
            base_data['current_buildings'] = []
            
            # Get all buildings within this base
            found_buildings = {}
            total_needed = {}
            for b in buildings_needed:
                found_buildings[b] = 0
                total_needed[b] = 0
            
            for b in base_data['buildings']:
                total_needed[b] += 1
            
            # Loop through all actors and see what we've got
            for i, a in self.own_actors.items():
                if actor_lib.is_inside(a, base_area):
                    if a.actor_type in buildings_needed:
                        found_buildings[a.actor_type] += 1
                        
                        if a.completion >= 100:
                            base_data['current_buildings'].append(a.oid)
            
            # Now also loop through all the buildings_in_progress
            # Use a range loop so we can update the list as we go
            for i in range(len(base_data['buildings_in_progress'])-1, -1, -1):
                b, ttl = base_data['buildings_in_progress'][i]
                
                if ttl <= 0:
                    del(base_data['buildings_in_progress'][i])
                    continue
                
                base_data['buildings_in_progress'][i][1] -= 1
                
                if b in found_buildings:
                    found_buildings[b] += 1
            
            # Now find out what we are missing
            missing = {}
            for b in buildings_needed:
                m = total_needed[b] - found_buildings[b]
                if m > 0:
                    missing[b] = m
            
            # None missing? We can stop looking around now
            if missing == {}:
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
                        if b in builders_used: continue
                        if actor_lib.can_build(
                            builder_type = self.actor_types[b.actor_type],
                            item_type = self.actor_types[building_type],
                            build_lists = self.build_lists,
                        ):
                            # If they are closest we want them to go build it
                            dist = vectors.distance(target_pos, b.pos)
                            
                            if dist < closest_builder[1]:
                                closest_builder = b, dist
                    
                    # Now remove them from the pool and issue the build order
                    if closest_builder[0] != None:
                        builders_used.append(closest_builder[0])
                        self.issue_orders(closest_builder[0].oid, cmd="build", pos=target_pos, target=building_type)
                        
                        base_data['buildings_in_progress'].append([building_type, buildings_in_progress_ttl])
            
    def plan_attacks(self):
        for base_name, base_data in self.bases.items():
            
            # Has it already selected an attack?
            if base_data['current_attack'] != None:
                # TODO check to see if attack has been constructed
                self.construct_attack(base_name)
                continue
            
            # Find out which of the attacks it can make
            buildable_attacks = set()
            buildable_units = set()
            unbuildable_units = set()
            for attack_id, attacker_list in base_data['attacks'].items():
                cannot_build_attack = False
                
                for a in attacker_list:
                    if a in buildable_units:
                        continue
                    if a in unbuildable_units:
                        cannot_build_attack = True
                        continue
                    
                    is_buildable = False
                    for b in base_data['current_buildings']:
                        the_builder = self.own_actors[b].actor_type
                        if actor_lib.can_build(
                            builder_type = self.actor_types[the_builder],
                            item_type = self.actor_types[a],
                            build_lists = self.build_lists,
                        ):
                            is_buildable = True
                    
                    if is_buildable:
                        buildable_units.add(a)
                    else:
                        unbuildable_units.add(a)
                        cannot_build_attack = True
                
                if cannot_build_attack == True:
                    continue
                
                buildable_attacks.add(attack_id)
            
            # Pick an attack to build, it'll get sorted in the next logic cycle
            if len(buildable_attacks) > 0:
                a = random.choice(list(buildable_attacks))
                base_data['current_attack'] = a
    
    def construct_attack(self, base_name):
        the_base = self.bases[base_name]
        attacker_list = the_base['attacks'][the_base['current_attack']]
        
        missing = {}
        found = []
        for a in attacker_list:
            if a not in missing:
                missing[a] = 0
            missing[a] += 1
        
        # Find out what we've got in the base that fits into
        # the list of units we plan to attack with
        for a in the_base['current_buildings']:
            the_actor = self.own_actors[a]
            
            if the_actor.actor_type in missing:
                if missing[the_actor.actor_type] > 0:
                    missing[the_actor.actor_type] -= 1
                    found.append(a)
        
        # We now have a list of what we're missing
        total_missing = sum([v for k,v in missing.items()])
        
        if total_missing == 0:
            # Do stuff
            self.commence_attack(base_name, found)
        
        else:
            for a_type, amount in missing.items():
                pass
    
    def commence_attack(self, base_name, found_units):
        """docstring for commence_attack"""
        pass
        
    
    def cycle(self):
        self.inspect_bases()
        self.plan_attacks()
        
        for k in self.enemy_actors.keys(): first_enemy = k
        
        if self.actors_updated:
            if len(self.enemy_actors) > 0:
                for aid, a in self.own_actors.items():
                    if self.actor_types[a.actor_type]['does_damage']:
                        self.issue_orders(a.oid, cmd="attack", target=first_enemy)
            
            self.actors_updated = False
            


core_ai.register_ai("Basic computer", BasicComputerAI)
