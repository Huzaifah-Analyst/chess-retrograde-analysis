"""
Test Dominic's 2 checkmate conditions on known data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import chess
from checkmate_detector import CheckmateDetector
from persistent_storage import ChessTreeStorage

def test_on_known_checkmates():
    """
    Test conditions on the 109 known checkmates from depth 5
    Should match 100% of them
    """
    print("Loading known checkmates from database...")
    
    storage = ChessTreeStorage('chess_tree.db')
    tree, _ = storage.load_tree()  # Unpack tuple
    storage.close()
    
    # Find all checkmate positions
    checkmates = [fen for fen, data in tree.items() 
                  if data.get('is_checkmate', False)]
    
    print(f"Found {len(checkmates)} checkmate positions\n")
    
    detector = CheckmateDetector()
    
    # For each checkmate, find the move that led to it
    matched = 0
    missed = 0
    
    for checkmate_fen in checkmates:
        # Find parent positions
        parents = []
        for fen, data in tree.items():
            if checkmate_fen in data.get('children', []):
                parents.append(fen)
        
        # Test each parent's move to this checkmate
        for parent_fen in parents:
            parent_board = chess.Board(parent_fen)
            
            # Find which move leads to checkmate
            for move in parent_board.legal_moves:
                parent_board.push(move)
                if parent_board.fen().split()[0] == checkmate_fen.split()[0]:
                    # This is the checkmate move
                    parent_board.pop()
                    
                    # Test conditions
                    if detector.matches_conditions(parent_board, move):
                        matched += 1
                    else:
                        missed += 1
                        print(f"MISSED: {parent_fen} -> {move}")
                    
                    break
                parent_board.pop()
    
    print("\n" + "="*50)
    print("KNOWN CHECKMATE TEST RESULTS")
    print("="*50)
    print(f"Checkmates tested: {len(checkmates)}")
    print(f"Conditions matched: {matched}")
    print(f"Conditions missed: {missed}")
    if matched + missed > 0:
        print(f"Recall rate: {matched/(matched+missed)*100:.1f}%")
    else:
        print("Recall rate: N/A")
    print("="*50 + "\n")
    
    detector.print_stats()

def test_on_random_positions(num_samples=10000):
    """
    Test conditions on random non-checkmate positions
    Should have very low false positive rate
    """
    print(f"\nTesting on {num_samples:,} random positions...\n")
    
    storage = ChessTreeStorage('chess_tree.db')
    tree, _ = storage.load_tree()  # Unpack tuple
    storage.close()
    
    # Get non-checkmate positions
    non_checkmates = [fen for fen, data in tree.items() 
                      if not data.get('is_checkmate', False)]
    
    import random
    if non_checkmates:
        sample = random.sample(non_checkmates, 
                              min(num_samples, len(non_checkmates)))
    else:
        sample = []
        print("No non-checkmate positions found!")
    
    detector = CheckmateDetector()
    false_positives = 0
    
    for fen in sample:
        board = chess.Board(fen)
        
        for move in board.legal_moves:
            if detector.matches_conditions(board, move):
                # Verify it's actually checkmate
                if not detector.verify_is_checkmate(board, move):
                    false_positives += 1
    
    print("\n" + "="*50)
    print("RANDOM POSITION TEST RESULTS")
    print("="*50)
    print(f"Positions tested: {num_samples:,}")
    print(f"False positives: {false_positives}")
    print(f"False positive rate: {false_positives/num_samples*100:.2f}%")
    print("="*50 + "\n")
    
    detector.print_stats()

if __name__ == "__main__":
    print("="*50)
    print("TESTING DOMINIC'S 2 CHECKMATE CONDITIONS")
    print("="*50)
    print("\nCondition 1: King has no escape squares")
    print("Condition 2: Attack lines created or improved\n")
    
    # Test on known checkmates
    test_on_known_checkmates()
    
    # Test on random positions
    test_on_random_positions(10000)
    
    print("\nTesting complete!")
