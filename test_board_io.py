import unittest
from board import Loc, Orientation
from board_io import parse_from_text, save_as_text

class TestBoardIO(unittest.TestCase):
    def test_serialization_roundtrip(self):
        original_text = (
            "+-----+\n"
            "|     |\n"
            "|   f |\n"
            "|   f |\n"
            "| R FF|\n"
            "| MM M|\n"
            "+-----+"
        )
        
        state = parse_from_text(original_text)
        
        # Check rabbits
        self.assertEqual(len(state.rabbits), 1)
        self.assertEqual(state.rabbits[0].loc.y, 3)
        self.assertEqual(state.rabbits[0].loc.x, 1)
        
        # Check mushrooms
        self.assertEqual(len(state.setup.mushrooms), 3)
        mushroom_locs = sorted([(m.loc.y, m.loc.x) for m in state.setup.mushrooms])
        self.assertEqual(mushroom_locs, [(4, 1), (4, 2), (4, 4)])
        
        # Check foxes
        self.assertEqual(len(state.foxes), 2)
        
        # Fox 1 (f) should be vertical at (1, 3)
        fox1 = state.foxes[0]
        self.assertEqual(fox1.orientation, Orientation.VERTICAL)
        self.assertEqual(fox1.loc.y, 1)
        self.assertEqual(fox1.loc.x, 3)
        
        # Fox 2 (F) should be horizontal at (3, 3)
        fox2 = state.foxes[1]
        self.assertEqual(fox2.orientation, Orientation.HORIZONTAL)
        self.assertEqual(fox2.loc.y, 3)
        self.assertEqual(fox2.loc.x, 3)
        
        # Round trip
        serialized_text = save_as_text(state)
        self.assertEqual(serialized_text.strip(), original_text.strip())

if __name__ == '__main__':
    unittest.main()
