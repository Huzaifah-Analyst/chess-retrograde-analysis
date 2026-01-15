import unittest
import sys
import os
import chess

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from chess_bfs import ChessBFS
from retrograde_analysis import RetrogradeAnalyzer
from persistent_storage import ChessTreeStorage

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_integration.db'
        # Use a simple endgame position: K+R vs K
        # White: Ke1, Ra1. Black: Ke8.
        self.fen = "4k3/8/8/8/8/8/8/R3K3 w - - 0 1"
        
    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_full_flow(self):
        # 1. Generate Tree (Depth 3)
        bfs = ChessBFS(self.fen)
        tree = bfs.generate_move_tree(max_depth=3, db_path=self.db_path, resume=False)
        
        self.assertTrue(len(tree) > 0)
        
        # 2. Verify Storage
        storage = ChessTreeStorage(self.db_path)
        loaded_tree, progress = storage.load_tree()
        storage.close()
        
        self.assertEqual(len(tree), len(loaded_tree))
        
        # 3. Retrograde Analysis
        analyzer = RetrogradeAnalyzer(loaded_tree, self.fen)
        results = analyzer.analyze()
        
        self.assertIn('checkmates', results)
        self.assertIn('dead_ends', results)
        self.assertIn('dominic_ratio', results)

if __name__ == '__main__':
    unittest.main()
