import unittest
from engine.libs import screen_lib

class ScreenLibTests(unittest.TestCase):
    def test_keyboard_converter(self):
        test_data = {
            ("qwerty", "colemak"): (
                ("q", "q"),
                ("w", "w"),
                ("e", "f"),
                ("r", "p"),
                ("t", "g"),
                ("y", "j"),
                ("u", "l"),
                ("i", "u"),
                ("o", "y"),
                ("p", ";"),
                
                ("a", "a"),
                ("s", "r"),
                ("d", "s"),
                ("f", "t"),
                ("g", "d"),
                ("h", "h"),
                ("j", "n"),
                ("k", "e"),
                ("l", "i"),
                
                ("z", "z"),
                ("x", "x"),
                ("c", "c"),
                ("v", "v"),
                ("b", "b"),
                ("n", "k"),
                ("m", "m"),
            ),
            
            ("colemak", "qwerty"): (
                ("q", "q"),
                ("w", "w"),
                ("f", "e"),
                ("p", "r"),
                ("g", "t"),
                ("j", "y"),
                ("l", "u"),
                ("u", "i"),
                ("y", "o"),
                (";", "p"),
                       
                ("a", "a"),
                ("r", "s"),
                ("s", "d"),
                ("t", "f"),
                ("d", "g"),
                ("h", "h"),
                ("n", "j"),
                ("e", "k"),
                ("i", "l"),
                       
                ("z", "z"),
                ("x", "x"),
                ("c", "c"),
                ("v", "v"),
                ("b", "b"),
                ("k", "n"),
                ("m", "m"),
            ),
        }
        
        for keyboard, vals in test_data.items():
            from_keyboard, to_keyboard = keyboard
            
            for key_in, expected in vals:
                result = screen_lib.translate_keyboard(from_keyboard, to_keyboard, key_in)
                
                self.assertEqual(result, expected,
                    msg="""screen_lib.translate_keyboard did not convert correctly
Args: %s, %s, %s
Expected: %s
Result: %s""" % (from_keyboard, to_keyboard, key_in, expected, result)
                )
                
            
        
    
suite = unittest.TestLoader().loadTestsFromTestCase(ScreenLibTests)