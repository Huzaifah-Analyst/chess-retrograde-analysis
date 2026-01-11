"""
Run analysis on chess starting position
"""

import os
import sys
import json
import chess

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chess_bfs import ChessBFS
from retrograde_analysis import RetrogradeAnalyzer, print_results_summary


def main():
    # Starting FEN
    STARTING_FEN = chess.STARTING_FEN
    MAX_DEPTH = 5  # Depth 5 is realistic for Python (~4.8M positions)
    
    print("="*70)
    print("CHESS STARTING POSITION ANALYSIS")
    print("="*70)
    print(f"FEN: {STARTING_FEN}")
    print(f"Target Depth: {MAX_DEPTH}")
    print(f"Target: Test refined ratio at increasing depths")
    print("="*70)

    # Create results directory
    os.makedirs('results', exist_ok=True)

    # Generate BFS tree
    print("\nPhase 1: Generating BFS tree...")
    bfs = ChessBFS(STARTING_FEN)
    tree = bfs.generate_move_tree(max_depth=MAX_DEPTH, resume=True, save_interval=1)

    print(f"\nTree complete: {len(tree)} positions")

    # Run retrograde analysis
    print("\nPhase 2: Running retrograde analysis...")
    analyzer = RetrogradeAnalyzer(tree)
    results = analyzer.analyze()

    # Print standard results
    print_results_summary(results)

    # Print refined ratio
    print("\n" + "="*70)
    print("REFINED RATIO RESULTS (Safe Moves After Decrement)")
    print("="*70)
    print(f"{'Depth':<8} {'Safe Moves':<15} {'Checkmates':<12} {'Dead Ends':<12} {'Ratio':<10}")
    print("-"*70)

    for depth, data in sorted(results['refined_ratio'].items()):
        ratio = data['ratio']
        ratio_str = f"{ratio:.2f}" if isinstance(ratio, (int, float)) else ratio
        print(f"{depth:<8} {data['safe_moves']:<15} {data['checkmates']:<12} "
              f"{data['dead_ends']:<12} {ratio_str:<10}")

    print("="*70)
    print("\nRefined Ratio Interpretation:")
    print("  Ratio = Safe Moves / (Checkmates + Dead Ends)")
    print("  * If ratio -> 1: Barrier is closing")
    print("  * If ratio stays high: More escapes than traps")
    print("="*70)

    # Save results
    results_file = 'results/starting_fen_results.json'
    
    # Convert sets to lists for JSON
    export_data = {
        'fen': STARTING_FEN,
        'max_depth': MAX_DEPTH,
        'total_positions': len(tree),
        'checkmates': len(results['checkmates']),
        'dead_ends': len(results['dead_ends']),
        'propagation_depth': results['propagation_depth'],
        'dominic_ratio': results['dominic_ratio'],
        'refined_ratio': results['refined_ratio']
    }
    
    with open(results_file, 'w') as f:
        json.dump(export_data, f, indent=2)

    print(f"\n[OK] Results saved to {results_file}")
    print(f"[OK] Database saved to chess_tree.db")


if __name__ == "__main__":
    main()
