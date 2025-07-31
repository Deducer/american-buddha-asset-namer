"""
Settings dialog for configuring the application
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, Any
import os
from pathlib import Path

from utils.logger import get_logger

logger = get_logger("SettingsDialog")

class SettingsDialog:
    """Settings dialog window"""
    
    def __init__(self, parent, config):
        """Initialize settings dialog"""
        self.parent = parent
        self.config = config
        self.dialog = None
        self.result = None
    
    def show(self):
        """Show the settings dialog"""
        # Create dialog window
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Settings")
        self.dialog.geometry("600x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        # Setup UI
        self._setup_ui()
        
        # Load current settings
        self._load_settings()
        
        # Wait for dialog to close
        self.parent.wait_window(self.dialog)
        
        return self.result
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get parent position
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Get dialog size
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def _setup_ui(self):
        """Setup the UI components"""
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(self.dialog)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs
        self.general_tab = self.notebook.add("General")
        self.ai_tab = self.notebook.add("AI Settings")
        self.naming_tab = self.notebook.add("Naming Patterns")
        self.advanced_tab = self.notebook.add("Advanced")
        
        # Setup each tab
        self._setup_general_tab()
        self._setup_ai_tab()
        self._setup_naming_tab()
        self._setup_advanced_tab()
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._cancel,
            width=100
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save,
            width=100
        ).pack(side="right", padx=5)
    
    def _setup_general_tab(self):
        """Setup general settings tab"""
        # Date format
        date_frame = ctk.CTkFrame(self.general_tab)
        date_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            date_frame,
            text="Date Format:",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.date_format_var = tk.StringVar()
        date_formats = ["%Y-%m-%d", "%Y%m%d", "%d-%m-%Y", "%m-%d-%Y"]
        self.date_format_menu = ctk.CTkOptionMenu(
            date_frame,
            values=date_formats,
            variable=self.date_format_var,
            width=200
        )
        self.date_format_menu.pack(side="left", padx=10)
        
        # Sequence padding
        padding_frame = ctk.CTkFrame(self.general_tab)
        padding_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            padding_frame,
            text="Sequence Padding:",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.padding_var = tk.IntVar()
        self.padding_slider = ctk.CTkSlider(
            padding_frame,
            from_=1,
            to=5,
            variable=self.padding_var,
            number_of_steps=4,
            width=200
        )
        self.padding_slider.pack(side="left", padx=10)
        
        self.padding_label = ctk.CTkLabel(padding_frame, text="")
        self.padding_label.pack(side="left", padx=10)
        
        # Update label when slider changes
        self.padding_var.trace("w", self._update_padding_label)
        
        # Lowercase names
        self.lowercase_var = tk.BooleanVar()
        self.lowercase_check = ctk.CTkCheckBox(
            self.general_tab,
            text="Convert names to lowercase",
            variable=self.lowercase_var
        )
        self.lowercase_check.pack(pady=10, padx=20, anchor="w")
        
        # Replace spaces
        replace_frame = ctk.CTkFrame(self.general_tab)
        replace_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            replace_frame,
            text="Replace spaces with:",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.replace_spaces_var = tk.StringVar()
        self.replace_spaces_entry = ctk.CTkEntry(
            replace_frame,
            textvariable=self.replace_spaces_var,
            width=100
        )
        self.replace_spaces_entry.pack(side="left", padx=10)
        
        # Backup originals
        self.backup_var = tk.BooleanVar()
        self.backup_check = ctk.CTkCheckBox(
            self.general_tab,
            text="Backup original files before renaming",
            variable=self.backup_var
        )
        self.backup_check.pack(pady=10, padx=20, anchor="w")
    
    def _setup_ai_tab(self):
        """Setup AI settings tab"""
        # API Key
        api_frame = ctk.CTkFrame(self.ai_tab)
        api_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            api_frame,
            text="OpenAI API Key:",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ctk.CTkEntry(
            api_frame,
            textvariable=self.api_key_var,
            width=300,
            show="*"
        )
        self.api_key_entry.pack(side="left", padx=10)
        
        # Show/hide button
        self.show_key_btn = ctk.CTkButton(
            api_frame,
            text="Show",
            command=self._toggle_api_key,
            width=60
        )
        self.show_key_btn.pack(side="left", padx=5)
        
        # Model selection
        model_frame = ctk.CTkFrame(self.ai_tab)
        model_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            model_frame,
            text="AI Model:",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.model_var = tk.StringVar()
        models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        self.model_menu = ctk.CTkOptionMenu(
            model_frame,
            values=models,
            variable=self.model_var,
            width=200
        )
        self.model_menu.pack(side="left", padx=10)
        
        # Temperature
        temp_frame = ctk.CTkFrame(self.ai_tab)
        temp_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            temp_frame,
            text="Temperature:",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.temp_var = tk.DoubleVar()
        self.temp_slider = ctk.CTkSlider(
            temp_frame,
            from_=0,
            to=1,
            variable=self.temp_var,
            width=200
        )
        self.temp_slider.pack(side="left", padx=10)
        
        self.temp_label = ctk.CTkLabel(temp_frame, text="")
        self.temp_label.pack(side="left", padx=10)
        
        self.temp_var.trace("w", self._update_temp_label)
        
        # Max tokens
        tokens_frame = ctk.CTkFrame(self.ai_tab)
        tokens_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            tokens_frame,
            text="Max Tokens:",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.tokens_var = tk.IntVar()
        self.tokens_slider = ctk.CTkSlider(
            tokens_frame,
            from_=50,
            to=300,
            variable=self.tokens_var,
            number_of_steps=25,
            width=200
        )
        self.tokens_slider.pack(side="left", padx=10)
        
        self.tokens_label = ctk.CTkLabel(tokens_frame, text="")
        self.tokens_label.pack(side="left", padx=10)
        
        self.tokens_var.trace("w", self._update_tokens_label)
    
    def _setup_naming_tab(self):
        """Setup naming patterns tab"""
        # Instructions
        ctk.CTkLabel(
            self.naming_tab,
            text="Define custom naming patterns using placeholders:",
            font=("Arial", 14)
        ).pack(pady=10)
        
        # Placeholder info
        info_frame = ctk.CTkFrame(self.naming_tab)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        placeholders = [
            ("{date}", "File date in selected format"),
            ("{description}", "AI-generated description"),
            ("{sequence}", "Sequential number"),
            ("{scene}", "Scene type (interview, b-roll, etc.)"),
            ("{location}", "Location from AI analysis"),
            ("{subject}", "Main subjects identified"),
            ("{action}", "Action in the scene"),
            ("{original}", "Original filename")
        ]
        
        for placeholder, desc in placeholders:
            frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                frame,
                text=placeholder,
                font=("Courier", 12, "bold"),
                width=120,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                frame,
                text=desc,
                anchor="w"
            ).pack(side="left", padx=10)
        
        # Pattern list
        patterns_label = ctk.CTkLabel(
            self.naming_tab,
            text="Naming Patterns:",
            font=("Arial", 14, "bold")
        )
        patterns_label.pack(pady=(20, 10))
        
        # Pattern editor frame
        self.patterns_frame = ctk.CTkScrollableFrame(self.naming_tab, height=200)
        self.patterns_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.pattern_entries = {}
    
    def _setup_advanced_tab(self):
        """Setup advanced settings tab"""
        # Batch size
        batch_frame = ctk.CTkFrame(self.advanced_tab)
        batch_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            batch_frame,
            text="Batch Size:",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.batch_var = tk.IntVar()
        self.batch_slider = ctk.CTkSlider(
            batch_frame,
            from_=1,
            to=50,
            variable=self.batch_var,
            number_of_steps=49,
            width=200
        )
        self.batch_slider.pack(side="left", padx=10)
        
        self.batch_label = ctk.CTkLabel(batch_frame, text="")
        self.batch_label.pack(side="left", padx=10)
        
        self.batch_var.trace("w", self._update_batch_label)
        
        # Max file size
        size_frame = ctk.CTkFrame(self.advanced_tab)
        size_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            size_frame,
            text="Max File Size (MB):",
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        self.max_size_var = tk.IntVar()
        self.max_size_entry = ctk.CTkEntry(
            size_frame,
            textvariable=self.max_size_var,
            width=100
        )
        self.max_size_entry.pack(side="left", padx=10)
        
        # Preview thumbnails
        self.preview_var = tk.BooleanVar()
        self.preview_check = ctk.CTkCheckBox(
            self.advanced_tab,
            text="Generate preview thumbnails",
            variable=self.preview_var
        )
        self.preview_check.pack(pady=10, padx=20, anchor="w")
    
    def _load_settings(self):
        """Load current settings into UI"""
        # General settings
        self.date_format_var.set(self.config.get("output.date_format", "%Y-%m-%d"))
        self.padding_var.set(self.config.get("output.sequence_padding", 3))
        self.lowercase_var.set(self.config.get("output.lowercase_names", False))
        self.replace_spaces_var.set(self.config.get("output.replace_spaces", "_"))
        self.backup_var.set(self.config.get("processing.backup_originals", True))
        
        # AI settings
        self.api_key_var.set(os.getenv("OPENAI_API_KEY", ""))
        self.model_var.set(self.config.get("ai_settings.model", "gpt-4o"))
        self.temp_var.set(self.config.get("ai_settings.temperature", 0.7))
        self.tokens_var.set(self.config.get("ai_settings.max_tokens", 150))
        
        # Naming patterns
        patterns = self.config.naming_patterns
        for name, pattern in patterns.items():
            self._add_pattern_entry(name, pattern)
        
        # Advanced settings
        self.batch_var.set(self.config.get("processing.batch_size", 10))
        self.max_size_var.set(self.config.get("processing.max_file_size_mb", 100))
        self.preview_var.set(self.config.get("processing.preview_thumbnails", True))
    
    def _add_pattern_entry(self, name: str, pattern: str):
        """Add a pattern entry to the list"""
        frame = ctk.CTkFrame(self.patterns_frame)
        frame.pack(fill="x", pady=5)
        
        # Name entry
        name_entry = ctk.CTkEntry(frame, width=150)
        name_entry.insert(0, name)
        name_entry.pack(side="left", padx=5)
        
        # Pattern entry
        pattern_entry = ctk.CTkEntry(frame, width=300)
        pattern_entry.insert(0, pattern)
        pattern_entry.pack(side="left", padx=5)
        
        # Store references
        self.pattern_entries[name] = (name_entry, pattern_entry, frame)
    
    def _update_padding_label(self, *args):
        """Update padding preview label"""
        padding = self.padding_var.get()
        self.padding_label.configure(text=f"{'1'.zfill(padding)}")
    
    def _update_temp_label(self, *args):
        """Update temperature label"""
        temp = self.temp_var.get()
        self.temp_label.configure(text=f"{temp:.2f}")
    
    def _update_tokens_label(self, *args):
        """Update tokens label"""
        tokens = self.tokens_var.get()
        self.tokens_label.configure(text=str(tokens))
    
    def _update_batch_label(self, *args):
        """Update batch size label"""
        batch = self.batch_var.get()
        self.batch_label.configure(text=f"{batch} files")
    
    def _toggle_api_key(self):
        """Toggle API key visibility"""
        if self.api_key_entry.cget("show") == "*":
            self.api_key_entry.configure(show="")
            self.show_key_btn.configure(text="Hide")
        else:
            self.api_key_entry.configure(show="*")
            self.show_key_btn.configure(text="Show")
    
    def _save(self):
        """Save settings and close dialog"""
        try:
            # Update config
            self.config.set("output.date_format", self.date_format_var.get())
            self.config.set("output.sequence_padding", self.padding_var.get())
            self.config.set("output.lowercase_names", self.lowercase_var.get())
            self.config.set("output.replace_spaces", self.replace_spaces_var.get())
            self.config.set("processing.backup_originals", self.backup_var.get())
            
            # AI settings
            self.config.set("ai_settings.model", self.model_var.get())
            self.config.set("ai_settings.temperature", self.temp_var.get())
            self.config.set("ai_settings.max_tokens", self.tokens_var.get())
            
            # Save API key to environment
            api_key = self.api_key_var.get()
            if api_key:
                # Update .env file
                env_path = Path(".env")
                env_content = f"OPENAI_API_KEY={api_key}\n"
                
                # Preserve other env vars if file exists
                if env_path.exists():
                    with open(env_path, 'r') as f:
                        lines = f.readlines()
                    
                    # Update or add API key
                    updated = False
                    new_lines = []
                    for line in lines:
                        if line.startswith("OPENAI_API_KEY="):
                            new_lines.append(env_content)
                            updated = True
                        else:
                            new_lines.append(line)
                    
                    if not updated:
                        new_lines.append(env_content)
                    
                    env_content = "".join(new_lines)
                
                with open(env_path, 'w') as f:
                    f.write(env_content)
                
                # Update environment
                os.environ["OPENAI_API_KEY"] = api_key
            
            # Naming patterns
            patterns = {}
            for name, (name_entry, pattern_entry, _) in self.pattern_entries.items():
                new_name = name_entry.get().strip()
                new_pattern = pattern_entry.get().strip()
                if new_name and new_pattern:
                    patterns[new_name] = new_pattern
            
            self.config.set("naming_patterns", patterns)
            
            # Advanced settings
            self.config.set("processing.batch_size", self.batch_var.get())
            self.config.set("processing.max_file_size_mb", self.max_size_var.get())
            self.config.set("processing.preview_thumbnails", self.preview_var.get())
            
            # Save config
            self.config.save()
            
            self.result = True
            self.dialog.destroy()
            
            messagebox.showinfo("Settings Saved", "Your settings have been saved successfully.")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _cancel(self):
        """Cancel and close dialog"""
        self.result = False
        self.dialog.destroy()