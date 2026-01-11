"""
Run Retrograde Analysis from saved SQLite database
Useful for debugging or resuming analysis without re-running BFS
"""

import os
import sys
import json
import time
from persistent_storage import ChessTreeStorage
from retrograde_analysis import RetrogradeAnalyzer, print_results_summary

def main():
    db_path = 'chess_tree.db'
    
    print(f"Loading tree from {db_path}...")
    start_time = time.time()
    
    storage = ChessTreeStorage(db_path)
    tree, progress = storage.load_tree()
    storage.close()
    
    if not tree:
        print("No tree found in database!")
        return

    load_time = time.time() - start_time
    print(f"Loaded {len(tree)} positions in {load_time:.1f}s")
    
    # Get starting FEN from progress info if available, else default
    starting_fen = progress.get('starting_fen', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    print(f"Starting FEN: {starting_fen}")
    
    # Run analysis
    print("\nStarting Retrograde Analysis...")
    analyzer = RetrogradeAnalyzer(tree, starting_fen=starting_fen)
    results = analyzer.analyze()
    
    # Print results
    print_results_summary(results)
    
    # Save results
    results_file = 'results/starting_fen_results_from_db.json'
    analyzer.export_results(results_file)
    print(f"\nResults saved to {results_file}")

if __name__ == "__main__":
    main()
