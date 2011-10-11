from engine.libs import sim_lib

def send_static_data(screen, queue):
    """Used to send data such as the templates of units, stuff you only need to send once"""
    if type(queue) == list:
        for q in queue:
            send_static_data(screen, q)
        return
    
    if type(queue) == dict:
        for i, q in queue.items():
            send_static_data(screen, q)
        return
    
    # Send actor types
    queue.put({"cmd":"actor_types", "actor_types":dict(screen.actor_types)})
    
    # Send build lists
    queue.put({"cmd":"build_lists", "build_lists":dict(screen.build_lists)})

def place_actor(actor_list, building_rect, distance=100):
    if type(distance) == list:
        for d in distance:
            r = place_actor(actor_list, building_rect, d)
            if r != None:
                return r
        return None
    
    """Tests several positions for the building by nudging it around. This is
    because an AI may not always have the most recent positions for actors."""
    
    ox, oy = building_rect.left, building_rect.right
    
    nudges = (
        (0,0),
        
        (-1,-1),
        (-1,0),
        (-1,1),
        (0,-1),
        (0,1),
        (1,-1),
        (1,0),
        (1,1),
    )
    
    for x,y in nudges:
        building_rect.left = ox + x * distance
        building_rect.top = oy + y * distance
        
        if not sim_lib.test_possible_collision(actor_list, building_rect, True):
            return building_rect
    
    return None

