"""
Module is designed to draw objects as HTML so as to give a visual idea
"""
import webbrowser

class DataObject (object):
    def __init__(self, x, y, width, height):
        super(DataObject, self).__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height

def _get_data(obj):
    if str(type(obj)) == "<type 'pygame.Rect'>":
        return DataObject(
            x = obj.left,
            y = obj.top,
            width = obj.width,
            height = obj.height,
        )
    elif str(type(obj)) in (
        "<class 'engine.logic.actor_subtypes.Walker'>",
        "<class 'engine.logic.actor_subtypes.Building'>"):
        return DataObject(
            x = obj.pos[0],
            y = obj.pos[1],
            width = obj.size[0],
            height = obj.size[1],
        )
    else:
        raise Exception("No handler for type(obj) == %s" % str(type(obj)))


def draw_objects(objects):
    output = []
    
    for o in objects:
        data_o = _get_data(o)
        
        output.append("""<div style="
            border:1px solid #000;
            position:absolute;
            top:    {y}px;
            left:   {x}px;
            width:  {width}px;
            height: {height}px;
            ">&nbsp;</div>""".format(
                x = data_o.x,
                y = data_o.y,
                width = data_o.width,
                height = data_o.height,
            ))
    
    return "".join(output)

def draw_and_view(objects):
    fpath = "/tmp/sequtus.html"
    
    with open(fpath, 'w') as f:
        f.write(draw_objects(objects))
    
    webbrowser.open(fpath)