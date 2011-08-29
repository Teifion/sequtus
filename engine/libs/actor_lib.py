from __future__ import division
import pygame
import vectors
import geometry
import drawing

def build_template_cache(template, engine):
    """Takes the template of the actor and creates some cache data"""
    
    if template['type'] == "building":
        template["acceleration"]    = 0
        template["deceleration"]    = 0
        template["turn_speed"]      = 0
        template["drifts"]          = False
        template["max_velocity"]    = 0
    
    temp_img = engine.images[template['image']]
    template['size'] = temp_img.get_rect().size

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
