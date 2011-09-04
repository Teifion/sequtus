import sys
import time

def progressbar(it, prefix = "", size = 60, with_eta=False):
    """
    for i in progressbar(range(15), "Computing: ", 40):
         time.sleep(0.1) # long computation
    """
    
    count = len(it)
    start_time = time.time()
    
    def _show(_i):
        eta_string = ""
        if _i > 0:
            time_so_far = time.time() - start_time
            time_per_item = time_so_far / _i
            eta = (count - _i) * time_per_item
            
            if with_eta:
                eta_string = "  eta %s" % round(eta, 1)
            
            if eta < 0.1:
                eta_string = "           "
        
        x = int(size*_i/count)
        sys.stdout.write("%s[%s%s] %i/%i%s\r" % (prefix, "#"*x, "."*(size-x), _i, count, eta_string))
        sys.stdout.flush()
    
    _show(0)
    for i, item in enumerate(it):
        yield item
        _show(i+1)
    
    # Cleanup
    time_so_far = time.time() - start_time
    
    if with_eta:
        eta_string = " in %ss" % round(time_so_far, 1)
        
        sys.stdout.write("%s[%s%s] %i/%i%s\r" % (prefix, "#"*size, "."*0, count, count, eta_string))
        sys.stdout.flush()
    
    print("")