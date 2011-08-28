from pygame import draw, Rect

class Effect (object):
    """An effect is a purely visual item such as map marker or the
    after-glow from a laser beam."""
    
    duration = 1000000
    
    def __init__(self):
        super(Effect, self).__init__()
        self.age = 0
        
        self.left, self.right = 0, 0
        self.top, self.bottom = 0, 0
    
    def update(self):
        self.age += 1
        if self.age > self.duration:
            del(self)
    
    def draw(self, surface, offset):
        """Not called publicly, this draws the effect"""
        raise Exception("%s has not implemented draw(surface, offset)")

class Beam (Effect):
    def __init__(self, origin, target, colour, duration=None):
        super(Beam, self).__init__()
        self.origin = origin
        self.target = target
        self.colour = colour
        
        left = min(origin[0], target[0])
        top = min(origin[1], target[1])
        
        right = max(origin[0], target[0])
        bottom = max(origin[1], target[1])
        
        if duration: self.duration = duration
        
        self.rect = Rect(left, top, right-left, bottom-top)
        
        print("New beam")
    
    def draw(self, surface, offset):
        adjusted_origin = (self.origin[0] + offset[0], self.origin[1] + offset[1])
        adjusted_target = (self.target[0] + offset[0], self.target[1] + offset[1])
        
        draw.line(surface, self.colour, adjusted_origin, adjusted_target, 2)

