

class Team (object):
    """An object storing information on what a team is/has"""
    def __init__(self, team_id, battle_sim):
        super(Team, self).__init__()
        
        self.resources = {}
        for k in battle_sim.resources.keys():
            self.resources[k] = 0
        
        self.sim        = battle_sim
        self.team_id    = team_id
        
        self.colour = None
        
    def can_afford(self, cost):
        for k, v in cost.items():
            if self.resources[k] < v:
                return False
        return True
    
    def spend(self, cost):
        for k, v in cost.items():
            self.resources[k] -= v
    
    def apply_data(self, data):
        """Takes starting data (resources, techs etc) and sets their values"""
        
        if "resources" in data:
            for k, v in data['resources'].items():
                self.resources[k] = v
        
        if "colour" in data:
            self.colour = data['colour']


def multiply_cost(cost, magnitude):
    new_cost = {}
    for k, v in cost.items():
        new_cost[k] = v * magnitude
    return new_cost
