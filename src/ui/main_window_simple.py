"""
Simplified main application window for American Buddha Asset Namer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
from threading import Thread
import queue
from typing import List, Dict, Any

from processors.file_processor import FileProcessor
from processors.ai_analyzer import AIAnalyzer
from utils.logger import get_logger

logger = get_logger("MainWindow")

class AssetNamerApp:
    """Main application window - simplified version"""
    
    def __init__(self, config):
        """Initialize the application"""
        self.config = config
        
        # Use standard tkinter root with customtkinter styling
        self.root = tk.Tk()
        self.root.title("American Buddha Asset Namer")
        self.root.geometry("1000x700")
        
        # Set background color
        self.root.configure(bg='#f0f0f0')
        
        # Initialize processors
        self.ai_analyzer = AIAnalyzer()
        self.file_processor = FileProcessor(self.config, self.ai_analyzer)
        
        # State
        self.current_directory = None
        self.scanned_files = []
        self.suggestions = []
        self.processing_queue = queue.Queue()
        
        # Setup UI
        self._setup_ui()
        
        # Center window
        self._center_window()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="American Buddha Asset Namer",
            font=("Arial", 24, "bold"),
            bg='#f0f0f0'
        )
        title_label.pack(pady=(0, 20))
        
        # Top toolbar
        toolbar = tk.Frame(main_frame, bg='#f0f0f0', height=50)
        toolbar.pack(fill="x", pady=(0, 20))
        
        # Select folder button
        self.select_folder_btn = tk.Button(
            toolbar,
            text="Select Folder",
            command=self._select_folder,
            font=("Arial", 14),
            bg='#007AFF',
            fg='white',
            padx=20,
            pady=10
        )
        self.select_folder_btn.pack(side="left", padx=5)
        
        # Process button
        self.process_btn = tk.Button(
            toolbar,
            text="Analyze Files",
            command=self._process_files,
            font=("Arial", 14),
            bg='#34C759',
            fg='white',
            padx=20,
            pady=10,
            state="disabled"
        )
        self.process_btn.pack(side="left", padx=5)
        
        # Apply button
        self.apply_btn = tk.Button(
            toolbar,
            text="Apply Renames",
            command=self._apply_renames,
            font=("Arial", 14),
            bg='#FF9500',
            fg='white',
            padx=20,
            pady=10,
            state="disabled"
        )
        self.apply_btn.pack(side="left", padx=5)
        
        # Pattern selector
        pattern_frame = tk.Frame(toolbar, bg='#f0f0f0')
        pattern_frame.pack(side="left", padx=20)
        
        tk.Label(
            pattern_frame,
            text="Naming Pattern:",
            font=("Arial", 12),
            bg='#f0f0f0'
        ).pack(side="left", padx=5)
        
        self.pattern_var = tk.StringVar(value="default")
        patterns = list(self.config.naming_patterns.keys())
        self.pattern_menu = ttk.Combobox(
            pattern_frame,
            textvariable=self.pattern_var,
            values=patterns,
            width=20,
            font=("Arial", 12)
        )
        self.pattern_menu.pack(side="left", padx=5)
        
        # File list frame
        list_frame = tk.Frame(main_frame, bg='white', relief="solid", borderwidth=1)
        list_frame.pack(fill="both", expand=True)
        
        # File list header
        header_frame = tk.Frame(list_frame, bg='#e0e0e0', height=40)
        header_frame.pack(fill="x")
        
        tk.Label(
            header_frame,
            text="Files to Process",
            font=("Arial", 16, "bold"),
            bg='#e0e0e0'
        ).pack(side="left", padx=10, pady=5)
        
        self.file_count_label = tk.Label(
            header_frame,
            text="0 files",
            font=("Arial", 12),
            bg='#e0e0e0'
        )
        self.file_count_label.pack(side="right", padx=10)
        
        # File listbox with scrollbar
        list_container = tk.Frame(list_frame, bg='white')
        list_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side="right", fill="y")
        
        self.file_listbox = tk.Listbox(
            list_container,
            yscrollcommand=scrollbar.set,
            font=("Arial", 11),
            selectmode="single"
        )
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Status bar
        self.status_bar = tk.Frame(main_frame, bg='#e0e0e0', height=30)
        self.status_bar.pack(fill="x", side="bottom", pady=(10, 0))
        
        self.status_label = tk.Label(
            self.status_bar,
            text="Ready",
            font=("Arial", 10),
            bg='#e0e0e0'
        )
        self.status_label.pack(side="left", padx=10)
        
        self.api_status_label = tk.Label(
            self.status_bar,
            text="AI: " + ("Connected" if self.ai_analyzer.client else "Not configured"),
            font=("Arial", 10),
            bg='#e0e0e0',
            fg='#34C759' if self.ai_analyzer.client else '#FF3B30'
        )
        self.api_status_label.pack(side="right", padx=10)
        
        # Progress bar (hidden initially)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 10),
            bg='#f0f0f0'
        )
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        window_width = 1000
        window_height = 700
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _select_folder(self):
        """Select folder dialog"""
        folder = filedialog.askdirectory(
            title="Select folder containing media files",
            initialdir=str(Path.home() / "Desktop")
        )
        
        if folder:
            self.current_directory = Path(folder)
            self._scan_directory()
    
    def _scan_directory(self):
        """Scan the selected directory for media files"""
        self.status_label.config(text="Scanning directory...")
        
        # Clear previous results
        self.file_listbox.delete(0, tk.END)
        self.suggestions = []
        
        # Scan directory
        self.scanned_files = self.file_processor.scan_directory(self.current_directory)
        
        # Update UI
        self.file_count_label.config(text=f"{len(self.scanned_files)} files")
        
        # Populate file list
        for file_path in self.scanned_files:
            self.file_listbox.insert(tk.END, file_path.name)
        
        # Enable process button
        self.process_btn.config(state="normal" if self.scanned_files else "disabled")
        
        self.status_label.config(text=f"Found {len(self.scanned_files)} files in {self.current_directory.name}")
    
    def _process_files(self):
        """Process files in background thread"""
        if not self.scanned_files:
            return
        
        # Disable buttons
        self.process_btn.config(state="disabled")
        self.apply_btn.config(state="disabled")
        
        # Show progress
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        self.progress_label.pack()
        self.progress_var.set(0)
        
        # Start processing in background
        thread = Thread(target=self._process_worker)
        thread.daemon = True
        thread.start()
        
        # Start checking queue
        self.root.after(100, self._check_processing_queue)
    
    def _process_worker(self):
        """Worker thread for processing files"""
        try:
            pattern_name = self.pattern_var.get()
            
            # Process files
            results = self.file_processor.process_files(
                self.scanned_files,
                pattern_name=pattern_name,
                progress_callback=self._update_progress
            )
            
            # Store suggestions
            self.suggestions = results["suggestions"]
            
            # Update queue
            self.processing_queue.put(("complete", results))
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            self.processing_queue.put(("error", str(e)))
    
    def _update_progress(self, current, total):
        """Update progress from worker thread"""
        self.processing_queue.put(("progress", (current, total)))
    
    def _check_processing_queue(self):
        """Check processing queue for updates"""
        try:
            while True:
                msg_type, data = self.processing_queue.get_nowait()
                
                if msg_type == "progress":
                    current, total = data
                    self.progress_var.set((current / total) * 100)
                    self.progress_label.config(text=f"Processing {current}/{total} files...")
                
                elif msg_type == "complete":
                    self._on_processing_complete(data)
                    return
                
                elif msg_type == "error":
                    messagebox.showerror("Processing Error", f"An error occurred: {data}")
                    self._reset_ui()
                    return
                    
        except queue.Empty:
            pass
        
        # Continue checking
        self.root.after(100, self._check_processing_queue)
    
    def _on_processing_complete(self, results):
        """Handle processing completion"""
        # Hide progress
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
        
        # Update file list with suggestions
        self.file_listbox.delete(0, tk.END)
        for suggestion in self.suggestions:
            if suggestion:
                display_text = f"{suggestion['original_name']} → {suggestion['new_name']}"
                self.file_listbox.insert(tk.END, display_text)
        
        # Enable apply button
        self.apply_btn.config(state="normal" if self.suggestions else "disabled")
        self.process_btn.config(state="normal")
        
        # Update status
        self.status_label.config(
            text=f"Processed {results['processed']} files, {results['errors']} errors"
        )
    
    def _apply_renames(self):
        """Apply the suggested renames"""
        if not self.suggestions:
            return
        
        # Confirm dialog
        result = messagebox.askyesno(
            "Confirm Rename",
            f"Are you sure you want to rename {len(self.suggestions)} files?\n\n"
            "Original files will be backed up."
        )
        
        if not result:
            return
        
        # Apply renames
        self.status_label.config(text="Applying renames...")
        
        results = self.file_processor.apply_renames(self.suggestions)
        
        # Update status
        self.status_label.config(
            text=f"Renamed {results['renamed']} files, {results['errors']} errors"
        )
        
        # Show completion message
        messagebox.showinfo(
            "Rename Complete",
            f"Successfully renamed {results['renamed']} files.\n"
            f"Backups saved to: backup/"
        )
        
        # Rescan directory
        self._scan_directory()
    
    def _reset_ui(self):
        """Reset UI after error"""
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
        self.process_btn.config(state="normal" if self.scanned_files else "disabled")
    
    def run(self):
        """Run the application"""
        logger.info("Starting GUI mainloop (simplified version)")
        self.root.mainloop()