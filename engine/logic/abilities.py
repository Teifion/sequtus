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
    
    turn_speed = 360
    fire_arc = [360, 360]
    
    # Allows us to ignore the Z facing for things like
    # catapults that need to aim high to hit targets
    ignore_z_facing = False
    
    # The location relative to our host that we draw from
    effect_offset = [0,0,0]
    
    # These are used by the system as it's easier to calculate
    # using these when actors are rotated etc but it's easier
    # for a person to define where on the model it's fired from
    # using an absolute X and Y
    _offset_distance = 0
    _offset_angle = 0
    
    image = None
    image_offset = [0,0,0]
    
    def __init__(self, actor, ability_data={}):
        super(Ability, self).__init__()
        self.actor = actor
        self.facing = [0,0]
        
        self.set_stats(ability_data)
        self.charge = self.required_charge
        
        self._offset_distance = vectors.distance(self.effect_offset)
        self._offset_angle = vectors.angle(self.effect_offset)
    
    def set_stats(self, ability_data):
        for k, v in ability_data.items():
            if k == "type": continue
            setattr(self, k, v)
    
    def turn(self, target_facing):
        """Turn's the ability towards a specific facing, returns True
        if the facing is achieved"""
        
        # This allows us to cut out all the below stuff if we have a
        # 360 degree fire-arc
        if self.fire_arc == [360, 360]:
            return True
        
        xy_diff, z_diff = vectors.angle_diff(self.facing, target_facing)
        
        # If it's within a certain range then BOOM, we're there
        if abs(xy_diff) <= self.turn_speed:
            if abs(z_diff) < self.turn_speed:
                self.facing = target_facing
                return True
        
        # XY first
        if xy_diff >= 0:
            self.facing[0] += self.turn_speed
        else:
            self.facing[0] -= self.turn_speed
        
        # Now for Z
        if z_diff >= 0:
            self.facing[1] += self.turn_speed
        else:
            self.facing[1] -= self.turn_speed
        
        self.facing = vectors.bound_angle(self.facing)
        return False
    
    def check_aim(self, target_facing):
        """Checks to see if we are pointing in the right direction to use
        the ability"""
        
        # This allows us to cut out all the below stuff if we have a
        # 360 degree fire-arc
        if self.fire_arc == [360, 360]:
            return True
        
        xy_diff, z_diff = vectors.angle_diff(self.facing, target_facing)
        
        if abs(xy_diff) < self.turn_speed:
            if abs(z_diff) < self.turn_speed or self.ignore_z_facing:
                return True
        
        return False
    
    def update(self):
        self.charge += self.charge_rate
    
    def can_use(self, target=None, **kwargs):
        """Called to see if the ability can be used"""
        if self.charge < self.required_charge:
            return False
        
        # Check aim
        if type(target) in (list, tuple):
            target_facing = vectors.angle(self.actor.pos, target)
        else:
            target_facing = vectors.angle(self.actor.pos, target.pos)
        
        if not self.check_aim(target_facing):
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
        # Just incase there are multiple sources building it
        # we don't want to run "next_order" several times
        if target.completion >= 100: return
        
        target.completion += (self.construction_rate * target.construction_rate)
        target.hp += (self.construction_rate * target.construction_heal_rate)
        
        self.generate_effect(target)
        
        if target.completion >= 100:
            target.next_order()
        
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
            origin=vectors.add_vectors(self.actor.pos, self.effect_offset),
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
        # Set correct origin
        offset_angle = vectors.bound_angle(
            vectors.add_vectors(self._offset_angle, self.facing)
        )
        
        origin_pos = vectors.add_vectors(
            self.actor.pos,
            vectors.move_to_vector(offset_angle, self._offset_distance)
        )
        
        # Get actual velocity we'll be using
        if type(target) == list or type(target) == tuple:
            direction = vectors.angle(origin_pos, target)
            target_pos = target
        else:
            direction = vectors.angle(origin_pos, target.pos)
            target_pos = target.pos
        
        velocity = vectors.move_to_vector(direction, self.bullet['velocity'])
        velocity[2] = math_lib.calc_trajectory(0.1, vectors.distance(self.actor.pos, target_pos), self.bullet['velocity'])
        
        the_bullet = bullets.Shell(
            pos=origin_pos,
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
        offset_angle = vectors.bound_angle(
            vectors.add_vectors(self._offset_angle, self.facing)
        )
        
        origin_pos = vectors.add_vectors(
            self.actor.pos,
            vectors.move_to_vector(offset_angle, self._offset_distance)
        )
        
        the_effect = effects.Beam(
            origin=origin_pos,
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
