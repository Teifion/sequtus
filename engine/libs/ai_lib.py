
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

