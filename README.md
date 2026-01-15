# Chess Retrograde Analysis - Week 3

Implementation of retrograde checkmate elimination algorithm for chess position analysis.

## Week 3 Deliverables

### 1. Features Implemented
- **Persistent Storage** (SQLite) - saves progress after each depth
- **Resume Capability** - automatically resumes from saved progress
- **Refined Ratio Calculation** - `Safe Moves / (Checkmates + Dead Ends)`
- **Starting FEN Analysis** - scalable to millions of positions

### 2. Test Results

#### Test A: Proof of Concept (K+Q vs K)
*Purpose: Prove algorithm works with checkmates present*
- **Depth**: 10
- **Positions**: 104,829
- **Checkmates Found**: 233
- **Refined Ratio**: 1,247.0 (Trending UP -> Barrier Weakening)
- **Result**: Algorithm correctly identifies checkmates and propagates backwards.

#### Test B: Starting FEN (Standard Chess)
*Purpose: Prove scalability on real board*
- **Depth**: 5
- **Positions**: ~4.8 Million
- **Checkmates**: 0 (Expected - games don't end in 5 moves)
- **Result**: System handles massive tree generation with persistent storage.

## Usage

### 🖥️ GUI Application (Recommended)

The entire project is consolidated into a single GUI application. This is the main entry point for all features.

```bash
python src/gui_app.py
```

**Features:**
- **Analysis Tab**: 
    - Configure and run new analyses (Starting FEN or Custom FEN).
    - Resume from saved progress.
    - View real-time logs and progress.
- **Results Tab**: 
    - View detailed results table (Safe Moves, Checkmates, Ratio).
    - Export results to JSON.
- **Tools Tab**:
    - **Run System Tests**: Verify the integrity of the algorithm and database.
    - **Check Database Progress**: View stats of the current database.
    - **Analyze from Database**: Run retrograde analysis on existing tree data without re-running BFS.

### Quick Start (Interactive Mode)

If you prefer the terminal:
```bash
python src/interactive_analysis.py
```

### View Results

- Results saved in `results/` directory.
- Tree saved in `chess_tree.db`.

## Refined Ratio

```
Ratio = Safe Moves / (Checkmates + Dead Ends)
```

- **If ratio → 1**: Barrier is closing
- **If ratio stays high**: More escapes than traps

## Project Structure

```
chess-retrograde-analysis/
├── src/
│   ├── chess_bfs.py            # Move tree generator with persistence
│   ├── retrograde_analysis.py  # Core decrement logic + refined ratio
│   ├── persistent_storage.py   # SQLite storage module
│   ├── run_starting_fen.py     # Starting position analysis
│   └── visualize.py            # Results visualization
├── results/                    # Test outputs (JSON)
├── chess_tree.db               # SQLite database (created on run)
└── docs/                       # Documentation
```

## Algorithm Approach

1. **BFS Move Generation**: Explore all possible moves breadth-first
2. **Checkmate Detection**: Identify terminal positions at each depth
3. **Retrograde Decrementing**: Reduce move counts for paths leading to checkmate
4. **Dead-End Tracking**: Mark positions with no winning continuations
5. **Refined Ratio**: Calculate safe moves vs barrier size after decrement

## Requirements

```
python-chess
numpy
pandas
matplotlib
```

Install: `pip install -r requirements.txt`
