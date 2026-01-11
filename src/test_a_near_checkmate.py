"""
Test A: Near-Checkmate Position Analysis (Depth 10)
Purpose: Prove the algorithm works correctly with checkmates present
"""

import os
import sys
import json
import time

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chess_bfs import ChessBFS
from retrograde_analysis import RetrogradeAnalyzer


def main():
    # Near-checkmate position: K+Q vs K (white to move, near checkmate)
    FEN = "7k/6Q1/5K2/8/8/8/8/8 w - - 0 1"
    MAX_DEPTH = 10
    DB_PATH = "test_a_near_checkmate.db"
    
    print("="*70)
    print("TEST A: NEAR-CHECKMATE POSITION ANALYSIS")
    print("="*70)
    print(f"FEN: {FEN}")
    print(f"Position: K+Q vs K (White to move)")
    print(f"Target Depth: {MAX_DEPTH}")
    print(f"Purpose: Prove algorithm works with checkmates present")
    print("="*70)

    # Create results directory
    os.makedirs('results', exist_ok=True)

    start_time = time.time()
    
    # Generate BFS tree
    print("\nPhase 1: Generating BFS tree...")
    bfs = ChessBFS(FEN)
    tree = bfs.generate_move_tree(max_depth=MAX_DEPTH, resume=True, save_interval=1, db_path=DB_PATH)

    bfs_stats = bfs.get_statistics(tree)
    
    print(f"\nTree Generation Complete!")
    print(f"  Total positions: {bfs_stats['total_positions']:,}")
    print(f"  Checkmates found: {bfs_stats['checkmates_found']}")

    # Run retrograde analysis
    print("\n" + "="*70)
    print("Phase 2: Running retrograde analysis...")
    analyzer = RetrogradeAnalyzer(tree)
    results = analyzer.analyze()

    # Print refined ratio results only
    print("\n" + "="*70)
    print("REFINED RATIO RESULTS")
    print("="*70)
    print(f"{'Depth':<8} {'Safe Moves':<15} {'Checkmates':<12} {'Dead Ends':<12} {'Barrier':<10} {'Ratio':<10}")
    print("-"*70)

    for depth, data in sorted(results['refined_ratio'].items()):
        ratio = data['ratio']
        if isinstance(ratio, str) or ratio == float('inf'):
            ratio_str = "inf"
        else:
            ratio_str = f"{ratio:.2f}"
        print(f"{depth:<8} {data['safe_moves']:<15} {data['checkmates']:<12} "
              f"{data['dead_ends']:<12} {data['barrier_size']:<10} {ratio_str:<10}")

    print("="*70)
    
    total_time = time.time() - start_time
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total positions analyzed: {bfs_stats['total_positions']:,}")
    print(f"Checkmates found: {bfs_stats['checkmates_found']}")
    print(f"Dead ends found: {len(results['dead_ends'])}")
    print(f"Propagation depth: {results['propagation_depth']}")
    print(f"Total time: {total_time:.1f}s")
    print("="*70)

    # Save results
    results_file = 'results/test_a_near_checkmate_depth10.json'
    
    export_data = {
        'test_name': 'Test A: Near-Checkmate Position',
        'fen': FEN,
        'max_depth': MAX_DEPTH,
        'total_positions': bfs_stats['total_positions'],
        'positions_by_depth': bfs_stats['positions_by_depth'],
        'checkmates_found': bfs_stats['checkmates_found'],
        'dead_ends_found': len(results['dead_ends']),
        'propagation_depth': results['propagation_depth'],
        'refined_ratio': results['refined_ratio'],
        'total_time_seconds': total_time
    }
    
    with open(results_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"\n[OK] Results saved to {results_file}")
    print(f"[OK] Database saved to {DB_PATH}")


if __name__ == "__main__":
    main()
