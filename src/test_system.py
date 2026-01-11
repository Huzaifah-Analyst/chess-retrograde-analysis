"""
Comprehensive system testing
"""
from persistent_storage import ChessTreeStorage
from retrograde_analysis import RetrogradeAnalyzer
import chess

print("="*70)
print("COMPREHENSIVE SYSTEM TEST")
print("="*70)

# Test 1: Tree Structure
print("\n[TEST 1] Tree Structure Validation")
print("-"*70)

storage = ChessTreeStorage('chess_tree.db')
tree, progress = storage.load_tree()

print(f"Total positions: {len(tree):,}")

# Check depth distribution
depths = {}
for fen, data in tree.items():
    d = data['depth']
    depths[d] = depths.get(d, 0) + 1

print("\nPositions per depth:")
for d in sorted(depths.keys()):
    print(f"  Depth {d}: {depths[d]:,}")

# Validate: Should have positions at ALL depths 0 to max
if depths:
    expected_depths = set(range(0, max(depths.keys()) + 1))
    actual_depths = set(depths.keys())
    missing = expected_depths - actual_depths

    if missing:
        print(f"\n❌ FAIL: Missing depths {sorted(missing)}")
        print("   → BFS not storing intermediate positions")
    else:
        print(f"\n✓ PASS: All depths 0-{max(depths.keys())} present")
else:
    print("\n❌ FAIL: Tree is empty")

# Test 2: Checkmate Validation
print("\n[TEST 2] Checkmate Position Validation")
print("-"*70)

checkmates = [fen for fen, data in tree.items() if data['is_checkmate']]
print(f"Checkmates found: {len(checkmates)}")

if checkmates:
    # Verify one manually
    test_fen = checkmates[0]
    test_board = chess.Board(test_fen)
    
    if test_board.is_checkmate():
        print(f"✓ PASS: Sample checkmate verified")
    else:
        print(f"❌ FAIL: Position marked as checkmate isn't actually checkmate")
        print(f"  FEN: {test_fen}")

# Test 3: Parent-Child Relationships
print("\n[TEST 3] Parent-Child Relationship Validation")
print("-"*70)

# Pick a depth 3 position
depth3_positions = [fen for fen, data in tree.items() if data['depth'] == 3]
if depth3_positions:
    test_fen = depth3_positions[0]
    test_data = tree[test_fen]
    
    print(f"Testing position at depth 3:")
    print(f"  FEN: {test_fen[:50]}...")
    print(f"  Move history length: {len(test_data['moves'])}")
    
    # Reconstruct parent
    if len(test_data['moves']) >= 1:
        board = chess.Board()
        for move in test_data['moves'][:-1]:
            board.push(move)
        
        parent_fen = board.fen()
        
        if parent_fen in tree:
            print(f"✓ PASS: Parent position exists in tree")
            print(f"  Parent depth: {tree[parent_fen]['depth']}")
        else:
            print(f"❌ FAIL: Parent position NOT in tree")
            print(f"  → Parent map will be empty")

# Test 4: Decrement Algorithm
print("\n[TEST 4] Decrement Algorithm Test")
print("-"*70)

analyzer = RetrogradeAnalyzer(tree)

# Check initial vs final move counts
print("Running analysis...")
results = analyzer.analyze()

print(f"Checkmates: {len(results['checkmates'])}")
print(f"Dead ends: {len(results['dead_ends'])}")

# Check if any move counts were modified
initial_total = sum(analyzer.initial_move_counts.values())
final_total = sum(analyzer.move_counts.values())

print(f"\nTotal initial move counts: {initial_total:,}")
print(f"Total final move counts: {final_total:,}")
print(f"Difference: {initial_total - final_total:,}")

if final_total < initial_total:
    print(f"✓ PASS: Decrement algorithm modified move counts")
else:
    print(f"❌ FAIL: Move counts unchanged")
    print(f"  → Decrement didn't propagate")

# Test 5: Ratio Calculation
print("\n[TEST 5] Ratio Calculation Validation")
print("-"*70)

for depth_str, data in sorted(results['refined_ratio'].items()):
    depth = int(depth_str)
    print(f"Depth {depth}: Ratio = {data['ratio']}")

print("\n✓ Ratio calculation complete")

# Test 6: Parent Map Size
print("\n[TEST 6] Parent Map Validation")
print("-"*70)

if hasattr(analyzer, 'parent_map'):
    print(f"Parent map size: {len(analyzer.parent_map):,} child positions")
    
    # Sample check
    if len(analyzer.parent_map) > 0:
        sample_child = list(analyzer.parent_map.keys())[0]
        sample_parents = analyzer.parent_map[sample_child]
        print(f"Sample: {len(sample_parents)} parents found for one child")
        print(f"✓ PASS: Parent map contains data")
    else:
        print(f"❌ FAIL: Parent map is empty")
else:
    print(f"❌ FAIL: Parent map not created")

print("\n" + "="*70)
print("TEST SUITE COMPLETE")
print("="*70)

storage.close()
