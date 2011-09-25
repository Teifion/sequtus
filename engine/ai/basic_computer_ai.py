from engine.ai import core_ai

class BasicComputerAI (core_ai.AICore):
    def cycle(self):
        if self.actors_updated:
            if len(self.enemy_actors) > 0:
                target = self.enemy_actors[0].oid
                
                for a in self.own_actors:
                    self.issue_orders(a.oid, cmd="attack", target=target)
            
            self.actors_updated = False
            


core_ai.register_ai("Basic computer", BasicComputerAI)