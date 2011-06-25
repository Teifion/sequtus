import math

# Combines two lists
def add_vectors(vec1, vec2):
    if type(vec2) == float or type(vec2) == int:
        vec2 = [vec2, vec2]
    
    try:
        return [vec1[i] + vec2[i] for i in range(len(vec1))]
    except Exception as e:
        print("Vec1: %s" % str(vec1))
        print("Vec2: %s" % str(vec2))
        raise

def multiply_vectors(vec1, vec2):
    if type(vec2) == float or type(vec2) == int:
        vec2 = [vec2, vec2]
    
    return [vec1[i] * vec2[i] for i in range(len(vec1))]

def sub_vectors(vec1, vec2):
    if type(vec2) == float or type(vec2) == int:
        vec2 = [vec2, vec2]
    
    return [vec1[i] - vec2[i] for i in range(len(vec1))]

def total_velocity(velocity):
    x, y = velocity
    return math.sqrt(x*x + y*y)

def bound_angle(angle):
    """returns an angle between 0 and 360"""
    while angle >= 360: angle -= 360
    while angle < 0: angle += 360
    return angle

def move_to_vector(angle, distance):
    """Takes an angle and a distance turning it into a vector"""
    angle = bound_angle(angle)
    
    # Needed or we get some bounding errors
    if angle == 0:      return [0, -distance, 0]
    if angle == 90:     return [distance, 0, 0]
    if angle == 180:    return [0, distance, 0]
    if angle == 270:    return [-distance, 0, 0]
    
    # SOH CAH TOA
    # x = opposite
    # y = adjacent
    x = math.sin(math.radians(angle)) * distance
    y = math.cos(math.radians(angle)) * distance
    z = 0
    
    return [x, -y, z]

def vector_to_move(vector):
    """Takes a vector and returns an angle and distance"""
    return angle([0,0,0], vector), total_velocity(vector)

def angle(pos1, pos2):
    """Gets the angle to go from pos1 to pos2"""
    # SOH CAH TOA
    # We have the opposite and adjacent
    x = abs(pos1[0] - pos2[0])
    y = abs(pos1[1] - pos2[1])
    
    # Exacts, because in these cases we get a divide by 0 error
    if x == 0:
        if pos1[1] >= pos2[1]:# Up
            return 0
        elif pos1[1] < pos2[1]:# Down
            return 180
    elif y == 0:
        if pos1[0] <= pos2[0]:# Right
            return 90
        elif pos1[0] > pos2[0]:# Left
            return 270
    else:
        # Using trig
        if pos1[1] > pos2[1]:# Up
            if pos1[0] < pos2[0]:# Right
                return math.degrees(math.atan(x/y))
            else:# Left
                return math.degrees(math.atan(y/x)) + 270
        else:# Down
            if pos1[0] < pos2[0]:# Right
                return math.degrees(math.atan(y/x)) + 90
            else:# Left
                return math.degrees(math.atan(x/y)) + 180

def distance(pos1, pos2):
    """Get the distance between two points"""
    x = abs(pos1[0] - pos2[0])
    y = abs(pos1[1] - pos2[1])
    
    return math.sqrt(x*x + y*y)

# def compare_vectors(vel1, vel2):
#   """
#   Returns a the difference between the two angles, if the two vectors collide then was it head on or side to side?
#   
#   Doesn't work correctly for angles that are closest over the 360 degree mark
#   """
#   a1 = vector_to_move(vel1)[0][0]
#   a2 = vector_to_move(vel2)[0][0]
#   
#   return abs(a1-a2)


