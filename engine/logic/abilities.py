import random

from engine.logic import effects, bullets
from engine.libs import vectors, actor_lib, math_lib

def _convert_dict(d):
    out = {}
    
    for k, v in d.items():
        out[str(k)] = v
    
    return out

class Ability (object):
    """An ability is an action that a unit can perform (shooting, building etc)"""
    
    required_charge = 20
    charge_rate = 1
    weapon = False
    
    # Flags for order types
    defence_flags = []
    offence_flags = []
    
    def __init__(self, actor, ability_data={}):
        super(Ability, self).__init__()
        self.actor = actor
        
        self.set_stats(ability_data)
        self.charge = self.required_charge
    
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
    weapon = True
    
    offence_flags = ["attack"]
    
    def can_use(self, target=None, **kwargs):
        if not super(WeaponAbility, self).can_use(target, **kwargs):
            return False
        
        if vectors.distance(self.actor.pos, target.pos) > self.max_range:
            return False
        
        if self.min_range > 0:
            if vectors.distance(self.actor.pos, target.pos) < self.min_range:
                return False
        
        if self.actor.team == target.team:
            return False
        
        return True

class ConstructionAbility (Ability):
    min_range = 0
    max_range = 10
    
    construction_rate = 0
    
    defence_flags = ["construct"]
    
    def can_use(self, target=None, **kwargs):
        if not super(ConstructionAbility, self).can_use(target, **kwargs):
            return False
        
        if vectors.distance(self.actor.pos, target.pos) > self.max_range:
            return False
        
        if self.min_range > 0:
            if vectors.distance(self.actor.pos, target.pos) < self.min_range:
                return False
        
        if self.actor.team != target.team:
            return False
        
        # Is the ally still under construction?
        if target.completion >= 100:
            return False
        
        return True
    
    def use(self, target):
        target.completion += (self.construction_rate * target.construction_rate)
        target.hp += (self.construction_rate * target.construction_heal_rate)
        
        self.generate_effect(target)
        
        self.charge = 0
    
    def generate_effect(self, target):
        colour = [self.effect['colour'][i] + random.random() * self.effect['variation'][i] for i in range(3)]
        
        the_effect = effects.Beam(
            origin=self.actor.pos,
            target=target.pos,
            colour=effects.bound_colour(colour),
            duration=self.required_charge-1,
        )
        self.actor.effects.append(the_effect)

class RepairAbility (Ability):
    max_range = 10
    
    repair_rate = 0
    
    defence_flags = ["repair"]
    
    def can_use(self, target=None, **kwargs):
        if not super(RepairAbility, self).can_use(target, **kwargs):
            return False
        
        if vectors.distance(self.actor.pos, target.pos) > self.max_range:
            return False
        
        if self.min_range > 0:
            if vectors.distance(self.actor.pos, target.pos) < self.min_range:
                return False
        
        if self.actor.team != target.team:
            return False
        
        # Is the ally still under construction?
        if target.completion < 100:
            return False
        
        # Is the ally hurt?
        if target.hp >= target.max_hp:
            return False
        
        return True
    
    def use(self, target):
        target.hp += (self.repair_rate * target.repair_rate)
        target.hp = min(target.hp, target.max_hp)
        self.generate_effect(target)
        
        self.charge = 0
    
    def generate_effect(self, target):
        colour = [self.effect['colour'][i] + random.random() * self.effect['variation'][i] for i in range(3)]
        
        the_effect = effects.Beam(
            origin=self.actor.pos,
            target=target.pos,
            colour=effects.bound_colour(colour),
            duration=self.required_charge-1,
        )
        self.actor.effects.append(the_effect)


class InstantHitWeapon (WeaponAbility):
    """Weapons that instantly hit their target such as lasers"""
    
    effect = {}
    damage = {"raw":1}
    
    def use(self, target):
        if target.team == self.actor.team:
            return False
        
        actor_lib.apply_damage(target, self.damage)
        self.generate_effect(target)
        
        self.charge = 0

class ProjectileWeapon (WeaponAbility):
    """Weapons that fire a bullet that takes time to reach it's target"""
    
    bullet = {}
    
    def use(self, target):
        if target.team == self.actor.team:
            return False
        
        self.generate_bullet(target)
        self.charge = 0

class MassDriver (ProjectileWeapon):
    def generate_bullet(self, target):
        if type(target) == list or type(target) == tuple:
            direction = vectors.angle(self.actor.pos, target)
            target_pos = target
        else:
            direction = vectors.angle(self.actor.pos, target.pos)
            target_pos = target.pos
        
        velocity = vectors.move_to_vector(direction, self.bullet['velocity'])
        velocity[2] = math_lib.calc_trajectory(0.1, vectors.distance(self.actor.pos, target_pos), self.bullet['velocity'])
        
        the_bullet = bullets.Shell(
            pos=self.actor.pos,
            velocity=velocity,
            image = self.bullet['image'],
            size = self.bullet['size'],
            blast_radius = self.bullet['blast_radius'],
            damage = self.bullet['damage'],
            dissipation_func = self.bullet.get('dissipation_func', "linear"),
        )
        self.actor.bullets.append(the_bullet)

class BeamWeapon (InstantHitWeapon):
    def generate_effect(self, target):
        the_effect = effects.Beam(
            origin=self.actor.pos,
            target=target.pos,
            colour=self.effect['colour'],
            duration=self.effect['duration'],
            degrade=self.effect.get("degrade", (0,0,0)),
        )
        self.actor.effects.append(the_effect)

lookup = {
    "BeamWeapon":   BeamWeapon,
    "MassDriver":   MassDriver,
    
    "Construction": ConstructionAbility,
    "Repair": RepairAbility,
}
