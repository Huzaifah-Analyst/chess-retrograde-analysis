"""
Chess Retrograde Analysis - GUI Application
Built with Tkinter (Native Python GUI) - No external dependencies required
"""

import sys
import os
import time
import platform
import psutil
import json
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Import analysis modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from chess_bfs import ChessBFS
from retrograde_analysis import RetrogradeAnalyzer
from interactive_analysis import estimate_time, format_time
import chess

class AnalysisWorker(threading.Thread):
    """Worker thread for running analysis without freezing UI"""
    def __init__(self, starting_fen, target_depth, resume, msg_queue, progress_queue, result_queue):
        super().__init__()
        self.starting_fen = starting_fen
        self.target_depth = target_depth
        self.resume = resume
        self.msg_queue = msg_queue
        self.progress_queue = progress_queue
        self.result_queue = result_queue
        self.is_running = True
        self.daemon = True  # Thread dies if main app closes

    def log(self, msg):
        self.msg_queue.put(msg)

    def run(self):
        try:
            # Clear DB if not resuming
            if not self.resume:
                self.log("Clearing previous database...")
                from persistent_storage import ChessTreeStorage
                storage = ChessTreeStorage('chess_tree.db')
                storage.clear()
                storage.close()
                self.log("Database cleared.")

            self.log(f"Starting analysis for depth {self.target_depth}...")
            self.log(f"FEN: {self.starting_fen}")
            self.log(f"Resume Mode: {'ON' if self.resume else 'OFF'}")
            
            start_time = time.time()
            
            # 1. Generate Tree
            self.log("\n--- Phase 1: Generating Move Tree (BFS) ---")
            bfs = ChessBFS(self.starting_fen)
            
            # We can't easily hook into the BFS progress without modifying it,
            # so we'll simulate progress updates or just wait.
            self.progress_queue.put(10) # Started
            
            tree = bfs.generate_move_tree(max_depth=self.target_depth, resume=self.resume, save_interval=1)
            
            if not self.is_running:
                return

            bfs_time = time.time() - start_time
            self.log(f"Tree generation complete: {len(tree):,} positions in {bfs_time:.1f}s")
            self.progress_queue.put(80) # BFS Done
            
            # 2. Retrograde Analysis
            self.log("\n--- Phase 2: Retrograde Analysis ---")
            analyzer = RetrogradeAnalyzer(tree, self.starting_fen)
            
            results = analyzer.analyze()
            
            analysis_time = time.time() - start_time - bfs_time
            self.log(f"Analysis complete in {analysis_time:.1f}s")
            self.progress_queue.put(100) # Done
            
            # Add timing info
            results['timing'] = {
                'bfs_time': bfs_time,
                'analysis_time': analysis_time,
                'total_time': time.time() - start_time
            }
            
            self.result_queue.put(results)
            
        except Exception as e:
            import traceback
            self.log(f"\nERROR: {str(e)}")
            self.log(traceback.format_exc())
            self.result_queue.put({"error": str(e)})

    def stop(self):
        self.is_running = False

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Retrograde Analysis")
        self.root.geometry("900x700")
        
        # Queues for thread communication
        self.msg_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.worker = None
        self.current_results = None
        
        self.setup_ui()
        self.start_monitoring()

    def setup_ui(self):
        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # --- Analysis Tab ---
        self.tab_analysis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analysis, text='Analysis')
        self.setup_analysis_tab()
        
        # --- Results Tab ---
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text='Results')
        self.setup_results_tab()

    def setup_analysis_tab(self):
        # 1. System Info
        info_frame = ttk.LabelFrame(self.tab_analysis, text="System Information", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        cpu_info = f"CPU: {platform.processor()} ({psutil.cpu_count(logical=False)} cores)"
        ram_info = f"RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB"
        
        ttk.Label(info_frame, text=cpu_info).pack(anchor='w')
        ttk.Label(info_frame, text=ram_info).pack(anchor='w')
        
        # 2. Configuration
        config_frame = ttk.LabelFrame(self.tab_analysis, text="Configuration", padding=10)
        config_frame.pack(fill='x', padx=10, pady=5)
        
        # FEN Selection
        self.fen_var = tk.StringVar(value="start")
        ttk.Radiobutton(config_frame, text="Starting FEN", variable=self.fen_var, value="start", 
                       command=self.toggle_fen_input).pack(anchor='w')
        
        custom_frame = ttk.Frame(config_frame)
        custom_frame.pack(fill='x', pady=2)
        ttk.Radiobutton(custom_frame, text="Custom FEN", variable=self.fen_var, value="custom",
                       command=self.toggle_fen_input).pack(side='left')
        
        self.entry_fen = ttk.Entry(custom_frame)
        self.entry_fen.pack(side='left', fill='x', expand=True, padx=5)
        self.entry_fen.state(['disabled'])
        
        # Depth Selection
        depth_frame = ttk.Frame(config_frame)
        depth_frame.pack(fill='x', pady=10)
        
        ttk.Label(depth_frame, text="Target Depth:").pack(side='left')
        self.spin_depth = ttk.Spinbox(depth_frame, from_=1, to=15, width=5)
        self.spin_depth.set(5)
        self.spin_depth.pack(side='left', padx=5)
        
        ttk.Button(depth_frame, text="Estimate Time", command=self.estimate_time).pack(side='left', padx=10)
        
        self.lbl_estimate = ttk.Label(config_frame, text="Ready to estimate.", foreground="gray")
        self.lbl_estimate.pack(anchor='w')

        # Resume Option
        self.var_resume = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Resume from saved progress (if available)", 
                       variable=self.var_resume).pack(anchor='w', pady=5)
        
        # 3. Actions
        action_frame = ttk.Frame(self.tab_analysis)
        action_frame.pack(fill='x', padx=10, pady=10)
        
        self.btn_start = ttk.Button(action_frame, text="Start Analysis", command=self.start_analysis)
        self.btn_start.pack(side='left', fill='x', expand=True, padx=5)
        
        self.btn_stop = ttk.Button(action_frame, text="Stop", command=self.stop_analysis, state='disabled')
        self.btn_stop.pack(side='left', fill='x', expand=True, padx=5)
        
        # 4. Progress & Logs
        self.progress = ttk.Progressbar(self.tab_analysis, mode='determinate')
        self.progress.pack(fill='x', padx=10, pady=5)
        
        self.txt_log = tk.Text(self.tab_analysis, height=15, font=("Consolas", 9))
        self.txt_log.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(self.txt_log, command=self.txt_log.yview)
        scrollbar.pack(side='right', fill='y')
        self.txt_log['yscrollcommand'] = scrollbar.set

    def setup_results_tab(self):
        # Table
        columns = ("Depth", "Safe Moves", "Checkmates", "Dead Ends", "Ratio")
        self.tree = ttk.Treeview(self.tab_results, columns=columns, show='headings')
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor='center')
            
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Export
        ttk.Button(self.tab_results, text="Export Results to JSON", command=self.export_results).pack(pady=10)

    def toggle_fen_input(self):
        if self.fen_var.get() == "custom":
            self.entry_fen.state(['!disabled'])
        else:
            self.entry_fen.state(['disabled'])

    def log(self, msg):
        self.txt_log.insert('end', msg + "\n")
        self.txt_log.see('end')

    def estimate_time(self):
        depth = int(self.spin_depth.get())
        fen = chess.STARTING_FEN if self.fen_var.get() == "start" else self.entry_fen.get().strip()
        
        if not fen:
            self.lbl_estimate.config(text="Error: Invalid FEN")
            return
            
        self.lbl_estimate.config(text="Calculating...")
        
        def run_estimation():
            try:
                est = estimate_time(depth, fen)
                time_str = format_time(est['estimated_seconds'])
                
                if est['already_completed']:
                    msg = f"Depth {depth} already completed! Analysis will be instant."
                else:
                    msg = f"Estimated: {est['remaining_positions']:,} positions (~{time_str})"
                
                # Update UI on main thread
                self.root.after(0, lambda: self.lbl_estimate.config(text=msg))
                
            except Exception as e:
                self.root.after(0, lambda: self.lbl_estimate.config(text=f"Error: {str(e)}"))

        threading.Thread(target=run_estimation, daemon=True).start()

    def start_analysis(self):
        try:
            depth = int(self.spin_depth.get())
            fen = chess.STARTING_FEN if self.fen_var.get() == "start" else self.entry_fen.get().strip()
            
            if not fen:
                messagebox.showerror("Error", "Please enter a valid FEN")
                return

            # UI State
            self.btn_start.state(['disabled'])
            self.btn_stop.state(['!disabled'])
            self.progress['value'] = 0
            self.txt_log.delete(1.0, 'end')
            
            resume = self.var_resume.get()
            if not resume:
                if not messagebox.askyesno("Confirm Delete", 
                    "You have chosen to start fresh.\n\nThis will DELETE all previous progress.\n\nAre you sure?"):
                    self.btn_start.state(['!disabled'])
                    self.btn_stop.state(['disabled'])
                    return

            # Start Thread
            self.worker = AnalysisWorker(fen, depth, resume, self.msg_queue, self.progress_queue, self.result_queue)
            self.worker.start()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_analysis(self):
        if self.worker:
            self.worker.stop()
            self.log("Stopping analysis...")
            self.btn_stop.state(['disabled'])

    def start_monitoring(self):
        """Poll queues for updates from worker thread"""
        # 1. Logs
        while not self.msg_queue.empty():
            msg = self.msg_queue.get_nowait()
            self.log(msg)
            
        # 2. Progress
        while not self.progress_queue.empty():
            val = self.progress_queue.get_nowait()
            self.progress['value'] = val
            
        # 3. Results
        while not self.result_queue.empty():
            res = self.result_queue.get_nowait()
            self.analysis_finished(res)
            
        # Schedule next check
        self.root.after(100, self.start_monitoring)

    def analysis_finished(self, results):
        self.btn_start.state(['!disabled'])
        self.btn_stop.state(['disabled'])
        self.progress['value'] = 100
        
        if "error" in results:
            messagebox.showerror("Analysis Failed", results["error"])
            return
            
        self.log("\nAnalysis Finished Successfully!")
        self.current_results = results
        self.populate_results(results)
        self.notebook.select(self.tab_results)

    def populate_results(self, results):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        ratio_data = results.get('refined_ratio', {})
        
        for depth_str, data in sorted(ratio_data.items(), key=lambda x: int(x[0])):
            depth = int(depth_str)
            ratio = data['ratio']
            ratio_str = f"{ratio:.2f}" if isinstance(ratio, (int, float)) and ratio != float('inf') else "∞"
            
            self.tree.insert('', 'end', values=(
                depth,
                f"{data['safe_moves']:,}",
                data['checkmates'],
                data['dead_ends'],
                ratio_str
            ))

    def export_results(self):
        if not self.current_results:
            messagebox.showwarning("No Results", "Please run an analysis first.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialfile=f"gui_export_{int(time.time())}.json"
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.current_results, f, indent=2)
                messagebox.showinfo("Success", f"Saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    # Set theme if available
    try:
        root.tk.call("source", "azure.tcl") # Optional theme support
        root.tk.call("set_theme", "light")
    except:
        pass
        
    app = ChessApp(root)
    root.mainloop()
