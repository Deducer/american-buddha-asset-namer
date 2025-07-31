"""
Main application window for American Buddha Asset Namer
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
from ui.preview_panel import PreviewPanel
from ui.settings_dialog import SettingsDialog
from utils.logger import get_logger

# Set appearance mode and color theme
ctk.set_appearance_mode("Light")  # Force Light mode to avoid black screen on macOS
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

logger = get_logger("MainWindow")

class AssetNamerApp:
    """Main application window"""
    
    def __init__(self, config):
        """Initialize the application"""
        self.config = config
        self.root = ctk.CTk()
        self.root.title("American Buddha Asset Namer")
        self.root.geometry("1200x800")
        
        # Force window to front on macOS
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.focus_force()
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        
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
        self._setup_menu()
        
        # Center window
        self._center_window()
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top toolbar
        self._create_toolbar()
        
        # Main content area with paned window
        self.paned_window = ctk.CTkFrame(self.main_frame)
        self.paned_window.pack(fill="both", expand=True, pady=(10, 0))
        
        # Left panel - file list
        self._create_file_panel()
        
        # Right panel - preview and settings
        self._create_preview_panel()
        
        # Bottom status bar
        self._create_status_bar()
    
    def _create_toolbar(self):
        """Create the toolbar"""
        toolbar = ctk.CTkFrame(self.main_frame, height=60)
        toolbar.pack(fill="x", pady=(0, 10))
        
        # Select folder button
        self.select_folder_btn = ctk.CTkButton(
            toolbar,
            text="Select Folder",
            command=self._select_folder,
            width=150,
            height=40
        )
        self.select_folder_btn.pack(side="left", padx=5)
        
        # Process button
        self.process_btn = ctk.CTkButton(
            toolbar,
            text="Analyze Files",
            command=self._process_files,
            width=150,
            height=40,
            state="disabled"
        )
        self.process_btn.pack(side="left", padx=5)
        
        # Apply button
        self.apply_btn = ctk.CTkButton(
            toolbar,
            text="Apply Renames",
            command=self._apply_renames,
            width=150,
            height=40,
            state="disabled",
            fg_color="#28a745"
        )
        self.apply_btn.pack(side="left", padx=5)
        
        # Pattern selector
        pattern_frame = ctk.CTkFrame(toolbar)
        pattern_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(pattern_frame, text="Naming Pattern:").pack(side="left", padx=5)
        
        self.pattern_var = tk.StringVar(value="default")
        patterns = list(self.config.naming_patterns.keys())
        self.pattern_menu = ctk.CTkOptionMenu(
            pattern_frame,
            values=patterns,
            variable=self.pattern_var,
            width=200
        )
        self.pattern_menu.pack(side="left", padx=5)
        
        # Settings button
        self.settings_btn = ctk.CTkButton(
            toolbar,
            text="⚙",
            command=self._show_settings,
            width=40,
            height=40
        )
        self.settings_btn.pack(side="right", padx=5)
    
    def _create_file_panel(self):
        """Create the file list panel"""
        left_frame = ctk.CTkFrame(self.paned_window)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Header
        header = ctk.CTkFrame(left_frame)
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="Files to Process", font=("Arial", 16, "bold")).pack(side="left")
        self.file_count_label = ctk.CTkLabel(header, text="0 files")
        self.file_count_label.pack(side="right")
        
        # File list with scrollbar
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Create Treeview for file list
        self.file_tree = ttk.Treeview(
            list_frame,
            columns=("new_name", "status"),
            show="tree headings",
            selectmode="browse"
        )
        
        # Configure columns
        self.file_tree.heading("#0", text="Original Name")
        self.file_tree.heading("new_name", text="New Name")
        self.file_tree.heading("status", text="Status")
        
        self.file_tree.column("#0", width=300)
        self.file_tree.column("new_name", width=300)
        self.file_tree.column("status", width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient="horizontal", command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elements
        self.file_tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.file_tree.bind("<<TreeviewSelect>>", self._on_file_select)
        
        # Progress bar
        self.progress_frame = ctk.CTkFrame(left_frame)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            variable=self.progress_var
        )
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="")
    
    def _create_preview_panel(self):
        """Create the preview panel"""
        right_frame = ctk.CTkFrame(self.paned_window, width=400)
        right_frame.pack(side="right", fill="both", padx=(5, 0))
        right_frame.pack_propagate(False)
        
        # Preview panel
        self.preview_panel = PreviewPanel(right_frame, self.config)
        self.preview_panel.pack(fill="both", expand=True)
    
    def _create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ctk.CTkFrame(self.root, height=30)
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready")
        self.status_label.pack(side="left", padx=10)
        
        self.api_status_label = ctk.CTkLabel(
            self.status_bar,
            text="AI: " + ("Connected" if self.ai_analyzer.client else "Not configured"),
            text_color="#28a745" if self.ai_analyzer.client else "#dc3545"
        )
        self.api_status_label.pack(side="right", padx=10)
    
    def _setup_menu(self):
        """Setup application menu (Mac-style)"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select Folder...", command=self._select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Settings...", command=self._show_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Get window dimensions
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _select_folder(self):
        """Select folder dialog"""
        folder = filedialog.askdirectory(
            title="Select folder containing media files",
            initialdir=str(Path.home() / "Pictures")
        )
        
        if folder:
            self.current_directory = Path(folder)
            self._scan_directory()
    
    def _scan_directory(self):
        """Scan the selected directory for media files"""
        self.status_label.configure(text="Scanning directory...")
        
        # Clear previous results
        self.file_tree.delete(*self.file_tree.get_children())
        self.suggestions = []
        
        # Scan directory
        self.scanned_files = self.file_processor.scan_directory(self.current_directory)
        
        # Update UI
        self.file_count_label.configure(text=f"{len(self.scanned_files)} files")
        
        # Populate file list
        for file_path in self.scanned_files:
            self.file_tree.insert("", "end", text=file_path.name, values=("", "Pending"))
        
        # Enable process button
        self.process_btn.configure(state="normal" if self.scanned_files else "disabled")
        
        self.status_label.configure(text=f"Found {len(self.scanned_files)} files")
    
    def _process_files(self):
        """Process files in background thread"""
        if not self.scanned_files:
            return
        
        # Disable buttons
        self.process_btn.configure(state="disabled")
        self.apply_btn.configure(state="disabled")
        
        # Show progress
        self.progress_frame.pack(fill="x", pady=(10, 0))
        self.progress_bar.pack(fill="x", padx=10, pady=5)
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
                    self.progress_var.set(current / total)
                    self.progress_label.configure(text=f"Processing {current}/{total} files...")
                
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
        self.progress_frame.pack_forget()
        
        # Update file list with suggestions
        for i, (item_id, suggestion) in enumerate(zip(self.file_tree.get_children(), self.suggestions)):
            if suggestion:
                self.file_tree.item(
                    item_id,
                    values=(suggestion["new_name"], "Ready")
                )
        
        # Enable apply button
        self.apply_btn.configure(state="normal" if self.suggestions else "disabled")
        self.process_btn.configure(state="normal")
        
        # Update status
        self.status_label.configure(
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
        self.status_label.configure(text="Applying renames...")
        
        results = self.file_processor.apply_renames(self.suggestions)
        
        # Update status
        self.status_label.configure(
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
    
    def _on_file_select(self, event):
        """Handle file selection"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        # Get selected file index
        item = self.file_tree.item(selection[0])
        index = self.file_tree.index(selection[0])
        
        if index < len(self.scanned_files):
            file_path = self.scanned_files[index]
            
            # Get suggestion if available
            suggestion = None
            if index < len(self.suggestions):
                suggestion = self.suggestions[index]
            
            # Update preview
            self.preview_panel.show_file(file_path, suggestion)
    
    def _show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.root, self.config)
        dialog.show()
    
    def _show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About American Buddha Asset Namer",
            "American Buddha Asset Namer v1.0\n\n"
            "AI-powered bulk media file naming tool\n"
            "for documentary production teams.\n\n"
            "© 2024 American Buddha Productions"
        )
    
    def _reset_ui(self):
        """Reset UI after error"""
        self.progress_frame.pack_forget()
        self.process_btn.configure(state="normal" if self.scanned_files else "disabled")
    
    def run(self):
        """Run the application"""
        logger.info("Starting GUI mainloop")
        self.root.update()
        self.root.deiconify()
        self.root.mainloop()