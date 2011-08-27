class Ability (object):
    """An ability is an action that a unit can perform (shooting, building etc)"""
    
    required_charge = 100
    
    def __init__(self):
        super(Ability, self).__init__()
        self.charge = 0
    
    def update(self):
        self.charge += 1
    
    def can_use(self, target, **kwargs):
        """Called to see if the ability can be used"""
        return True
    
    def use(self):
        if self.charge < self.required_charge:
            return False, "Lack of charge"
    
    def action(self):
        raise Exception("%s has not implemented action()")

class InstantHitWeapon (Ability):
    """Weapons that instantly hit their target such as lasers"""
    
    min_range = 1
    max_range = 10
    
    damage = {"raw":1}
    effect = None

class ProjectileWeapon (Ability):
    """Weapons that fire a bullet that takes time to reach it's target"""
    
    min_range = 1
    max_range = 10
    bullet = ""