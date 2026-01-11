
import time
import chess

def benchmark():
    print("Benchmarking move replay...")
    
    starting_fen = chess.STARTING_FEN
    moves = [chess.Move.from_uci('e2e4'), chess.Move.from_uci('e7e5'), chess.Move.from_uci('g1f3'), chess.Move.from_uci('b8c6')]
    
    start_time = time.time()
    iterations = 10000
    
    for _ in range(iterations):
        board = chess.Board(starting_fen)
        for move in moves:
            board.push(move)
        _ = board.fen()
        
    elapsed = time.time() - start_time
    avg_time = elapsed / iterations
    
    print(f"Time for {iterations} replays: {elapsed:.4f}s")
    print(f"Average time per replay: {avg_time:.6f}s")
    
    total_positions = 1500000
    estimated_total = total_positions * avg_time
    print(f"Estimated time for 1.5M positions: {estimated_total:.2f}s ({estimated_total/60:.2f} mins)")

if __name__ == "__main__":
    benchmark()
