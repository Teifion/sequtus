from __future__ import division

import pygame
from engine.libs import vectors, geometry, drawing

class StrippedActor (object):
    pass
        
attribs = (
    "team", "velocity", "pos", "facing", "actor_type",
    "oid", "hp", "completion",
    "offence_flags", "defence_flags")

# Things I don't think we need but might
# self.rally_orders = []
# self.micro_orders = []

def strip_actor(the_actor):
    sa = StrippedActor()
    
    for a in attribs:
        setattr(sa, a, getattr(the_actor, a))
    
    # Orders can contain a target and we don't want to pass around a
    # reference to a whole actor by mistake
    def _strip_order(order):
        cmd, pos, target = order
        
        if target != None:
            if type(target) != int:
                target = target.oid
        
        return cmd, pos, target
    
    sa.current_order = _strip_order(the_actor.current_order)
    sa.order_queue = [_strip_order(o) for o in the_actor.order_queue]
    
    return sa

def build_template_cache(template, engine):
    """Takes the template of the actor and creates some cache data"""
    
    template["uses_build_queue"] = False
    
    # Template of a template?
    if template['type'] == "building":
        template["uses_build_queue"]= True
        template["acceleration"]    = 0
        template["deceleration"]    = 0
        template["turn_speed"]      = 0
        template["drifts"]          = False
        template["max_velocity"]    = 0
    
    template['does_damage'] = False
    template['can_construct'] = False
    template['can_repair'] = False
    
    max_attack_range = 0
    minmax_attack_range = 99999
    
    max_heal_range = 0
    minmax_heal_range = 99999
    
    for a in template['abilities']:
        ability_type = engine.current_screen.ability_types[a]
        ability_damage = {}
        
        # Markers for the AIs
        if ability_type.get('construction_rate', 0) > 0:
            template['can_construct'] = True
        
        if ability_type.get('repair_rate', 0) > 0:
            template['can_repair'] = True
        
        if "damage" in ability_type:
            ability_damage = ability_type['damage']
            template['does_damage'] = True
        elif "bullet" in ability_type:
            if "damage" in ability_type['bullet']:
                ability_damage = ability_type['bullet']['damage']
                template['does_damage'] = True
        
        if "max_range" in ability_type:
            if ability_damage != {}:
                max_attack_range = max(max_attack_range, ability_type['max_range'])
                minmax_attack_range = min(minmax_attack_range, ability_type['max_range'])
            else:
                max_heal_range = max(max_heal_range, ability_type['max_range'])
                minmax_heal_range = min(minmax_heal_range, ability_type['max_range'])
    
    if minmax_attack_range == 99999:
        minmax_attack_range = 0
    
    if minmax_heal_range == 99999:
        minmax_heal_range = 0
    
    template['optimum_attack_range']    = minmax_attack_range
    template['max_attack_range']        = max_attack_range
    
    template['optimum_heal_range']      = minmax_heal_range
    template['max_heal_range']          = max_heal_range
    
    # Construction/Repair
    template['construction_cost']       = template.get('construction_cost', {})
    template['repair_cost']             = template.get('repair_cost', {})
    
    template['construction_rate']   = template.get('construction_rate', 1)
    template['repair_rate']         = template.get('repair_rate', 1)
    
    construction_cycles = 100/template['construction_rate']
    repair_cycles = template['max_hp']/template['repair_rate']
    
    template['_part_construction_cost'] = {}
    for k, v in template['construction_cost'].items():
        template['_part_construction_cost'][k] = v/construction_cycles
    
    template['_part_repair_cost'] = {}
    for k, v in template['repair_cost'].items():
        template['_part_repair_cost'][k] = v/repair_cycles
    
    if "image" in template:
        temp_img = engine.images[template['image']]
        template['size'] = temp_img.get_rect().size
    else:
        template['size'] = [0,0]

def apply_damage(the_actor, damage):
    """Applies damage to the actor, returns the alive status of the actor
    True meaning that the actor is still alive."""
    
    for k, v in damage.items():
        the_actor.hp -= v
    
    return the_actor.hp <= 0


# Trying out a new method
def handle_pathing_collision(a1, a2):
    if a1.max_velocity > 0 and a2.max_velocity > 0:
        _bounce_both(a1, a2)
    elif a1.max_velocity <= 0:
        _bounce_one(a2, a1)
    elif a2.max_velocity <= 0:
        _bounce_one(a1, a2)
    else:
        raise Exception("Neither actor can move")

def _bounce_one(a1, a2):
    # Bounces a1
    dir_angle = vectors.angle(a2.pos, a1.pos)
    
    vel_angle = vectors.angle(a1.velocity)
    
    # If they are head on then we want to swivel them a little
    if vectors.bound_angle(dir_angle[0]+180) == vel_angle[0]:
        dir_angle[0] = vectors.bound_angle(dir_angle[0] + 40)
    
    # Keep trying distances further and further apart until they're
    # not going to be overlapping any more
    overlapping = True
    dist = vectors.total_velocity(a1.velocity)
    
    a2_rect = (a2.pos[0], a2.pos[1], a2.size[0], a2.size[1])
    
    while overlapping:
        new_pos = vectors.add_vectors(a1.pos, vectors.move_to_vector(
            dir_angle, dist
        ))
        
        new_rect = (new_pos[0], new_pos[1], a1.size[0], a1.size[1])
        
        if not geometry.rect_collision(new_rect, a2_rect, True):
            overlapping = False
        
        dist += 1
    
    # Add a bit to be safe
    new_pos = vectors.add_vectors(a1.pos, vectors.move_to_vector(
        dir_angle, dist + vectors.total_velocity(a1.velocity)
    ))
    
    a1.pos = new_pos

def _bounce_both(a1, a2):
    # These are the angles directly away from each other
    angle1 = vectors.angle(a2.pos, a1.pos)
    angle2 = vectors.angle(a1.pos, a2.pos)
    
    vel_angle1 = vectors.angle(a1.velocity)
    vel_angle2 = vectors.angle(a2.velocity)
    
    # If they are head on then we want to swivel them a little
    if vel_angle1[0] == angle2[0] and vel_angle2[0] == angle1[0]:
        angle1[0] = vectors.bound_angle(angle1[0] + 20)
        angle2[0] = vectors.bound_angle(angle2[0] + 20)
    
    # Keep trying distances further and further apart until they're
    # not going to be overlapping any more
    overlapping = True
    dist_multiplier = 0.1
    
    while overlapping:
        dist_multiplier += 0.1
        
        new_pos1 = vectors.add_vectors(a1.pos, vectors.move_to_vector(
            angle1, max(a1.size) * dist_multiplier
        ))
        
        new_pos2 = vectors.add_vectors(a2.pos, vectors.move_to_vector(
            angle2, max(a2.size) * dist_multiplier
        ))
        
        new_rect1 = (new_pos1[0], new_pos1[1], a1.size[0], a1.size[1])
        new_rect2 = (new_pos2[0], new_pos2[1], a2.size[0], a2.size[1])
        
        if not geometry.rect_collision(new_rect1, new_rect2):
            overlapping = False
    
    a1.pos = new_pos1
    a2.pos = new_pos2

def _will_collide(a1, a2, target=None):
    """Answers if a2 will collide with a1's movement target"""
    if not target:
        target = a1.current_action()[1]
    
    target_rect = pygame.Rect((0, 0, a1.rect.width, a1.rect.height))
    
    target_rect.left = target[0] - a1.rect.width/2
    target_rect.top = target[1] - a1.rect.height/2
    
    return geometry.rect_collision(target_rect, a2.rect, convert=True)

def can_build(actor_type, item_type, build_lists):
    """Discovers if this actor has the pre-reqs to build the item"""
    
    # Check for tech requirements
    if item_type.get('required_techs', []) != []:
        raise Exception("No handler for required techs in a unit")
    
    # Now we go through all the build lists we have and see if our
    # build request is in one of them
    for f in actor_type['flags']:
        if f in build_lists:
            if item_type['name'] in build_lists[f]:
                return True
    
    return False

def contains_point(the_actor, point):
    """Point is a length 2 sequence X, Y"""
    left = the_actor.pos[0] - the_actor.rect.width/2
    right = the_actor.pos[0] + the_actor.rect.width/2
    
    top = the_actor.pos[1] - the_actor.rect.height/2
    bottom = the_actor.pos[1] + the_actor.rect.height/2
    
    if left <= point[0] <= right:
        if top <= point[1] <= bottom:
            return True

def is_inside(the_actor, rect):
    if rect[0] <= the_actor.pos[0] <= rect[2]:
        if rect[1] <= the_actor.pos[1] <= rect[3]:
            return True
