"""
Basic tkinter version of American Buddha Asset Namer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from threading import Thread
import queue

from processors.file_processor import FileProcessor
from processors.ai_analyzer import AIAnalyzer
from utils.logger import get_logger

logger = get_logger("MainWindow")

class AssetNamerApp:
    """Main application window - basic tkinter version"""
    
    def __init__(self, config):
        """Initialize the application"""
        self.config = config
        
        # Create basic tkinter window
        self.root = tk.Tk()
        self.root.title("American Buddha Asset Namer")
        self.root.geometry("900x600")
        self.root.configure(bg='white')
        
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
        
        # Make sure window is visible
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
    
    def _setup_ui(self):
        """Setup the user interface with basic tkinter"""
        # Title
        title = tk.Label(
            self.root,
            text="🎬 American Buddha Asset Namer",
            font=("Arial", 20, "bold"),
            bg='white',
            pady=10
        )
        title.pack()
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="AI-powered bulk file renaming for your media assets",
            font=("Arial", 12),
            bg='white',
            fg='gray'
        )
        instructions.pack()
        
        # Button frame
        button_frame = tk.Frame(self.root, bg='white')
        button_frame.pack(pady=20)
        
        # Select folder button
        self.select_btn = tk.Button(
            button_frame,
            text="📁 Select Folder",
            command=self._select_folder,
            font=("Arial", 12),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=0
        )
        self.select_btn.pack(side=tk.LEFT, padx=5)
        
        # Process button
        self.process_btn = tk.Button(
            button_frame,
            text="🤖 Analyze Files",
            command=self._process_files,
            font=("Arial", 12),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=0,
            state=tk.DISABLED
        )
        self.process_btn.pack(side=tk.LEFT, padx=5)
        
        # Apply button
        self.apply_btn = tk.Button(
            button_frame,
            text="✅ Apply Renames",
            command=self._apply_renames,
            font=("Arial", 12),
            bg='#FF9800',
            fg='white',
            padx=20,
            pady=10,
            relief=tk.RAISED,
            bd=0,
            state=tk.DISABLED
        )
        self.apply_btn.pack(side=tk.LEFT, padx=5)
        
        # Pattern selection
        pattern_frame = tk.Frame(self.root, bg='white')
        pattern_frame.pack()
        
        tk.Label(
            pattern_frame,
            text="Naming Pattern:",
            font=("Arial", 11),
            bg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        self.pattern_var = tk.StringVar(value="default")
        self.pattern_combo = ttk.Combobox(
            pattern_frame,
            textvariable=self.pattern_var,
            values=list(self.config.naming_patterns.keys()),
            width=30,
            state='readonly'
        )
        self.pattern_combo.pack(side=tk.LEFT)
        
        # Current folder label
        self.folder_label = tk.Label(
            self.root,
            text="No folder selected",
            font=("Arial", 10),
            bg='white',
            fg='gray'
        )
        self.folder_label.pack(pady=10)
        
        # File list
        list_frame = tk.Frame(self.root, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            bg='#f5f5f5',
            selectbackground='#2196F3',
            selectforeground='white'
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.root,
            variable=self.progress_var,
            length=300,
            mode='determinate'
        )
        
        # Status label
        self.status_label = tk.Label(
            self.root,
            text=f"Ready | AI: {'✅ Connected' if self.ai_analyzer.client else '❌ Not configured'}",
            font=("Arial", 10),
            bg='white',
            fg='green' if self.ai_analyzer.client else 'red'
        )
        self.status_label.pack(pady=5)
    
    def _center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _select_folder(self):
        """Select folder containing media files"""
        folder = filedialog.askdirectory(
            title="Select folder with images/videos",
            initialdir=str(Path.home() / "Desktop")
        )
        
        if folder:
            self.current_directory = Path(folder)
            self.folder_label.config(text=f"📁 {folder}")
            self._scan_directory()
    
    def _scan_directory(self):
        """Scan directory for media files"""
        self.file_listbox.delete(0, tk.END)
        self.suggestions = []
        
        self.scanned_files = self.file_processor.scan_directory(self.current_directory)
        
        if self.scanned_files:
            self.file_listbox.insert(tk.END, f"Found {len(self.scanned_files)} media files:")
            self.file_listbox.insert(tk.END, "-" * 50)
            
            for file in self.scanned_files:
                self.file_listbox.insert(tk.END, f"📄 {file.name}")
            
            self.process_btn.config(state=tk.NORMAL)
        else:
            self.file_listbox.insert(tk.END, "No media files found in this folder")
            self.process_btn.config(state=tk.DISABLED)
    
    def _process_files(self):
        """Process files with AI"""
        if not self.scanned_files:
            return
        
        # Show progress
        self.progress_bar.pack(pady=10)
        self.progress_var.set(0)
        self.process_btn.config(state=tk.DISABLED)
        
        # Process in thread
        thread = Thread(target=self._process_worker)
        thread.daemon = True
        thread.start()
        
        self.root.after(100, self._check_queue)
    
    def _process_worker(self):
        """Worker thread for processing"""
        try:
            results = self.file_processor.process_files(
                self.scanned_files,
                pattern_name=self.pattern_var.get(),
                progress_callback=lambda c, t: self.processing_queue.put(("progress", (c, t)))
            )
            self.suggestions = results["suggestions"]
            self.processing_queue.put(("done", results))
        except Exception as e:
            self.processing_queue.put(("error", str(e)))
    
    def _check_queue(self):
        """Check processing queue"""
        try:
            while True:
                msg_type, data = self.processing_queue.get_nowait()
                
                if msg_type == "progress":
                    current, total = data
                    self.progress_var.set((current / total) * 100)
                
                elif msg_type == "done":
                    self._show_results()
                    return
                
                elif msg_type == "error":
                    messagebox.showerror("Error", f"Processing failed: {data}")
                    self.progress_bar.pack_forget()
                    self.process_btn.config(state=tk.NORMAL)
                    return
        
        except queue.Empty:
            pass
        
        self.root.after(100, self._check_queue)
    
    def _show_results(self):
        """Show processing results"""
        self.progress_bar.pack_forget()
        self.process_btn.config(state=tk.NORMAL)
        
        self.file_listbox.delete(0, tk.END)
        self.file_listbox.insert(tk.END, "✨ AI Analysis Complete!")
        self.file_listbox.insert(tk.END, "-" * 50)
        
        for suggestion in self.suggestions:
            if suggestion:
                old_name = suggestion['original_name']
                new_name = suggestion['new_name']
                self.file_listbox.insert(tk.END, f"{old_name}")
                self.file_listbox.insert(tk.END, f"  → {new_name}")
                self.file_listbox.insert(tk.END, "")
        
        if self.suggestions:
            self.apply_btn.config(state=tk.NORMAL)
    
    def _apply_renames(self):
        """Apply the renames"""
        if not self.suggestions:
            return
        
        if messagebox.askyesno("Confirm", f"Rename {len(self.suggestions)} files?"):
            results = self.file_processor.apply_renames(self.suggestions)
            
            messagebox.showinfo(
                "Success", 
                f"Renamed {results['renamed']} files!\nBackups saved in 'backup' folder."
            )
            
            self._scan_directory()
            self.apply_btn.config(state=tk.DISABLED)
    
    def run(self):
        """Run the application"""
        logger.info("Starting basic tkinter GUI")
        self.root.mainloop()