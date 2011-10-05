

class Team (object):
    """An object storing information on what a team is/has"""
    def __init__(self, team_id, battle_sim):
        super(Team, self).__init__()
        self.resources = {}
        
        self.sim        = battle_sim
        self.team_id    = team_id
    
    def can_affort(self, cost):
        for k, v in cost.items():
            if self.resources[k] < v:
                return False
        return True
    
    def spend(self, cost):
        for k, v in cost.items():
            self.resources[k] -= v

