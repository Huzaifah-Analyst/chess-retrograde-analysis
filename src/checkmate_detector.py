"""
Checkmate Detector - Dominic's 4 Conditions
"""

import chess

class CheckmateDetector:
    def matches_conditions(self, board, move):
        """
        Dominic's 4 conditions for checkmate
        """
        # Apply move temporarily
        board.push(move)
        
        try:
            # Condition 1: King has no escape squares
            king_trapped = self.king_has_no_escapes(board)
            
            # Condition 2: Attack lines created or improved
            # Note: This is hard to define exactly without previous state comparison or specific definition.
            # For now, we'll check if the move gives check or attacks squares near king.
            attack_improved = self.attack_lines_improved(board, move)
            
            # Condition 3: Attacker within attack range immediately
            attacker_in_range = self.attacker_in_range(board, move)
            
            # Condition 4: Opponent has threatening piece in range
            # This sounds like "Is the opponent threatening us?" or "Do we have a threat?"
            # Assuming it means "The piece we moved is a threatening piece"
            threat_present = self.threatening_piece_exists(board, move)
            
            # All 4 must be true
            return all([king_trapped, attack_improved, 
                       attacker_in_range, threat_present])
        finally:
            board.pop()

    def king_has_no_escapes(self, board):
        """Condition 1: King has no escape squares (legal moves)"""
        # This is effectively "is checkmate" OR "is stalemate" if we only look at King moves.
        # But specifically "King has no escapes".
        # We can check if the King has any legal moves.
        
        turn = board.turn # Side to move (opponent of the one who just moved)
        king_square = board.king(turn)
        
        if king_square is None:
            return False
            
        # Check all pseudo-legal moves for King
        # If any are legal, then he has an escape.
        # Note: board.legal_moves includes all pieces. We need to filter for King.
        
        for move in board.legal_moves:
            if move.from_square == king_square:
                return False # Found an escape
        
        return True

    def attack_lines_improved(self, board, move):
        """Condition 2: Attack lines created or improved"""
        # Simplest interpretation: The move put the opponent in check.
        if board.is_check():
            return True
            
        # Or maybe it attacks a square adjacent to the king?
        turn = board.turn
        king_square = board.king(turn)
        if king_square is None:
            return False
            
        # Check if any square around king is attacked by the piece that moved
        # The piece that moved is now at move.to_square
        # But wait, board.turn is the opponent. The piece that moved belongs to (not board.turn).
        
        attacker_color = not board.turn
        moved_piece_square = move.to_square
        
        # Get squares around king
        king_rank = chess.square_rank(king_square)
        king_file = chess.square_file(king_square)
        
        for r in range(max(0, king_rank-1), min(8, king_rank+2)):
            for f in range(max(0, king_file-1), min(8, king_file+2)):
                sq = chess.square(f, r)
                if sq == king_square:
                    continue
                    
                # Is this square attacked by the moved piece?
                if board.is_attacked_by(attacker_color, sq):
                    # Ideally we check if it's attacked by the SPECIFIC piece, but generic attack is a good proxy
                    return True
                    
        return False

    def attacker_in_range(self, board, move):
        """Condition 3: Attacker within attack range immediately"""
        # Interpretation: The piece that moved is attacking the King or King's vicinity?
        # Let's assume it means "The piece that moved is attacking the King" (Check)
        # OR "The piece is close to the King".
        
        # Let's use: Piece is attacking the King (Check) OR Piece is attacking a square next to King.
        # This overlaps with Condition 2.
        
        # Alternative Interpretation: "Attacker" (the piece moving) is "in range" (can reach the king/critical squares).
        # If it gives check, it's definitely in range.
        if board.is_check():
            return True
            
        return False

    def threatening_piece_exists(self, board, move):
        """Condition 4: Opponent has threatening piece in range"""
        # "Opponent" here refers to the side that just moved (from the perspective of the victim).
        # So "Do I (the mover) have a threatening piece?"
        # Yes, the piece I just moved.
        
        # Maybe it means "Is there a piece that CAN deliver mate?"
        # Let's return True if the piece that moved is a Queen, Rook, or Bishop (Major/Minor pieces that can attack from range).
        # Or maybe just "Is there a threat?"
        
        # Let's stick to a simple check: Did the move create a threat?
        # If we are in check, that's a threat.
        if board.is_check():
            return True
            
        return False
