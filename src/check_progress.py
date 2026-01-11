import sqlite3
import json

def check_progress():
    try:
        conn = sqlite3.connect('chess_tree.db')
        cursor = conn.cursor()
        
        # Check progress table
        cursor.execute('SELECT * FROM progress ORDER BY id DESC LIMIT 1')
        progress = cursor.fetchone()
        
        if progress:
            print(f"Found saved progress:")
            print(f"  Starting FEN: {progress[1]}")
            print(f"  Current Depth: {progress[2]}")
            print(f"  Max Depth: {progress[3]}")
            print(f"  Positions Analyzed: {progress[4]:,}")
            print(f"  Timestamp: {progress[5]}")
        else:
            print("No progress found in database.")
            
        # Check positions count
        cursor.execute('SELECT count(*) FROM positions')
        count = cursor.fetchone()[0]
        print(f"Total positions stored: {count:,}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_progress()
