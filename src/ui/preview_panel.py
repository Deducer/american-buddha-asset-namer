"""
Preview panel for displaying file information and analysis results
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from pathlib import Path
from PIL import Image, ImageTk
import cv2
from typing import Dict, Any, Optional

from utils.logger import get_logger

logger = get_logger("PreviewPanel")

class PreviewPanel(ctk.CTkFrame):
    """Panel for previewing files and their analysis"""
    
    def __init__(self, parent, config):
        """Initialize preview panel"""
        super().__init__(parent)
        self.config = config
        self.current_file = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI components"""
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="File Preview",
            font=("Arial", 18, "bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        # Preview image frame
        self.preview_frame = ctk.CTkFrame(self, height=200)
        self.preview_frame.pack(fill="x", padx=10, pady=10)
        self.preview_frame.pack_propagate(False)
        
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="No file selected")
        self.preview_label.pack(expand=True)
        
        # Tabs for information
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # File Info tab
        self.info_tab = self.tab_view.add("File Info")
        self._create_info_tab()
        
        # AI Analysis tab
        self.analysis_tab = self.tab_view.add("AI Analysis")
        self._create_analysis_tab()
        
        # Naming tab
        self.naming_tab = self.tab_view.add("Naming")
        self._create_naming_tab()
    
    def _create_info_tab(self):
        """Create file info tab"""
        # Create scrollable frame
        self.info_frame = ctk.CTkScrollableFrame(self.info_tab)
        self.info_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Info labels
        self.info_labels = {}
        info_fields = [
            ("filename", "Filename:"),
            ("path", "Path:"),
            ("size", "Size:"),
            ("dimensions", "Dimensions:"),
            ("format", "Format:"),
            ("created", "Created:"),
            ("modified", "Modified:")
        ]
        
        for field, label in info_fields:
            frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=("Arial", 12, "bold"),
                width=100,
                anchor="w"
            ).pack(side="left")
            
            self.info_labels[field] = ctk.CTkLabel(
                frame,
                text="",
                anchor="w"
            )
            self.info_labels[field].pack(side="left", fill="x", expand=True)
    
    def _create_analysis_tab(self):
        """Create AI analysis tab"""
        # Create scrollable frame
        self.analysis_frame = ctk.CTkScrollableFrame(self.analysis_tab)
        self.analysis_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Analysis status
        self.analysis_status = ctk.CTkLabel(
            self.analysis_frame,
            text="No analysis available",
            font=("Arial", 12)
        )
        self.analysis_status.pack(pady=10)
        
        # Analysis details
        self.analysis_text = ctk.CTkTextbox(
            self.analysis_frame,
            height=200,
            wrap="word"
        )
    
    def _create_naming_tab(self):
        """Create naming tab"""
        # Create frame
        naming_frame = ctk.CTkFrame(self.naming_tab)
        naming_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Current name
        current_frame = ctk.CTkFrame(naming_frame)
        current_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            current_frame,
            text="Current:",
            font=("Arial", 12, "bold"),
            width=80
        ).pack(side="left")
        
        self.current_name_label = ctk.CTkLabel(
            current_frame,
            text="",
            anchor="w"
        )
        self.current_name_label.pack(side="left", fill="x", expand=True)
        
        # Suggested name
        suggested_frame = ctk.CTkFrame(naming_frame)
        suggested_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            suggested_frame,
            text="Suggested:",
            font=("Arial", 12, "bold"),
            width=80
        ).pack(side="left")
        
        self.suggested_name_label = ctk.CTkLabel(
            suggested_frame,
            text="",
            anchor="w",
            text_color="#28a745"
        )
        self.suggested_name_label.pack(side="left", fill="x", expand=True)
        
        # Pattern breakdown
        ctk.CTkLabel(
            naming_frame,
            text="Pattern Breakdown:",
            font=("Arial", 12, "bold")
        ).pack(pady=(20, 5))
        
        self.pattern_frame = ctk.CTkScrollableFrame(naming_frame, height=150)
        self.pattern_frame.pack(fill="both", expand=True, pady=5)
    
    def show_file(self, file_path: Path, suggestion: Optional[Dict[str, Any]] = None):
        """Show file preview and information"""
        self.current_file = file_path
        
        # Update preview
        self._update_preview(file_path)
        
        # Update file info
        self._update_file_info(file_path)
        
        # Update analysis if available
        if suggestion:
            self._update_analysis(suggestion.get("analysis", {}))
            self._update_naming(file_path, suggestion)
        else:
            self.analysis_status.configure(text="Not analyzed yet")
            self.analysis_text.pack_forget()
            self._clear_naming()
    
    def _update_preview(self, file_path: Path):
        """Update the preview image"""
        try:
            # Clear previous preview
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
            
            if file_path.suffix.lower() in self.config.supported_image_formats:
                # Load and display image
                img = Image.open(file_path)
                
                # Resize to fit preview
                img.thumbnail((380, 180), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Display
                label = tk.Label(self.preview_frame, image=photo)
                label.image = photo  # Keep reference
                label.pack(expand=True)
                
            elif file_path.suffix.lower() in self.config.supported_video_formats:
                # Extract video frame
                cap = cv2.VideoCapture(str(file_path))
                
                # Get middle frame
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
                
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # Convert to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    
                    # Resize
                    img.thumbnail((380, 180), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(img)
                    
                    # Display with video indicator
                    frame_container = tk.Frame(self.preview_frame)
                    frame_container.pack(expand=True)
                    
                    label = tk.Label(frame_container, image=photo)
                    label.image = photo
                    label.pack()
                    
                    # Video indicator
                    video_label = ctk.CTkLabel(
                        frame_container,
                        text="🎥 VIDEO",
                        font=("Arial", 12, "bold"),
                        text_color="#dc3545"
                    )
                    video_label.pack()
                else:
                    self._show_no_preview("Video preview unavailable")
            else:
                self._show_no_preview("Preview not available")
                
        except Exception as e:
            logger.error(f"Error creating preview: {e}")
            self._show_no_preview("Error loading preview")
    
    def _show_no_preview(self, message: str):
        """Show no preview message"""
        label = ctk.CTkLabel(self.preview_frame, text=message)
        label.pack(expand=True)
    
    def _update_file_info(self, file_path: Path):
        """Update file information"""
        stat = file_path.stat()
        
        # Get image/video dimensions if possible
        dimensions = "N/A"
        if file_path.suffix.lower() in self.config.supported_image_formats:
            try:
                img = Image.open(file_path)
                dimensions = f"{img.width} x {img.height}"
            except:
                pass
        elif file_path.suffix.lower() in self.config.supported_video_formats:
            try:
                cap = cv2.VideoCapture(str(file_path))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                cap.release()
                dimensions = f"{width} x {height} @ {fps:.1f}fps"
            except:
                pass
        
        # Update labels
        self.info_labels["filename"].configure(text=file_path.name)
        self.info_labels["path"].configure(text=str(file_path.parent))
        self.info_labels["size"].configure(text=f"{stat.st_size / (1024*1024):.2f} MB")
        self.info_labels["dimensions"].configure(text=dimensions)
        self.info_labels["format"].configure(text=file_path.suffix.upper()[1:])
        self.info_labels["created"].configure(
            text=Path(file_path).stat().st_birthtime if hasattr(stat, 'st_birthtime') else "N/A"
        )
        self.info_labels["modified"].configure(
            text=Path(file_path).stat().st_mtime
        )
    
    def _update_analysis(self, analysis: Dict[str, Any]):
        """Update AI analysis display"""
        if not analysis:
            self.analysis_status.configure(text="No analysis available")
            self.analysis_text.pack_forget()
            return
        
        # Update status
        if analysis.get("ai_analyzed"):
            self.analysis_status.configure(
                text="✅ AI Analysis Complete",
                text_color="#28a745"
            )
        else:
            self.analysis_status.configure(
                text="⚠️ Basic Analysis (No AI)",
                text_color="#ffc107"
            )
        
        # Format analysis data
        text_lines = []
        
        if "description" in analysis:
            text_lines.append(f"Description: {analysis['description']}")
        
        if "scene_type" in analysis:
            text_lines.append(f"Scene Type: {analysis['scene_type']}")
        
        if "subjects" in analysis and analysis["subjects"]:
            subjects = ", ".join(analysis["subjects"])
            text_lines.append(f"Subjects: {subjects}")
        
        if "location" in analysis:
            text_lines.append(f"Location: {analysis['location']}")
        
        if "action" in analysis:
            text_lines.append(f"Action: {analysis['action']}")
        
        if "mood" in analysis:
            text_lines.append(f"Mood: {analysis['mood']}")
        
        if "technical" in analysis and analysis["technical"]:
            text_lines.append("\nTechnical Details:")
            for key, value in analysis["technical"].items():
                text_lines.append(f"  {key}: {value}")
        
        # Update text
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.insert("1.0", "\n".join(text_lines))
        self.analysis_text.pack(fill="both", expand=True, pady=5)
    
    def _update_naming(self, file_path: Path, suggestion: Dict[str, Any]):
        """Update naming information"""
        # Update name labels
        self.current_name_label.configure(text=file_path.name)
        self.suggested_name_label.configure(text=suggestion.get("new_name", ""))
        
        # Clear pattern frame
        for widget in self.pattern_frame.winfo_children():
            widget.destroy()
        
        # Show pattern breakdown
        if "analysis" in suggestion:
            analysis = suggestion["analysis"]
            metadata = suggestion.get("metadata", {})
            
            # Create pattern breakdown
            pattern_parts = [
                ("Date", metadata.get("date", "").strftime("%Y-%m-%d") if "date" in metadata else ""),
                ("Description", analysis.get("description", "")),
                ("Scene Type", analysis.get("scene_type", "")),
                ("Location", analysis.get("location", "")),
                ("Subjects", ", ".join(analysis.get("subjects", []))),
                ("Action", analysis.get("action", ""))
            ]
            
            for label, value in pattern_parts:
                if value:
                    frame = ctk.CTkFrame(self.pattern_frame, fg_color="transparent")
                    frame.pack(fill="x", pady=2)
                    
                    ctk.CTkLabel(
                        frame,
                        text=f"{label}:",
                        font=("Arial", 11, "bold"),
                        width=100,
                        anchor="w"
                    ).pack(side="left")
                    
                    ctk.CTkLabel(
                        frame,
                        text=str(value),
                        anchor="w"
                    ).pack(side="left", fill="x", expand=True)
    
    def _clear_naming(self):
        """Clear naming information"""
        self.current_name_label.configure(text="")
        self.suggested_name_label.configure(text="")
        
        for widget in self.pattern_frame.winfo_children():
            widget.destroy()