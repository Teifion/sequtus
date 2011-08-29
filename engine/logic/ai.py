class AI (object):
    """An object for assigning actions to actors. In it's most basic
    incarnation it does things such as auto-assigning combat targets
    to actors that don't already have them. More advanced ones can
    run a whole team (computer opponent)."""
    
    def __init__(self, sim, team):
        super(AI, self).__init__()
        
        self.sim = sim
        self.team = team
        
        self.next_update = 0
        
        self.enemy_actors = []
    
    def update(self):
        self.next_update -= 1
        if self.next_update > 0: return
        
        self.enemy_actors = []
        
        for a in self.sim.actors:
            if a.team != self.team:
                self.enemy_actors.append(a)
        
        self.next_update = 10
    
    def update_actor(self, the_actor):
        if self.enemy_actors != []:
            the_actor.enemy_targets = [self.enemy_actors[0]]
        else:
            the_actor.enemy_targets = []