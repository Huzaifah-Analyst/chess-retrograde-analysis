"""
BFS Chess Move Tree Generator
Generates all possible moves breadth-first to a specified depth
With persistent storage and resume capability
"""

import chess
import time
from collections import deque
from persistent_storage import ChessTreeStorage
from checkmate_detector import CheckmateDetector


class ChessBFS:
    """Generates chess move tree using Breadth-First Search"""
    
    def __init__(self, starting_fen, logger=None):
        """
        Initialize with a chess position
        
        Args:
            starting_fen: Chess position in FEN notation
            logger: Optional callback for logging
        """
        self.starting_fen = starting_fen
        self.positions_analyzed = 0
        self.logger = logger or print
        
    def log(self, msg):
        """Log message using configured logger"""
        if self.logger:
            self.logger(msg)
        
    def generate_move_tree(self, max_depth, resume=True, save_interval=1, db_path='chess_tree.db', use_checkmate_filter=False, limit_promotions=True, save_interval_nodes=500000, logger=None):
        """
        Generate move tree with persistent storage
        
        Args:
            max_depth: How deep to analyze
            resume: Whether to resume from saved progress
            save_interval: Save after every N depths
            db_path: Path to SQLite database
            use_checkmate_filter: Only generate moves matching conditions
            limit_promotions: If True, only consider Queen and Knight promotions
            save_interval_nodes: Save after every N moves analyzed
            logger: Optional callback for logging (overrides init logger)
            
        Returns:
            Dictionary of positions with their data
        """
        if logger:
            self.logger = logger
            
        self.log(f"Generating move tree to depth {max_depth}...")
        
        if use_checkmate_filter:
            detector = CheckmateDetector()
            self.log("🎯 Checkmate filter ENABLED")
        else:
            detector = None
            self.log("⚠️  Checkmate filter DISABLED (generating all moves)")
            
        if limit_promotions:
            self.log("  [!] Limiting promotions to Queen and Knight only")
        
        start_time = time.time()
        last_save_time = time.time()
        save_interval_seconds = 2 * 60 * 60  # 2 hours
        storage = ChessTreeStorage(db_path)
        
        # Try to resume
        start_depth = 1
        tree = {}
        
        if resume:
            saved_tree, progress = storage.load_tree()
            if saved_tree and progress:
                # Verify same starting position
                if progress['starting_fen'] == self.starting_fen:
                    self.log(f"Resuming from depth {progress['current_depth']}")
                    start_depth = progress['current_depth'] + 1
                    self.positions_analyzed = progress['positions_analyzed']
                    tree = saved_tree
                else:
                    self.log("Different starting position, starting fresh...")
                    storage.clear()
        
        # If we're at max depth already, nothing to do
        if start_depth > max_depth:
            self.log(f"Already at depth {start_depth - 1}, nothing to do")
            storage.close()
            return tree
        
        # Build tree using BFS - process ALL positions level by level
        # Start with initial position  
        start_board = chess.Board(self.starting_fen)
        
        # For first depth, queue is just starting position
        if start_depth == 1:
            current_level = [(start_board, [])]
        else:
            # Resume: get all positions at the last completed depth
            current_level = []
            for fen, data in tree.items():
                if data['depth'] == start_depth - 1:
                    if not data['is_checkmate'] and not data['is_stalemate']:
                        current_level.append((data['board'], data['moves']))
            self.log(f"Resuming with {len(current_level)} positions at depth {start_depth - 1}")
        
        # Process each depth level
        for current_depth in range(start_depth, max_depth + 1):
            depth_start_time = time.time()
            positions_at_start = len(tree)
            positions_analyzed_start = self.positions_analyzed
            
            self.log(f"\nGenerating depth {current_depth}...")
            self.log(f"  Processing {len(current_level)} parent positions...")
            
            next_level = []
            
            # Process all positions at current level
            for board, move_history in current_level:
                for move in board.legal_moves:
                    # Skip bishop/rook promotions (Dominic's optimization)
                    if limit_promotions and move.promotion and move.promotion in [chess.BISHOP, chess.ROOK]:
                        continue
                    
                    # Apply checkmate filter if enabled
                    if detector is not None:
                        if not detector.matches_conditions(board, move):
                            continue  # Skip this move
                    
                    self.positions_analyzed += 1
                    
                    # Make the move
                    new_board = board.copy()
                    new_board.push(move)
                    new_history = move_history + [move]
                    
                    # Get unique position key
                    position_key = new_board.fen()
                    
                    # Only add if not seen before
                    if position_key not in tree:
                        tree[position_key] = {
                            'depth': current_depth,
                            'moves': new_history,
                            'is_checkmate': new_board.is_checkmate(),
                            'is_stalemate': new_board.is_stalemate(),
                            'board': new_board.copy()
                        }
                        
                        # Add to next level if game not over
                        if not new_board.is_game_over():
                            next_level.append((new_board, new_history))
                    
                    # Progress indicator & Granular Saving
                    if self.positions_analyzed % 100000 == 0:
                        elapsed = time.time() - depth_start_time
                        self.log(f"    {self.positions_analyzed:,} moves analyzed, {len(tree):,} unique positions ({elapsed:.1f}s)...")
                        
                    current_time = time.time()
                    if current_time - last_save_time >= save_interval_seconds:
                        self.log(f"💾 Checkpoint: {len(tree):,} positions at {time.strftime('%H:%M:%S')}")
                        storage.save_tree(tree, self.starting_fen, current_depth, max_depth, self.positions_analyzed)
                        last_save_time = current_time
            
            # Move to next level
            current_level = next_level
            
            # Timing info
            depth_time = time.time() - depth_start_time
            total_time = time.time() - start_time
            new_positions = len(tree) - positions_at_start
            moves_analyzed = self.positions_analyzed - positions_analyzed_start
            
            self.log(f"[OK] Depth {current_depth}: +{new_positions:,} positions ({moves_analyzed:,} moves) in {depth_time:.1f}s")
            self.log(f"     Total: {len(tree):,} positions, {total_time:.1f}s elapsed")
            
            # Save after each depth
            if current_depth % save_interval == 0:
                storage.save_tree(tree, self.starting_fen, current_depth, max_depth, self.positions_analyzed)
            
            # Stop if no more positions to explore
            if not current_level:
                self.log(f"\nNo more positions to explore at depth {current_depth}")
                break
        
        # Final save
        storage.save_tree(tree, self.starting_fen, max_depth, max_depth, self.positions_analyzed)
        storage.close()
        
        total_time = time.time() - start_time
        self.log(f"\n{'='*60}")
        self.log(f"COMPLETE!")
        self.log(f"  Total moves analyzed: {self.positions_analyzed:,}")
        self.log(f"  Unique positions stored: {len(tree):,}")
        self.log(f"  Total time: {total_time:.1f}s")
        self.log(f"{'='*60}")
        
        if detector is not None:
            detector.print_stats()
        
        return tree
    
    def generate_move_tree_simple(self, max_depth):
        """
        Simple tree generation without persistence (for testing)
        
        Args:
            max_depth: How many moves ahead to analyze
            
        Returns:
            Dictionary of positions with their data
        """
        self.log(f"Generating move tree to depth {max_depth}...")
        
        start_time = time.time()
        
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
                # Skip bishop/rook promotions (Dominic's optimization)
                if move.promotion and move.promotion in [chess.BISHOP, chess.ROOK]:
                    continue
                    
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
                if self.positions_analyzed % 100000 == 0:
                    elapsed = time.time() - start_time
                    self.log(f"  {self.positions_analyzed:,} moves analyzed, {len(tree):,} positions ({elapsed:.1f}s)...")
        
        total_time = time.time() - start_time
        self.log(f"\n{'='*60}")
        self.log(f"COMPLETE!")
        self.log(f"  Total moves analyzed: {self.positions_analyzed:,}")
        self.log(f"  Unique positions stored: {len(tree):,}")
        self.log(f"  Total time: {total_time:.1f}s")
        self.log(f"{'='*60}")
        
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
    # Test with near-checkmate position
    fen = "7k/6Q1/5K2/8/8/8/8/8 w - - 0 1"
    
    print("="*60)
    print("Testing BFS on Near-Checkmate Position")
    print("="*60)
    print(f"FEN: {fen}")
    print()
    
    bfs = ChessBFS(fen)
    tree = bfs.generate_move_tree_simple(max_depth=6)
    
    stats = bfs.get_statistics(tree)
    
    print("\n=== STATISTICS ===")
    print(f"Total positions: {stats['total_positions']:,}")
    print(f"Checkmates found: {stats['checkmates_found']}")
    print("\nPositions by depth:")
    for depth, count in sorted(stats['positions_by_depth'].items()):
        print(f"  Depth {depth}: {count:,} positions")