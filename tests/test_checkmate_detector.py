import unittest
import sys
import os
import chess

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from checkmate_detector import CheckmateDetector

class TestCheckmateDetector(unittest.TestCase):
    def setUp(self):
        self.detector = CheckmateDetector()
        self.log_file = open("test_output.txt", "a")

    def tearDown(self):
        self.log_file.close()

    def log(self, msg):
        self.log_file.write(msg + "\n")

    def test_king_has_no_escapes(self):
        # Stalemate position: Black King at h8, White King f6, White Q g6.
        # Wait, if Q is at g6, it's mate if it's at g7.
        # Let's use the one I analyzed:
        # White K f6, Q g5. Black K h8. Black to move.
        # h8 -> g8 (attacked by Q at g5? g5 attacks d8..h5? No diagonal.)
        # Q at g5 attacks: g-file, 5th rank.
        # Diagonals: f4, e3... and h6.
        # Diagonals: f6, e7, d8.
        # Diagonals: h4.
        # So Q at g5 does NOT attack g8 or h7?
        # g5 (6, 4). g8 (6, 7). Yes g-file.
        # h7 (7, 6).
        # g5 -> h6 -> i7? No.
        # g5 -> f6 -> e7 -> d8.
        # So h7 is safe?
        
        # Let's use a simple Fool's Mate final position.
        # FEN: rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3
        # White is checkmated.
        board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
        
        result = self.detector.king_has_no_escapes(board)
        self.log(f"test_king_has_no_escapes (Fool's Mate): {result}")
        self.assertTrue(result)

    def test_attack_lines_improved(self):
        # Valid Mate: K+Q vs K
        # Start: White K f6, Q g6. Black K h8.
        # Move: Qg7#
        start_fen = "7k/8/5KQ1/8/8/8/8/8 w - - 0 1"
        board = chess.Board(start_fen)
        move = chess.Move.from_uci("g6g7") # Checkmate
        
        self.log("\nDEBUG: test_attack_lines_improved")
        
        # Manually check
        board.push(move)
        c1 = self.detector.king_has_no_escapes(board)
        c2 = self.detector.attack_lines_improved(board, move)
        c3 = self.detector.attacker_in_range(board, move)
        c4 = self.detector.threatening_piece_exists(board, move)
        board.pop()
        
        self.log(f"King No Escapes: {c1}")
        self.log(f"Attack Improved: {c2}")
        self.log(f"Attacker Range: {c3}")
        self.log(f"Threat Exists: {c4}")
        
        self.assertTrue(c1, "Condition 1 Failed")
        self.assertTrue(c2, "Condition 2 Failed")
        self.assertTrue(c3, "Condition 3 Failed")
        self.assertTrue(c4, "Condition 4 Failed")
        
        self.assertTrue(self.detector.matches_conditions(board, move))

    def test_non_checkmate_move(self):
        start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        board = chess.Board(start_fen)
        move = chess.Move.from_uci("e2e4")
        
        self.log("\nDEBUG: test_non_checkmate_move")
        # Manually check
        board.push(move)
        c1 = self.detector.king_has_no_escapes(board)
        c2 = self.detector.attack_lines_improved(board, move)
        c3 = self.detector.attacker_in_range(board, move)
        c4 = self.detector.threatening_piece_exists(board, move)
        board.pop()
        
        self.log(f"King No Escapes: {c1}")
        self.log(f"Attack Improved: {c2}")
        self.log(f"Attacker Range: {c3}")
        self.log(f"Threat Exists: {c4}")
        
        # We expect at least one to be False
        self.assertFalse(all([c1, c2, c3, c4]))

if __name__ == '__main__':
    # Clear log file
    with open("test_output.txt", "w") as f:
        f.write("Starting Tests\n")
    unittest.main()
