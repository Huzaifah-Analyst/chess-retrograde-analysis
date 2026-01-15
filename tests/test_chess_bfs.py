import unittest
import sys
import os
import chess

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from chess_bfs import ChessBFS

class TestChessBFS(unittest.TestCase):
    def setUp(self):
        self.starting_fen = chess.STARTING_FEN
        self.bfs = ChessBFS(self.starting_fen)

    def test_initialization(self):
        self.assertEqual(self.bfs.starting_fen, self.starting_fen)
        self.assertEqual(self.bfs.positions_analyzed, 0)

    def test_simple_tree_generation_depth_1(self):
        # Depth 1 from starting position = 20 moves
        tree = self.bfs.generate_move_tree_simple(max_depth=1)
        self.assertEqual(len(tree), 20)
        
        # Verify structure
        first_key = list(tree.keys())[0]
        self.assertIn('depth', tree[first_key])
        self.assertIn('moves', tree[first_key])
        self.assertIn('is_checkmate', tree[first_key])
        self.assertEqual(tree[first_key]['depth'], 1)

    def test_checkmate_detection(self):
        # Fool's Mate: f3 e5 g4 Qh4#
        fools_mate_fen = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
        bfs = ChessBFS(fools_mate_fen)
        
        # Should detect checkmate immediately if we process it
        # Note: generate_move_tree_simple starts FROM the given position.
        # If the given position IS checkmate, it might not generate children.
        # Let's test a position 1 move away from checkmate.
        
        # White to move, Qh5# is available
        # Position: 4k3/8/8/8/8/8/5Q2/4K3 w - - 0 1 (White Q at f2, Black K at e8)
        # Let's set up a mate in 1
        mate_in_1 = "7k/6Q1/5K2/8/8/8/8/8 b - - 0 1" # Black is checkmated
        
        # If we start with a checkmated position, BFS might return empty or just that pos depending on implementation
        # Actually BFS generates moves FROM the start. If start is mate, 0 moves.
        
        # Let's try a position where white moves to mate
        # White King f6, White Queen g6, Black King h8. White to move. Qg7#
        near_mate = "7k/6Q1/5K2/8/8/8/8/8 w - - 0 1" # Wait, this is already mate if black to move? No, white to move.
        # If white to move, Qg7 is not legal if black king is there.
        
        # Let's use a standard mate in 1
        # White: Kh1, Rh2. Black: Kh8. White moves Rh8#?? No.
        # Simple: K+Q vs K. 
        # White: Kf6, Qg6. Black: Kh8. White to move. Qg7#
        near_mate = "7k/6P1/5K2/8/8/8/8/8 w - - 0 1" # This is just a pawn.
        
        # Real mate in 1:
        # White: Ke1, Qd1. Black: Ke8.
        # 1. Qd8# ?? No.
        
        # Let's use the one from the code: "7k/6Q1/5K2/8/8/8/8/8 w - - 0 1"
        # This FEN means White to move. But black king is in check from Q at g7?
        # If Q is at g7 and K is at h8.
        # If it's white to move, how did white get there?
        # Ah, the test code used: "7k/6Q1/5K2/8/8/8/8/8 w - - 0 1"
        # Let's check if that's valid.
        # Board("7k/6Q1/5K2/8/8/8/8/8 w - - 0 1").is_valid() -> False (King in check)
        
        # Let's use a valid mate in 1.
        # White: Kg6, Qf7. Black: Kh8. White to move.
        # Qf8# or Qg7#
        pos = "7k/5Q2/6K1/8/8/8/8/8 w - - 0 1"
        bfs = ChessBFS(pos)
        tree = bfs.generate_move_tree_simple(max_depth=1)
        
        # Find the checkmate position in the tree
        checkmates = [fen for fen, data in tree.items() if data['is_checkmate']]
        self.assertTrue(len(checkmates) > 0, "Should find at least one checkmate")

    def test_promotion_handling(self):
        # Dominic's optimization: Skip Bishop/Rook promotions
        # Setup a pawn ready to promote
        # White pawn on a7, Black king on c8. White to move.
        pos = "2k5/P7/8/8/8/8/8/4K3 w - - 0 1"
        bfs = ChessBFS(pos)
        tree = bfs.generate_move_tree_simple(max_depth=1)
        
        # Moves: a8=Q, a8=R, a8=B, a8=N
        # Should only have Q and N (if optimization works)
        
        promotions = []
        for fen, data in tree.items():
            last_move = data['moves'][-1]
            if last_move.promotion:
                promotions.append(last_move.promotion)
        
        self.assertIn(chess.QUEEN, promotions)
        self.assertIn(chess.KNIGHT, promotions)
        self.assertNotIn(chess.ROOK, promotions)
        self.assertNotIn(chess.BISHOP, promotions)

if __name__ == '__main__':
    unittest.main()
