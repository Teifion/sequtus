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
    