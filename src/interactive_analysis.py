"""
Interactive Chess Analysis - User selects depth with time estimates
"""

import time
import platform
import psutil
from chess_bfs import ChessBFS
from retrograde_analysis import RetrogradeAnalyzer
from persistent_storage import ChessTreeStorage
import chess
import json
import os

def get_system_info():
    """Display system hardware info"""
    print("\n" + "="*70)
    print("SYSTEM INFORMATION")
    print("="*70)
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Processor: {platform.processor()}")
    print(f"CPU Cores: {psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical")
    print(f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print("="*70)

def estimate_time(target_depth, starting_fen):
    """
    Estimate time to complete based on:
    1. Existing data in database (if any)
    2. Standard Perft numbers
    3. Exponential growth calculations
    """
    
    # Standard perft positions per depth for starting FEN
    perft_estimates = {
        1: 20,
        2: 400,
        3: 8_902,
        4: 197_281,
        5: 4_865_609,
        6: 119_060_324,
        7: 3_195_901_860,
        8: 84_998_978_956,
        9: 2_439_530_234_167,
        10: 69_352_859_712_417
    }
    
    # Check if we have existing data
    storage = ChessTreeStorage('chess_tree.db')
    progress = storage.load_progress()
    storage.close()
    
    current_depth = 0
    positions_so_far = 0
    time_so_far = 0
    
    if progress and progress['starting_fen'] == starting_fen:
        current_depth = progress['current_depth']
        positions_so_far = progress['positions_analyzed']
        
        print(f"\n✓ Found existing progress: Depth {current_depth} ({positions_so_far:,} positions)")
        
        # Try to estimate time per position from what we have
        # Rough estimate: 10,000 positions/second on average hardware
        time_per_position = 0.0001  # 100 microseconds per position
    else:
        print(f"\nNo existing progress found. Starting from scratch.")
        time_per_position = 0.0001
    
    # Estimate positions to generate
    if target_depth <= current_depth:
        remaining_positions = 0
        estimated_seconds = 0
    else:
        # Estimate positions from current to target
        remaining_positions = 0
        for d in range(current_depth + 1, target_depth + 1):
            if d <= 10 and d in perft_estimates:
                remaining_positions += perft_estimates[d]
            else:
                # Rough exponential estimate beyond depth 10
                remaining_positions += perft_estimates[10] * (30 ** (d - 10))
        
        estimated_seconds = remaining_positions * time_per_position
    
    return {
        'current_depth': current_depth,
        'target_depth': target_depth,
        'remaining_positions': remaining_positions,
        'estimated_seconds': estimated_seconds,
        'already_completed': target_depth <= current_depth
    }

def format_time(seconds):
    """Convert seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    elif seconds < 86400:
        return f"{seconds/3600:.1f} hours"
    elif seconds < 604800:
        return f"{seconds/86400:.1f} days"
    else:
        return f"{seconds/604800:.1f} weeks"

def display_estimate(estimate):
    """Show time estimate to user"""
    print("\n" + "="*70)
    print("TIME ESTIMATE")
    print("="*70)
    
    if estimate['already_completed']:
        print(f"✓ Depth {estimate['target_depth']} already completed!")
        print(f"  Analysis can run instantly from database.")
        return True
    
    print(f"Current Depth: {estimate['current_depth']}")
    print(f"Target Depth:  {estimate['target_depth']}")
    print(f"")
    print(f"Estimated Positions to Generate: {estimate['remaining_positions']:,}")
    print(f"Estimated Time: {format_time(estimate['estimated_seconds'])}")
    print(f"")
    print(f"Note: This is a rough estimate. Actual time may vary by ±50%")
    print(f"      depending on your hardware and system load.")
    print("="*70)
    
    return False

def get_user_confirmation():
    """Ask user if they want to proceed"""
    print("\n" + "="*70)
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    return response in ['yes', 'y']

def main():
    """Main interactive flow"""
    print("\n" + "="*70)
    print("CHESS RETROGRADE ANALYSIS - INTERACTIVE MODE")
    print("="*70)
    print("\nThis tool analyzes chess positions using Dominic's Barrier Algorithm")
    print("and calculates the 'Refined Ratio' to test if escape routes close.")
    
    # Show system info
    get_system_info()
    
    # Position selection
    print("\n" + "="*70)
    print("POSITION SELECTION")
    print("="*70)
    print("\n1. Starting FEN (standard chess opening)")
    print("2. Custom FEN (enter your own)")
    
    choice = input("\nSelect position (1 or 2): ").strip()
    
    if choice == '2':
        starting_fen = input("Enter FEN: ").strip()
    else:
        starting_fen = chess.STARTING_FEN
        print(f"\nUsing Starting FEN: {starting_fen}")
    
    # Depth selection
    print("\n" + "="*70)
    print("DEPTH SELECTION")
    print("="*70)
    print("\nRecommended depths:")
    print("  • Depth 4-5: Quick test (~1 hour)")
    print("  • Depth 6-7: Medium test (~1 day)")
    print("  • Depth 8-10: Deep analysis (~1 week)")
    print("  • Depth 10+: Research-grade (weeks/months)")
    
    while True:
        try:
            target_depth = int(input("\nEnter target depth (1-15): ").strip())
            if 1 <= target_depth <= 15:
                break
            else:
                print("Please enter a number between 1 and 15")
        except ValueError:
            print("Please enter a valid number")
    
    # Calculate estimate
    print("\nCalculating time estimate...")
    estimate = estimate_time(target_depth, starting_fen)
    
    # Display estimate
    already_done = display_estimate(estimate)
    
    # Get confirmation
    if not already_done:
        if not get_user_confirmation():
            print("\nOperation cancelled by user.")
            return
    
    # Start the analysis
    print("\n" + "="*70)
    print("STARTING ANALYSIS")
    print("="*70)
    print("\nGenerating BFS tree...")
    print("(Progress will be displayed. You can stop with Ctrl+C and resume later)\n")
    
    start_time = time.time()
    
    # Generate tree
    bfs = ChessBFS(starting_fen)
    tree = bfs.generate_move_tree(max_depth=target_depth, resume=True, save_interval=1)
    
    bfs_time = time.time() - start_time
    
    print(f"\n✓ Tree generation complete in {format_time(bfs_time)}")
    print(f"✓ Total positions: {len(tree):,}")
    
    # Run retrograde analysis
    print("\nRunning retrograde analysis...")
    analysis_start = time.time()
    
    analyzer = RetrogradeAnalyzer(tree, starting_fen)
    results = analyzer.analyze()
    
    analysis_time = time.time() - analysis_start
    
    print(f"\n✓ Analysis complete in {format_time(analysis_time)}")
    
    # Display results
    print("\n" + "="*70)
    print("REFINED RATIO RESULTS")
    print("="*70)
    print(f"\n{'Depth':<8} {'Safe Moves':<15} {'Checkmates':<12} {'Dead Ends':<12} {'Ratio':<10}")
    print("-"*70)
    
    for depth_str, data in sorted(results['refined_ratio'].items(), key=lambda x: int(x[0])):
        depth = int(depth_str)
        ratio = data['ratio']
        ratio_str = f"{ratio:.2f}" if isinstance(ratio, (int, float)) and ratio != float('inf') else "∞"
        print(f"{depth:<8} {data['safe_moves']:<15,} {data['checkmates']:<12} "
              f"{data['dead_ends']:<12} {ratio_str:<10}")
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"\nTotal time: {format_time(time.time() - start_time)}")
    print(f"Database saved: chess_tree.db")
    print(f"Results saved: results/analysis_results.json")
    
    # Save results to JSON
    os.makedirs('results', exist_ok=True)
    
    with open('results/analysis_results.json', 'w') as f:
        json.dump({
            'starting_fen': starting_fen,
            'target_depth': target_depth,
            'total_positions': len(tree),
            'bfs_time_seconds': bfs_time,
            'analysis_time_seconds': analysis_time,
            'checkmates': len(results['checkmates']),
            'dead_ends': len(results['dead_ends']),
            'refined_ratio': results['refined_ratio']
        }, f, indent=2)
    
    print("\n✓ All done! You can run this script again to analyze deeper.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress has been saved.")
        print("Run this script again to resume from where you left off.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
