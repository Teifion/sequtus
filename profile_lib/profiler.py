import cProfile
import pstats
import time
from game import seq_game

def general_test():
    s = seq_game.Sequtus()
    s.start()

def run(suite):
    if suite == "":
        run_str = 'seq_game.Sequtus().start()'
    
    start_time = time.time()
    cache = {}
    
    cProfile.runctx(run_str, {"seq_game":seq_game}, {}, "print_stats")
    
    print("View stats with: rob profile -v True")

def view(options):
    p = pstats.Stats("print_stats")
    
    p.sort_stats('cumulative')
    p.print_stats(35)