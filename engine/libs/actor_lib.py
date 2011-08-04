from __future__ import division
import pygame
import vectors
import geometry

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

def handle_pathing_collision(a1, a2):
    a1_angle = vectors.angle(a1.velocity)
    a2_angle = vectors.angle(a2.velocity)
    
    # What sort of a collision is this?
    a_diff = abs(vectors.angle_diff(a1_angle, a2_angle)[0])
    
    if a1.is_moving and a2.is_moving:
        # Nearly the same direction
        if a_diff < 30:
            avg_angle = (a1_angle[0] + a2_angle[0])/2.0
            avg_pos = [(a1.pos[i] + a2.pos[i])/2.0 for i in range(3)]
            
            avg_move = vectors.move_to_vector([avg_angle, 0], 1000)
            avg_target = vectors.add_vectors(avg_pos, avg_move)
            
            a1_dist = vectors.distance(a1.pos, avg_target)
            a2_dist = vectors.distance(a2.pos, avg_target)
            
            if a1_dist < a2_dist:
                a2.pause(10)
                a2.dont_collide_with[a1.aid] = 10
            else:
                a1.pause(10)
                a1.dont_collide_with[a2.aid] = 10
            
        # Right angle
        elif a_diff < 150:
            # Now we tell a1 to reverse and a2 to pause a moment while
            # a1 moves out of the way
            a1.reverse(0, 15)
            a2.pause(2)
            
        # Opposite directions
        else:
            _sidestep_collision_resolution(a1, a2)
        
    else:
        if a1.is_moving():
            # If a2 is sitting around doing nothing then move it out the way
            if a2.max_velocity > 0 and a2.current_action() == ["stop", -1]:
                _sidestep_collision_resolution(a1, a2)
            else:
                # a2 is sitting on our target spot, so we stop
                if _will_collide(a1, a2):
                    a1.next_order()
                else:
                    print("busy")
                    # a2 can't move or is busy doing something else
        
        elif a2.is_moving():
            if a1.max_velocity > 0 and a1.current_action() == ["stop", -1]:
                _sidestep_collision_resolution(a2, a1)
            else:
                if _will_collide(a2, a1):
                    a2.next_order()
                else:
                    print("busy")

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
    a2.insert_order_queue([("reverse", target), ("stop", 10)])
    
    # Pause a1 to let a2 get out the way
    a1.pause(10)

def _will_collide(a1, a2):
    """Answers if a2 will collide with a1's movement target"""
    target = a1.current_action()[1]
    target_rect = pygame.Rect((0, 0, a1.rect.width, a1.rect.height))
    
    target_rect.left = target[0] - a1.rect.width/2
    target_rect.top = target[1] - a1.rect.height/2
    
    return geometry.rect_collision(target_rect, a2.rect)
