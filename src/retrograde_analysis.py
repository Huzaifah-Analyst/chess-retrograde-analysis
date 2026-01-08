"""
Retrograde Analysis - Dominic's Decrement Algorithm
Implements backward propagation from checkmates to find dead-end positions
"""

import chess
import json
from collections import defaultdict


class RetrogradeAnalyzer:
    """
    Analyzes chess positions using retrograde (backward) checkmate elimination.
    
    Core Algorithm:
    1. Find all checkmate positions
    2. Work backwards to find parent positions
    3. Decrement move counts for parents of checkmates
    4. Mark positions with 0 good moves as dead ends
    5. Propagate backwards from dead ends
    """
    
    def __init__(self, move_tree):
        """
        Initialize analyzer with BFS move tree
        
        Args:
            move_tree: Dictionary from ChessBFS.generate_move_tree()
        """
        self.tree = move_tree
        self.dead_ends = set()
        self.move_counts = {}
        self.initial_move_counts = {}
        self.depth_stats = defaultdict(lambda: {
            'positions': 0,
            'checkmates': 0,
            'dead_ends': 0,
            'available_moves': 0,
            'initial_moves': 0
        })
        
    def analyze(self):
        """
        Run complete retrograde analysis
        
        Returns:
            Dictionary with comprehensive results including Dominic's ratio data
        """
        print("\n" + "="*60)
        print("RETROGRADE ANALYSIS - Dominic's Algorithm")
        print("="*60)
        
        # Step 1: Find checkmates
        print("\nStep 1: Finding checkmate positions...")
        checkmates = self.find_checkmates()
        print(f"✓ Found {len(checkmates)} checkmate positions")
        
        # Step 2: Initialize move counts
        print("\nStep 2: Initializing move counts...")
        self.initialize_move_counts()
        print(f"✓ Initialized {len(self.move_counts)} positions")
        
        # Step 3: Collect initial statistics
        print("\nStep 3: Collecting depth statistics...")
        self.collect_depth_statistics()
        
        # Step 4: Run decrement algorithm
        print("\nStep 4: Running decrement propagation...")
        self.decrement_from_checkmates(checkmates)
        print(f"✓ Found {len(self.dead_ends)} dead-end positions")
        
        # Step 5: Calculate final statistics
        print("\nStep 5: Calculating final statistics...")
        propagation_depth = self.calculate_propagation_depth()
        ratio_data = self.calculate_dominic_ratio()
        
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        
        return {
            'checkmates': checkmates,
            'dead_ends': self.dead_ends,
            'move_counts': self.move_counts,
            'initial_move_counts': self.initial_move_counts,
            'propagation_depth': propagation_depth,
            'depth_statistics': dict(self.depth_stats),
            'dominic_ratio': ratio_data
        }
    
    def find_checkmates(self):
        """Find all checkmate positions in tree"""
        checkmates = []
        for fen, data in self.tree.items():
            if data['is_checkmate']:
                checkmates.append(fen)
        return checkmates
    
    def initialize_move_counts(self):
        """
        Initialize move count for each position
        
        Counts legal moves available from each position.
        These counts will be decremented when moves lead to bad positions.
        """
        for fen, data in self.tree.items():
            board = data['board']
            move_count = len(list(board.legal_moves))
            self.move_counts[fen] = move_count
            self.initial_move_counts[fen] = move_count  # Save original for comparison
    
    def collect_depth_statistics(self):
        """Collect statistics per depth for ratio analysis"""
        for fen, data in self.tree.items():
            depth = data['depth']
            
            # Count positions
            self.depth_stats[depth]['positions'] += 1
            
            # Count checkmates
            if data['is_checkmate']:
                self.depth_stats[depth]['checkmates'] += 1
            
            # Sum available moves
            self.depth_stats[depth]['available_moves'] += self.initial_move_counts[fen]
            self.depth_stats[depth]['initial_moves'] += self.initial_move_counts[fen]
    
    def decrement_from_checkmates(self, checkmates):
        """
        Core Algorithm: Dominic's Decrement Logic
        
        Process:
        1. Start with all checkmate positions (bad for opponent)
        2. Find positions that lead to these checkmates (parents)
        3. Decrement parent move counts (one less good option)
        4. If parent reaches 0 good moves → dead end
        5. Treat dead ends like checkmates, propagate backwards
        
        This creates a "barrier" of bad positions spreading backwards through tree.
        """
        to_process = list(checkmates)
        processed = set()
        iterations = 0
        
        while to_process:
            iterations += 1
            bad_position = to_process.pop(0)
            
            if bad_position in processed:
                continue
            processed.add(bad_position)
            
            # Find all positions that can reach this bad position
            parents = self.find_parent_positions(bad_position)
            
            # Decrement each parent's move count
            for parent_fen in parents:
                self.move_counts[parent_fen] -= 1
                
                # If parent has no good moves left, it's a dead end
                if self.move_counts[parent_fen] <= 0:
                    self.dead_ends.add(parent_fen)
                    # Add dead end to process queue (propagate further back)
                    to_process.append(parent_fen)
            
            # Progress indicator
            if len(processed) % 50 == 0 and len(processed) > 0:
                print(f"  Processed: {len(processed)} | Dead ends: {len(self.dead_ends)} | Queue: {len(to_process)}")
        
        # Update depth statistics with dead ends
        for fen in self.dead_ends:
            depth = self.tree[fen]['depth']
            self.depth_stats[depth]['dead_ends'] += 1
        
        print(f"\n✓ Completed in {iterations} iterations")
    
    def find_parent_positions(self, position_fen):
        """
        Find positions that can reach target position in one move
        
        Works backwards: given a position, who can get here?
        """
        parents = []
        target_depth = self.tree[position_fen]['depth']
        
        # Only look at positions one level up
        for fen, data in self.tree.items():
            if data['depth'] == target_depth - 1:
                board = data['board']
                
                # Check if any move leads to target
                for move in board.legal_moves:
                    test_board = board.copy()
                    test_board.push(move)
                    if test_board.fen() == position_fen:
                        parents.append(fen)
                        break
        
        return parents
    
    def calculate_propagation_depth(self):
        """
        Calculate shallowest depth where dead end was found
        
        Shows how far back the "barrier" propagated
        """
        if not self.dead_ends:
            return None
        
        min_depth = float('inf')
        for fen in self.dead_ends:
            depth = self.tree[fen]['depth']
            min_depth = min(min_depth, depth)
        
        return min_depth
    
    def calculate_dominic_ratio(self):
        """
        Calculate Dominic's barrier ratio at each depth
        
        Ratio = available_moves / (checkmates + dead_ends)
        
        If ratio → 1 or below: barrier is closing, position trapped
        If ratio stays > 1: game continues
        """
        ratio_by_depth = {}
        
        for depth, stats in sorted(self.depth_stats.items()):
            checkmates = stats['checkmates']
            dead_ends = stats['dead_ends']
            available_moves = stats['available_moves']
            
            barrier_size = checkmates + dead_ends
            
            if barrier_size > 0:
                ratio = available_moves / barrier_size
            else:
                ratio = "Infinity"  # No barrier yet (String for valid JSON)
            
            ratio_by_depth[depth] = {
                'available_moves': available_moves,
                'checkmates': checkmates,
                'dead_ends': dead_ends,
                'barrier_size': barrier_size,
                'ratio': ratio
            }
        
        return ratio_by_depth
    
    def export_results(self, filename='results/analysis_results.json'):
        """Export results to JSON for further analysis"""
        results = self.analyze()
        
        # Convert sets to lists for JSON serialization
        export_data = {
            'checkmates': list(results['checkmates']),
            'dead_ends': list(results['dead_ends']),
            'propagation_depth': results['propagation_depth'],
            'depth_statistics': results['depth_statistics'],
            'dominic_ratio': results['dominic_ratio']
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n✓ Results exported to {filename}")
        return export_data


def print_results_summary(results):
    """Print human-readable summary of results"""
    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    
    print(f"\nCheckmates found: {len(results['checkmates'])}")
    print(f"Dead ends found: {len(results['dead_ends'])}")
    print(f"Propagation reached depth: {results['propagation_depth']}")
    
    print("\n" + "-"*60)
    print("DOMINIC'S RATIO ANALYSIS")
    print("-"*60)
    print(f"{'Depth':<8} {'Avail Moves':<15} {'Checkmates':<12} {'Dead Ends':<12} {'Ratio':<10}")
    print("-"*60)
    
    for depth, data in sorted(results['dominic_ratio'].items()):
        ratio_str = f"{data['ratio']:.2f}" if data['ratio'] != float('inf') else "∞"
        print(f"{depth:<8} {data['available_moves']:<15} {data['checkmates']:<12} "
              f"{data['dead_ends']:<12} {ratio_str:<10}")
    
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    print("Ratio = Available Moves / (Checkmates + Dead Ends)")
    print("  • Ratio > 1: Game can continue (more options than barriers)")
    print("  • Ratio ≤ 1: Position trapped (barriers equal/exceed options)")
    print("  • Trending down: Barrier is closing")
    print("  • Trending up: Barrier effect weakening")
    print("="*60)


# Test with multiple positions
if __name__ == "__main__":
    from chess_bfs import ChessBFS
    import os
    
    # Create results directory
    os.makedirs('results', exist_ok=True)
    
    # Test positions
    test_positions = [
        {
            'name': 'Near Checkmate (K+Q vs K)',
            'fen': '7k/6Q1/5K2/8/8/8/8/8 w - - 0 1',
            'depth': 6
        },
        {
            'name': 'Simple Endgame (K+R vs K)',
            'fen': '4k3/8/8/8/8/8/4R3/4K3 w - - 0 1',
            'depth': 8
        }
    ]
    
    for i, pos in enumerate(test_positions, 1):
        print("\n" + "="*60)
        print(f"TEST {i}: {pos['name']}")
        print("="*60)
        
        # Generate BFS tree
        print(f"\nGenerating BFS tree to depth {pos['depth']}...")
        bfs = ChessBFS(pos['fen'])
        tree = bfs.generate_move_tree(max_depth=pos['depth'])
        
        bfs_stats = bfs.get_statistics(tree)
        print(f"✓ Tree generated: {bfs_stats['total_positions']} positions")
        
        # Run retrograde analysis
        analyzer = RetrogradeAnalyzer(tree)
        results = analyzer.analyze()
        
        # Print results
        print_results_summary(results)
        
        # Export to JSON
        filename = f'results/test_{i}_{pos["name"].replace(" ", "_").lower()}.json'
        analyzer.export_results(filename)
        
        print("\n" + "="*60)