import unittest
import sys
import os
import chess
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from persistent_storage import ChessTreeStorage

class TestPersistentStorage(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_chess_tree.db'
        self.storage = ChessTreeStorage(self.db_path)
        
    def tearDown(self):
        self.storage.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_and_load(self):
        # Create dummy tree
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        tree = {
            fen: {
                'depth': 0,
                'moves': [],
                'is_checkmate': False,
                'is_stalemate': False,
                'board': chess.Board(fen)
            }
        }
        
        self.storage.save_tree(tree, fen, 0, 1, 1)
        
        # Load back
        loaded_tree, progress = self.storage.load_tree()
        
        self.assertIsNotNone(loaded_tree)
        self.assertIn(fen, loaded_tree)
        self.assertEqual(loaded_tree[fen]['depth'], 0)
        self.assertEqual(progress['starting_fen'], fen)

    def test_clear(self):
        # Save something
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        tree = {fen: {'depth': 0, 'moves': [], 'is_checkmate': False, 'is_stalemate': False, 'board': chess.Board(fen)}}
        self.storage.save_tree(tree, fen, 0, 1, 1)
        
        # Clear
        self.storage.clear()
        
        # Load
        loaded_tree, progress = self.storage.load_tree()
        self.assertIsNone(loaded_tree)

if __name__ == '__main__':
    unittest.main()
