import math

# Combines two lists
def add_vectors(vec1, vec2):
    if type(vec2) == float or type(vec2) == int:
        vec2 = [vec2, vec2, vec2]
    
    try:
        return [vec1[i] + vec2[i] for i in range(len(vec1))]
    except Exception as e:
        print("Vec1: %s" % str(vec1))
        print("Vec2: %s" % str(vec2))
        raise

def multiply_vectors(vec1, vec2):
    if type(vec2) == float or type(vec2) == int:
        vec2 = [vec2, vec2, vec2]
    
    return [vec1[i] * vec2[i] for i in range(len(vec1))]

def divide_vectors(vec1, vec2):
    if type(vec2) == float or type(vec2) == int:
        vec2 = [vec2, vec2, vec2]
    
    return [vec1[i] / vec2[i] for i in range(len(vec1))]

def sub_vectors(vec1, vec2):
    if type(vec2) == float or type(vec2) == int:
        vec2 = [vec2, vec2, vec2]
    
    return [vec1[i] - vec2[i] for i in range(len(vec1))]

def total_velocity(velocity):
    if len(velocity) == 3:
        x, y, z = velocity
        
        a = math.sqrt(x*x + y*y)
        return math.sqrt(a*a + z*z)
    else:
        x, y = velocity
        return math.sqrt(x*x + y*y)

def bound_angle(angle):
    if type(angle) == list or type(angle) == tuple:
        return [bound_angle(angle[0]), bound_angle(angle[1])]
    
    while angle >= 360: angle -= 360
    while angle < 0: angle += 360
    return angle

def angle_diff(angle1, angle2):
    """Gives the amount you need to turn by to get from angle1 to angle2
    
    will provide a minus number if you turn counter-clockwise"""
    
    if type(angle1) == list or type(angle1) == tuple:
        return [angle_diff(angle1[0], angle2[0]), angle_diff(angle1[1], angle2[1])]
    
    # Distance going right
    if angle1 > angle2:# We cross 360
        right = angle2 - angle1 + 360
    else:
        right = angle2 - angle1
    
    # Distance going left
    if angle2 > angle1:# We cross 360
        left = angle1 - angle2 + 360
    else:
        left = angle1 - angle2
    
    # Now return the shortest path
    if abs(right) < abs(left):
        return right
    else:
        return -left

def move_to_vector(angle, distance):
    """
    distance is the 3D line going from origin at angles a1 and a2 (contained as the variable angle)
    we must first break it down into the vertical plane to determine the length of the 2D hypotenuse (h)
    
    h is the adjacent to our 3D angle which leaves z as the opposite
    """
    angle = bound_angle(angle)
    
    # First we get the vertical plane
    z, h = _move_to_vector_2d(angle[1], distance)
    
    # Hypotenuse cannot be negative in length
    h = abs(h)
    
    # Now horrizontal
    x, y = _move_to_vector_2d(angle[0], h)
    
    return x, y, z

def _move_to_vector_2d(angle, distance):
    """Returns an opposite and adjacent from the triangle"""
    
    if angle == 0:      return 0, -distance
    if angle == 90:     return distance, 0
    if angle == 180:    return 0, distance
    if angle == 270:    return -distance, 0
    
    opp = math.sin(math.radians(angle)) * distance
    adj = math.cos(math.radians(angle)) * distance
    
    return opp, -adj

def vector_to_move(vector):
    return angle([0,0,0], vector), total_velocity(vector)

# Gets the angle to go from 1 to 2, first item is 2D angle, 2nd return is the Z angle
def angle(pos1, pos2):
    # SOH CAH TOA
    # We have the opposite and adjacent
    x = abs(pos1[0] - pos2[0])
    y = abs(pos1[1] - pos2[1])
    z = abs(pos1[2] - pos2[2])
    
    # Exacts, because in these cases we get a divide by 0 error
    if x == 0:
        if pos1[1] >= pos2[1]:# Up
            xy = 0
        elif pos1[1] < pos2[1]:# Down
            xy = 180
    elif y == 0:
        if pos1[0] <= pos2[0]:# Right
            xy = 90
        elif pos1[0] > pos2[0]:# Left
            xy = 270
    else:
        # Using trig
        if pos1[1] > pos2[1]:# Up
            if pos1[0] < pos2[0]:# Right
                xy = math.degrees(math.atan(x/y))
            else:# Left
                xy = math.degrees(math.atan(y/x)) + 270
        else:# Down
            if pos1[0] < pos2[0]:# Right
                xy = math.degrees(math.atan(y/x)) + 90
            else:# Left
                xy = math.degrees(math.atan(x/y)) + 180
    
    # UP DOWN
    hyp = math.sqrt(x*x + y*y)
    if hyp > 0:
        za = math.atan(z/hyp)
    else:
        za = 0
    
    return xy, math.degrees(za)

def distance(pos1, pos2):
    x = abs(pos1[0] - pos2[0])
    y = abs(pos1[1] - pos2[1])
    
    a = math.sqrt(x*x + y*y)
    
    if len(pos1) == 3:
        z = abs(pos1[2] - pos2[2])
        return math.sqrt(a*a + z*z)
    
    return a

def compare_vectors(vel1, vel2):
    """
    Returns a the difference between the two angles, if the two vectors collide then was it head on or side to side?
    """
    a1 = vector_to_move(vel1)[0][0]
    a2 = vector_to_move(vel2)[0][0]
    
    return abs(a1-a2)

def get_midpoint(pos1, pos2, distance):
    """
    Given pos1 and pos2 it determines where pos1 will end up if it travels "distance" towards pos2.
    """
    a, za = angle(pos1, pos2)
    
    x = pos1[0] + (math.sin(math.radians(a)) * distance)
    y = pos1[1] - (math.cos(math.radians(a)) * distance)
    z = pos1[2] + (math.sin(math.radians(za)) * distance)
    
    return x,y,z
    
