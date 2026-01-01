"""
BFS Chess Move Tree Generator
Generates all possible moves breadth-first to a specified depth
"""

import chess
from collections import deque


class ChessBFS:
    """Generates chess move tree using Breadth-First Search"""
    
    def __init__(self, starting_fen):
        """
        Initialize with a chess position
        
        Args:
            starting_fen: Chess position in FEN notation
        """
        self.starting_fen = starting_fen
        self.positions_analyzed = 0
        
    def generate_move_tree(self, max_depth):
        """
        Generate all possible moves up to max_depth
        
        Args:
            max_depth: How many moves ahead to analyze
            
        Returns:
            Dictionary of positions with their data
        """
        print(f"Generating move tree to depth {max_depth}...")
        
        # Start with initial position
        start_board = chess.Board(self.starting_fen)
        
        # Queue: (board, depth, move_history)
        queue = deque([(start_board, 0, [])])
        
        # Store all positions
        tree = {}
        
        # BFS loop
        while queue:
            board, depth, move_history = queue.popleft()
            
            # Stop if we've reached max depth
            if depth >= max_depth:
                continue
            
            # Analyze all legal moves from this position
            for move in board.legal_moves:
                self.positions_analyzed += 1
                
                # Make the move on a copy of the board
                new_board = board.copy()
                new_board.push(move)
                new_history = move_history + [move]
                
                # Get unique key for this position
                position_key = new_board.fen()
                
                # Store position data (only if not seen before)
                if position_key not in tree:
                    tree[position_key] = {
                        'depth': depth + 1,
                        'moves': new_history,
                        'is_checkmate': new_board.is_checkmate(),
                        'is_stalemate': new_board.is_stalemate(),
                        'board': new_board.copy()
                    }
                    
                    # Add to queue if game not over
                    if not new_board.is_game_over():
                        queue.append((new_board, depth + 1, new_history))
                
                # Progress indicator
                if self.positions_analyzed % 10000 == 0:
                    print(f"  Analyzed {self.positions_analyzed:,} positions...")
        
        print(f"Complete! Total positions: {self.positions_analyzed:,}")
        print(f"Unique positions stored: {len(tree):,}")
        
        return tree
    
    def get_statistics(self, tree):
        """Get statistics about the move tree"""
        
        depth_counts = {}
        checkmate_count = 0
        
        for data in tree.values():
            depth = data['depth']
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
            
            if data['is_checkmate']:
                checkmate_count += 1
        
        return {
            'total_positions': len(tree),
            'positions_by_depth': depth_counts,
            'checkmates_found': checkmate_count
        }


# Test the BFS
if __name__ == "__main__":
    # Simple endgame: King + Queen vs King
    fen = "4k3/8/8/8/8/8/4Q3/4K3 w - - 0 1"
    
    print("Testing BFS on K+Q vs K endgame\n")
    
    bfs = ChessBFS(fen)
    tree = bfs.generate_move_tree(max_depth=10)
    
    stats = bfs.get_statistics(tree)
    
    print("\n=== STATISTICS ===")
    print(f"Total positions: {stats['total_positions']:,}")
    print(f"Checkmates found: {stats['checkmates_found']}")
    print("\nPositions by depth:")
    for depth, count in sorted(stats['positions_by_depth'].items()):
        print(f"  Depth {depth}: {count:,} positions")