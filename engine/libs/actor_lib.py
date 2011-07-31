import vectors

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
    a_diff = vectors.angle_diff(a1_angle, a2_angle)[0]
    
    if a1.is_moving and a2.is_moving:
        # Nearly the same direction
        if a_diff < 30:
            pass
            
        # Right angle
        elif a_diff < 150:
            # Now we tell a1 to reverse and a2 to pause a moment while
            # a1 moves out of the way
            a1.reverse(0, 15)
            a2.pause(2)
            
        # Opposite directions
        else:
            pass
        
    else:
        if a1.is_moving:
            # If a2 is sitting around doing nothing then move it out the way
            if a2.max_velocity > 0 and a2.current_order == ["stop", -1]:
                side_angle = vectors.bound_angle((a1_angle[0]+90, 0))
                
                target = vectors.add_vectors(
                    a2.pos,
                    vectors.move_to_vector(side_angle, 5 + max(a1.size)*1.1)
                )
                
                a2.insert_order_queue([("reverse", target), ("stop", 5), ("move", a2.pos)])
                a1.pause(3)
                
                
            else:
                pass
                # a1 move around a2
            
        elif a2.is_moving:
            pass