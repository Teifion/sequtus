import multiprocessing

from engine.libs import vectors

ai_classes = {}
def register_class(class_name, class_template):
    if class_name not in ai_classes:
        ai_classes[class_name] = class_template
    else:
        raise KeyError("AI class %s already exists in the ai_classes" % class_name)

class AICore (object):
    """This forms the basis of an AI that runs a team."""
    
    def __init__(self, in_queue, out_queue):
        super(AICore, self).__init__()
        
        self.running = True
        self.team = None
        
        self.in_queue = in_queue
        self.out_queue = out_queue
        
        self.next_update = 0
        
        self.actors = {}
        self.terrain = {}
        
        self.data_handlers = {
            "_default": self._default_data_handler,
            "init":     self._init,
            "quit":     self._quit,
        }
    
    def read_queue(self):
        try:
            data = self.in_queue.get()
        except Exception as e:
            print("Error reading in from in_queue")
            raise
        
        cmd = data['cmd']
        kwargs = data.get('data', {})
        
        if cmd in self.data_handlers:
            self.data_handlers[cmd](**kwargs)
        else:
            self.data_handlers['_default'](cmd=cmd, **kwargs)
    
    def _default_data_handler(self, **kwargs):
        raise Exception("No handler for cmd: %s" % kwargs['cmd'])
    
    def _quit(self):
        self.running = False
    
    def _init(self, **kwargs):
        pass
    
    def cycle(self):
        """The central loop for the AI"""
        
        # If there's stuff in the queue then we'll read it in
        while not self.in_queue.empty():
            self.read_queue()
        
    
    def update(self):
        self.next_update -= 1
        if self.next_update > 0: return
        
        self.enemy_actors = []
        
        for a in self.sim.actors:
            if a.team != self.team:
                self.enemy_actors.append(weakref.ref(a)())
        
        self.next_update = 10
    
    def update_actor(self, the_actor):
        the_actor.enemy_targets = []
        
        for a in self.enemy_actors:
            dist = vectors.distance(a.pos, the_actor.pos)
            
            if dist <= the_actor.max_attack_range:
                the_actor.enemy_targets.append(a)

def _ai_process(ai_class, in_queue, out_queue):
    try:
        a = ai_class(in_queue, out_queue)
        
        while a.running:
            a.cycle()
        
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        raise

def make_ai(class_name):
    """Returns the ai in and out queues"""
    if class_name not in ai_classes:
        raise KeyError("No AI class by name of %s" % class_name)
    
    ai_in_queue = multiprocessing.Queue()
    ai_out_queue = multiprocessing.Queue()
    
    ai_class = ai_classes[class_name]
    
    p = multiprocessing.Process(target=_ai_process, args=(ai_class, ai_in_queue, ai_out_queue))
    p.start()
    
    return ai_in_queue, ai_out_queue


register_class("basic", AICore)