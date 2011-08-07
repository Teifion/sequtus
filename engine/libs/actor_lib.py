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

def _pass_around(act1, act2):
    """Issues micro orders to a1 and a2,
    the faster actor will pass around the other while the other pauses"""
    if act1.max_velocity >= act2.max_velocity:
        a1, a2 = act1, act2
    else:
        a1, a2 = act2, act1
    
    _step_around(a1, a2)
    
    a2.pause(30)
    a1.dont_collide_with[a2.aid] = 15

def handle_pathing_collision(a1, a2):
    if a1.is_moving() and a2.is_moving():
        a1_angle = vectors.angle(a1.velocity)
        a2_angle = vectors.angle(a2.velocity)
        
        # What sort of a collision is this?
        a_diff = abs(vectors.angle_diff(a1_angle, a2_angle)[0])
        
        # Very similar direction
        if a_diff < 30:
            _pass_around(a1, a2)
        
        # Right angle
        elif a_diff < 150:
            # Now we tell a1 to reverse and a2 to pause a moment while
            # a1 moves out of the way
            a1.reverse(0, 15)
            a2.pause(2)
            
        # Opposite directions
        else:
            _step_around(a1, a2)
            _step_around(a2, a1)
            a2.dont_collide_with[a1.aid] = 6
        
    elif not a1.is_moving() and not a2.is_moving():
        print("a1 = %s, a2 = %s" % (a1.aid, a2.aid))
        raise Exception("Neither actor is moving yet they are colliding")
        
    else:
        _handle_one_moving_collision(a1, a2)

def _handle_one_moving_collision(act1, act2):
    """A collision where only one party is moving
    a1 is set as the moving party"""
    if act1.is_moving():
        a1, a2 = act1, act2
    else:
        a1, a2 = act2, act1
    
    # Where is a1 trying to get?
    target = a1.get_move_target()
    
    # a2 cannot move
    if a2.max_velocity <= 0:
        # a2 is sitting on the ultimate target for a1
        if _will_collide(a1, a2, target):
            a1.next_order()
        else:
            _step_around(a1, a2)
        
    # a2 can move
    else:
        # a2 is sitting on the ultimate target for a1
        if _will_collide(a1, a2, target):
            angle = vectors.angle(a1.pos, a2.pos)
            
            # If it's a diagonal then they'll need to take that into account
            dist = max(max(a1.size), max(a2.size)) * 1.5
            
            a2_target = vectors.add_vectors(
                target,
                vectors.move_to_vector(angle, dist)
            )
            
            # Use reverse to show that it's moving in response to a collision
            a2.insert_order_queue([("move", a2_target)])
            a2.dont_collide_with[a1.aid] = 7
            
            # Pause a1 a moment to left a2 move
            a1.pause(7)
            
        else:
            pass
            # print("Step around (2)")
            # _sidestep_collision_resolution(a1, a2)

def _sidestep_collision_resolution(a1, a2):
    """
    Used when one actor has to move to the side to avoid another
    """
    side_angle = vectors.bound_angle((vectors.angle(a1.velocity)[0]+90, 0))
    
    target = vectors.add_vectors(
        a2.pos,
        vectors.move_to_vector(side_angle, 5 + max(a1.size)*1.2)
    )
    
    # Use reverse to show that it's moving in response to a collision
    a2.insert_order_queue([("move", target), ("stop", 10)])
    
    # Pause a1 to let a2 get out the way
    a1.pause(10)

def _step_around(a1, a2):
    """a1 is given order to step around a2"""
    angle = vectors.angle(a1.pos, a2.pos)[0]
    size = max(max(a1.size), max(a2.size))
    dist = max(a1.size) + max(a2.size)
    
    # First move directly away from a2
    target1 = vectors.add_vectors(
        vectors.move_to_vector([vectors.bound_angle(angle+180), 0], size),
        a2.pos
    )
    
    # Now move to a location that is 45 degrees around a2 from where a1 is
    target2 = vectors.add_vectors(
        vectors.move_to_vector([vectors.bound_angle(angle+180+45), 0], size*1.1),
        a2.pos
    )
    
    # Now to a location 45 + 90 degrees around a2 from a1
    target3 = vectors.add_vectors(
        vectors.move_to_vector([vectors.bound_angle(angle+180+90+45), 0], size*1.1),
        a2.pos
    )
    
    orders = [["move", target1], ["move", target2], ["move", target3]]
    
    a1.insert_order_queue(orders)
    a2.dont_collide_with[a1.aid] = 2

def _will_collide(a1, a2, target=None):
    """Answers if a2 will collide with a1's movement target"""
    if not target:
        target = a1.current_action()[1]
    
    target_rect = pygame.Rect((0, 0, a1.rect.width, a1.rect.height))
    
    target_rect.left = target[0] - a1.rect.width/2
    target_rect.top = target[1] - a1.rect.height/2
    
    return geometry.rect_collision(target_rect, a2.rect, convert=True)
