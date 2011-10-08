import re
import traceback
import sys

from engine.ai import core_ai

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
        
        print(self.bases)
    
    def _save_base(self, base_name, base_data):
        base_setup = {
            "location": base_data['location'],
            "size":     base_data['size'],
            "buildings":    []
        }
        
        for b in base_data['buildings']:
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
        for base_name, base_data in self.bases.items():
            for b in base_data['buildings']:
                pass
            
    
    def cycle(self):
        for k in self.enemy_actors.keys(): first_enemy = k
        
        if self.actors_updated:
            if len(self.enemy_actors) > 0:
                for aid, a in self.own_actors.items():
                    if self.actor_types[a.actor_type]['does_damage']:
                        self.issue_orders(a.oid, cmd="attack", target=first_enemy)
            
            self.actors_updated = False
            


core_ai.register_ai("Basic computer", BasicComputerAI)