"""
Dominic's 2-Condition Checkmate Detection
Condition 1: King has no escape squares
Condition 2: Attack lines are created or improved
"""

import chess

class CheckmateDetector:
    """
    Detects potential checkmate moves using 2 logical conditions
    """
    
    def __init__(self):
        self.stats = {
            'total_moves_checked': 0,
            'condition_matches': 0,
            'confirmed_checkmates': 0,
            'false_positives': 0
        }
    
    def matches_conditions(self, board, move):
        """
        Check if a move matches Dominic's 2 checkmate conditions
        
        Args:
            board: Current chess board
            move: Move to evaluate
            
        Returns:
            True if both conditions are met
        """
        self.stats['total_moves_checked'] += 1
        
        # Apply move temporarily
        board.push(move)
        
        # Condition 1: King has no escape squares
        condition1 = self.king_has_no_escapes(board)
        
        # Condition 2: Attack lines created or improved
        condition2 = self.attack_lines_created(board)
        
        # Undo move
        board.pop()
        
        # Both conditions must be true
        result = condition1 and condition2
        
        if result:
            self.stats['condition_matches'] += 1
        
        return result
    
    def king_has_no_escapes(self, board):
        """
        Condition 1: King has no escape squares
        
        After the move, the opponent's king must have:
        - No legal moves that escape check
        - This means king is trapped
        """
        # Get opponent's king position
        opponent_king_square = board.king(board.turn)
        
        if opponent_king_square is None:
            return False
        
        # Check if king is in check
        if not board.is_check():
            return False
        
        # Generate all legal moves for the king
        king_moves = []
        for move in board.legal_moves:
            if move.from_square == opponent_king_square:
                king_moves.append(move)
        
        # If king has ANY legal move, it can escape
        # So condition fails
        if len(king_moves) > 0:
            return False
        
        # King is in check and has no moves = trapped
        return True
    
    def attack_lines_created(self, board):
        """
        Condition 2: Attack lines are created or improved
        
        After the move:
        - Opponent's king must be in check (under attack)
        - This verifies attack lines exist
        """
        # Simply check if king is in check
        return board.is_check()
    
    def verify_is_checkmate(self, board, move):
        """
        After conditions match, verify it's actually checkmate
        
        Args:
            board: Current chess board
            move: Move that matched conditions
            
        Returns:
            True if confirmed checkmate
        """
        board.push(move)
        is_mate = board.is_checkmate()
        board.pop()
        
        if is_mate:
            self.stats['confirmed_checkmates'] += 1
        else:
            self.stats['false_positives'] += 1
        
        return is_mate
    
    def get_stats(self):
        """Return detection statistics"""
        stats = self.stats.copy()
        
        if stats['condition_matches'] > 0:
            stats['accuracy'] = (stats['confirmed_checkmates'] / 
                               stats['condition_matches'] * 100)
        else:
            stats['accuracy'] = 0.0
        
        if stats['total_moves_checked'] > 0:
            stats['filter_rate'] = (stats['condition_matches'] / 
                                   stats['total_moves_checked'] * 100)
        else:
            stats['filter_rate'] = 0.0
        
        return stats
    
    def print_stats(self):
        """Print detection statistics"""
        stats = self.get_stats()
        
        print("\n" + "="*50)
        print("CHECKMATE DETECTION STATISTICS")
        print("="*50)
        print(f"Total moves checked: {stats['total_moves_checked']:,}")
        print(f"Condition matches: {stats['condition_matches']:,} ({stats['filter_rate']:.2f}%)")
        print(f"Confirmed checkmates: {stats['confirmed_checkmates']:,}")
        print(f"False positives: {stats['false_positives']:,}")
        print(f"Accuracy: {stats['accuracy']:.2f}%")
        print("="*50 + "\n")
