from pygame import draw, Rect

def bound_colour(colour):
    return [min(max(c, 0), 255) for c in colour]

class Effect (object):
    """An effect is a purely visual item such as map marker or the
    after-glow from a laser beam."""
    
    duration = 1000000
    
    def __init__(self):
        super(Effect, self).__init__()
        self.age = 0
        self.dead = False
        
        self.left, self.right = 0, 0
        self.top, self.bottom = 0, 0
    
    def update(self):
        self.age += 1
        if self.age > self.duration:
            self.dead = True
    
    def draw(self, surface, offset):
        """Not called publicly, this draws the effect"""
        raise Exception("%s has not implemented draw(surface, offset)")

class Beam (Effect):
    def __init__(self, origin, target, colour, duration=None, degrade=(0,0,0)):
        super(Beam, self).__init__()
        self.origin = origin
        self.target = target
        self.colour = colour
        
        self.degrade = degrade
        
        left = min(origin[0], target[0])
        top = min(origin[1], target[1])
        
        right = max(origin[0], target[0])
        bottom = max(origin[1], target[1])
        
        if duration: self.duration = duration
        
        self.rect = Rect(left, top, right-left, bottom-top)
    
    def draw(self, surface, offset):
        adjusted_origin = (self.origin[0] + offset[0], self.origin[1] + offset[1])
        adjusted_target = (self.target[0] + offset[0], self.target[1] + offset[1])
        
        real_colour = [self.colour[i] - self.degrade[i] * self.age for i in range(3)]
        
        draw.line(surface, bound_colour(real_colour), adjusted_origin, adjusted_target, 2)

class Explosion (Effect):
    def __init__(self, center, colour, radius, colour_change=(0,0,0), radius_change=0, duration=None):
        super(Explosion, self).__init__()
        self.colour = colour
        self.radius = radius
        self.colour_change = colour_change
        self.radius_change = radius_change
        self.center = center
        
        if duration: self.duration = duration
        
        self.rect = Rect(center[0]-radius, center[1]-radius, radius*2, radius*2)
        
    def draw(self, surface, offset):
        adjusted_center = (int(self.center[0] + offset[0]), int(self.center[1] + offset[1]))
        real_colour = [self.colour[i] + self.colour_change[i] * self.age for i in range(3)]
        
        # Typecast to an int to stop float warning
        radius = int(self.radius + self.radius_change * self.age)
        draw.circle(surface, bound_colour(real_colour), adjusted_center, radius, min(2, radius))
            
    
