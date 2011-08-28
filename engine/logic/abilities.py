from engine.logic import effects
from engine.libs import vectors, actor_lib

def _convert_dict(d):
    out = {}
    
    for k, v in d.items():
        out[str(k)] = v
    
    return out

class Ability (object):
    """An ability is an action that a unit can perform (shooting, building etc)"""
    
    required_charge = 20
    charge_rate = 1
    
    def __init__(self, actor, ability_data={}):
        super(Ability, self).__init__()
        self.charge = 0
        self.actor = actor
        
        self.set_stats(ability_data)
    
    def set_stats(self, ability_data):
        for k, v in ability_data.items():
            if k == "type": continue
            setattr(self, k, v)
        
    
    def update(self):
        self.charge += self.charge_rate
    
    def can_use(self, target=None, **kwargs):
        """Called to see if the ability can be used"""
        if self.charge < self.required_charge:
            return False
        
        return True
    
    def use(self, **kwargs):
        raise Exception("%s has not implemented use()")
    
    def generate_effect(self, **kwargs):
        raise Exception("%s has not implemented generate_effect()")

class WeaponAbility (Ability):
    min_range = 0
    max_range = 10
    
    def can_use(self, target=None, **kwargs):
        """Called to see if the ability can be used"""
        if self.charge < self.required_charge:
            return False
        
        if vectors.distance(self.actor.pos, target.pos) > self.max_range:
            return False
        
        if self.min_range > 0:
            if vectors.distance(self.actor.pos, target.pos) < self.min_range:
                return False
        
        return True
    

class InstantHitWeapon (WeaponAbility):
    """Weapons that instantly hit their target such as lasers"""
    
    damage = {"raw":1}
    
    def use(self, target):
        actor_lib.apply_damage(target, self.damage)
        self.generate_effect(target)
        
        self.charge = 0

class ProjectileWeapon (WeaponAbility):
    """Weapons that fire a bullet that takes time to reach it's target"""
    
    bullet = ""


class BeamWeapon (InstantHitWeapon):
    effect = {}
    
    def generate_effect(self, target):
        the_effect = effects.Beam(
            origin=self.actor.pos,
            target=target.pos,
            colour=self.effect['colour'],
            duration=self.effect['duration']
        )
        self.actor.effects.append(the_effect)

lookup = {
    "BeamWeapon": BeamWeapon,
    "ProjectileWeapon": ProjectileWeapon,
}