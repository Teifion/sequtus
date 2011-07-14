import actors

class Building (actors.Actor):
    speed = 0
    
    def update(self):
        super(Building, self).update()
        self.velocity = [0,0]

class Walker (actors.Actor):
    pass

class Wheeled (actors.Actor):
    pass

class Winged (actors.Actor):
    pass

class VTOL (actors.Actor):
    pass

class Ship (actors.Actor):
    pass

class Submarine (actors.Actor):
    pass

types = {
    "building":     Building,
    "walker":       Walker,
    "wheeled":      Wheeled,
    "winged":       Winged,
    "vtol":         VTOL,
    "ship":         Ship,
    "submarine":    Submarine,
}
