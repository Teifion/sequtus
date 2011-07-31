import unittest
import sim_t

class BattleTests (sim_t.SimTester):
    def test_load(self):
        sim = self.new_sim(0)
        sim.run()
        
        # State checks
        self.assertEqual(len(sim.actors), 2, "Sim loaded an incorrect number of actors")
        
        self.assertEqual(sim.actors[0].aid, 0, "Sim does not correctly set the first actor's aid")
        self.assertEqual(sim.actors[1].aid, 1, "Sim does not correctly increment actor aid")
        
        self.assertEqual(sim.actors[0].team, 1, "Sim does not correctly assign a team to actors")
        self.assertEqual(sim.actors[1].team, 2, "Sim does not correctly assign a team to actors")
        
        self.assertEqual(sim.actors[0].hp, 5, "Sim does not correctly assign hp to actors")
        self.assertEqual(sim.actors[1].hp, 10, "Sim does not correctly assign hp to actors")
    
    def test_orders(self):
        sim = self.new_sim(150)
        
        sim.actors[0].issue_command("move", (500, 500))
        sim.actors[0].append_command("stop", -1)
        
        sim.actors[1].issue_command("move", (1000, 1000))
        sim.actors[1].issue_command("stop", -1)
        
        sim.run()
        
        self.assertEqual(sim.actors[0].pos, [500, 500, 0], "Actor does not correctly append orders")
        self.assertEqual(sim.actors[1].pos, [1000, 500, 0], "Actor does not correctly issue orders")
    
    def test_flags(self):
        sim = self.new_sim(1)
        
        sim.actors[0].issue_command("move", (500, 500))
        
        sim.run()
        
        self.assertEqual(sim.actors[0].is_moving, True, "Moving actor does not register .is_moving flag")
        self.assertEqual(sim.actors[1].is_moving, False, "Stationary actor does not register .is_moving flag")


suite = unittest.TestLoader().loadTestsFromTestCase(BattleTests)