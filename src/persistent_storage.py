"""
Persistent storage for chess BFS tree
Saves progress to SQLite database
"""

import sqlite3
import json
import chess
from datetime import datetime


class ChessTreeStorage:
    """Manages persistent storage of chess move tree"""
    
    def __init__(self, db_path='chess_tree.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                fen TEXT PRIMARY KEY,
                depth INTEGER,
                move_history TEXT,
                is_checkmate INTEGER,
                is_stalemate INTEGER,
                board_state TEXT
            )
        ''')
        
        # Progress tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY,
                starting_fen TEXT,
                current_depth INTEGER,
                max_depth INTEGER,
                positions_analyzed INTEGER,
                timestamp TEXT
            )
        ''')
        
        self.conn.commit()
    
    def save_tree(self, tree, starting_fen, current_depth, max_depth, positions_analyzed):
        """Save entire tree to database"""
        cursor = self.conn.cursor()
        
        print(f"Saving {len(tree)} positions to database...")
        
        # Save positions
        for fen, data in tree.items():
            cursor.execute('''
                INSERT OR REPLACE INTO positions 
                (fen, depth, move_history, is_checkmate, is_stalemate, board_state)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                fen,
                data['depth'],
                json.dumps([str(m) for m in data['moves']]),
                1 if data['is_checkmate'] else 0,
                1 if data['is_stalemate'] else 0,
                data['board'].fen()
            ))
        
        # Save progress
        cursor.execute('''
            INSERT INTO progress 
            (starting_fen, current_depth, max_depth, positions_analyzed, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            starting_fen,
            current_depth,
            max_depth,
            positions_analyzed,
            datetime.now().isoformat()
        ))
        
        self.conn.commit()
        print(f"[OK] Saved to {self.db_path}")
    
    def load_tree(self):
        """Load tree from database"""
        cursor = self.conn.cursor()
        
        # Get latest progress
        cursor.execute('SELECT * FROM progress ORDER BY id DESC LIMIT 1')
        progress = cursor.fetchone()
        
        if not progress:
            return None, None
        
        # Load positions
        cursor.execute('SELECT * FROM positions')
        rows = cursor.fetchall()
        
        tree = {}
        for row in rows:
            fen, depth, move_history, is_checkmate, is_stalemate, board_state = row
            
            board = chess.Board(board_state)
            moves = json.loads(move_history)
            
            tree[fen] = {
                'depth': depth,
                'moves': [chess.Move.from_uci(m) for m in moves],
                'is_checkmate': bool(is_checkmate),
                'is_stalemate': bool(is_stalemate),
                'board': board
            }
        
        progress_info = {
            'starting_fen': progress[1],
            'current_depth': progress[2],
            'max_depth': progress[3],
            'positions_analyzed': progress[4]
        }
        
        print(f"[OK] Loaded {len(tree)} positions from {self.db_path}")
        return tree, progress_info

    def load_progress(self):
        """Load only progress metadata (fast)"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM progress ORDER BY id DESC LIMIT 1')
        progress = cursor.fetchone()
        
        if not progress:
            return None
            
        return {
            'starting_fen': progress[1],
            'current_depth': progress[2],
            'max_depth': progress[3],
            'positions_analyzed': progress[4]
        }
    
    def clear(self):
        """Clear all data from database"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM positions')
        cursor.execute('DELETE FROM progress')
        self.conn.commit()
        print(f"[OK] Cleared all data from {self.db_path}")
    
    def close(self):
        """Close database connection"""
        self.conn.close()
