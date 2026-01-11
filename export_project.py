import os
import zipfile
import shutil
from datetime import datetime

def export_project():
    """
    Packages the entire project into a zip file for easy transfer.
    Includes source code, database, and results.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"chess_analysis_export_{timestamp}.zip"
    
    # Define what to include
    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, 'src')
    
    print(f"📦 Packaging project into {zip_filename}...")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Add README and Requirements
        for file in ['README.md', 'requirements.txt']:
            if os.path.exists(file):
                print(f"  Adding {file}...")
                zipf.write(file, arcname=file)
        
        # 2. Add Source Code (excluding __pycache__)
        print("  Adding source code...")
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith('.py') or file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_dir)
                    zipf.write(file_path, arcname=arcname)
        
        # 3. Add Database (Large file!)
        db_path = os.path.join(src_dir, 'chess_tree.db')
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            print(f"  Adding Database ({size_mb:.1f} MB)... This might take a moment.")
            zipf.write(db_path, arcname=os.path.join('src', 'chess_tree.db'))
            
    print("\n" + "="*60)
    print(f"✅ Export Complete: {zip_filename}")
    print("="*60)
    print(f"You can now download/move '{zip_filename}' to any other machine.")
    print("To run on a new machine:")
    print("1. Unzip the file")
    print("2. pip install -r requirements.txt")
    print("3. cd src")
    print("4. python analyze_from_db.py")

if __name__ == "__main__":
    export_project()
