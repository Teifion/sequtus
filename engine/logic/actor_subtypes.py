import actors

class Building (actors.Actor):
    speed = 0
    
    def update(self):
        super(Building, self).update()
        self.velocity = [0,0,0]
    
    def issue_command(self, cmd, pos=None, target=None):
        if cmd == "move":
            self.rally_orders = [(cmd, pos, target)]
        else:
            super(Building, self).issue_command(cmd, pos, target)
    
    def append_command(self, cmd, pos=None, target=None):
        if cmd == "move":
            self.rally_orders.append((cmd, pos, target))
        else:
            super(Building, self).append_command(cmd, pos, target)

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
