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

### 🖥️ GUI Application

The easiest way to use the tool is via the new Desktop GUI (built with Tkinter, no extra install needed):

```bash
cd src
python gui_app.py
```

Features:
- **Visual Configuration**: Select depth and FEN easily.
- **Resume Control**: Choose to resume analysis or start fresh (clear data).
- **Real-time Progress**: Watch the analysis steps.
- **Results Table**: View formatted results instantly.

### Quick Start (Interactive Mode)

If you prefer the terminal:
```bash
cd src
python interactive_analysis.py
```

This will:
1. Show your system specifications
2. Let you choose position and depth
3. **Estimate time required**
4. Ask for confirmation
5. Run the analysis with progress tracking

### Advanced Usage (Direct Scripts)

For automated/scripted runs:
```bash
python run_starting_fen.py  # Uses preset depth
python analyze_from_db.py   # Analyze existing data
```

### View Results

- Results saved in `results/starting_fen_results.json`
- Tree saved in `chess_tree.db`

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
