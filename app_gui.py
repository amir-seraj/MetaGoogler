#!/usr/bin/env python3
"""
Song Metadata Fixer GUI - CustomTkinter Application
A modern, user-friendly graphical interface for fixing music metadata.

Features:
- Folder browser for music library selection
- Real-time file listing with audio format detection
- Multi-threaded operations to prevent UI freezing
- Progress bar and log window for user feedback
- Batch operations (validate, fix whitespace, embed cover art, etc.)
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from threading import Thread
from queue import Queue
from datetime import datetime
import os
import sys
from typing import Optional, Callable

# Add parent directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent))

from song_metadata_fixer_v2 import SongMetadataFixer, OperationResult
from config_manager import ConfigManager
from logger_setup import get_logger
from ai_manager import AIManager

logger = get_logger(__name__)


class MetadataFixerGUI:
    """Main GUI application for Song Metadata Fixer."""
    
    def __init__(self, root: ctk.CTk):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Song Metadata Fixer")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize config and fixer
        self.config = ConfigManager()
        self.fixer = SongMetadataFixer()
        self.ai_manager = AIManager()
        self.current_folder: Optional[Path] = None
        self.audio_files: list = []
        
        # Threading queue for thread-safe GUI updates
        self.update_queue: Queue = Queue()
        self.is_processing = False
        
        # Set appearance mode
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")
        
        # Build the GUI
        self._build_layout()
        self._start_queue_monitor()
    
    def _build_layout(self):
        """Build the main GUI layout."""
        # Configure grid weights for responsive layout
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # ===== TOP SECTION: Folder Selection =====
        top_frame = ctk.CTkFrame(self.root)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(top_frame, text="Music Folder:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, sticky="w", padx=5
        )
        
        self.folder_label = ctk.CTkLabel(
            top_frame, 
            text="No folder selected", 
            text_color="gray",
            font=("Arial", 11)
        )
        self.folder_label.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.browse_btn = ctk.CTkButton(
            top_frame,
            text="Browse Folder",
            command=self._on_browse_folder,
            width=120
        )
        self.browse_btn.grid(row=0, column=2, sticky="e", padx=5)
        
        # ===== MAIN CONTENT SECTION =====
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=0)
        
        # --- Left side: File list ---
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            left_frame, 
            text="Audio Files:", 
            font=("Arial", 12, "bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # File listbox with scrollbar
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        scrollbar = ctk.CTkScrollbar(list_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.file_listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            bg="#212121",
            fg="#ffffff",
            borderwidth=0,
            highlightthickness=0
        )
        self.file_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.configure(command=self.file_listbox.yview)
        
        # File info section
        info_frame = ctk.CTkFrame(left_frame)
        info_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        info_frame.grid_columnconfigure(1, weight=1)
        
        self.file_count_label = ctk.CTkLabel(
            info_frame,
            text="Files: 0",
            font=("Arial", 10),
            text_color="gray"
        )
        self.file_count_label.grid(row=0, column=0, sticky="w")
        
        # --- Right side: Controls ---
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.grid(row=0, column=1, sticky="n", padx=(5, 0))
        right_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            right_frame,
            text="Actions:",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))
        
        # Action buttons
        actions = [
            ("Validate Metadata", self._on_validate_all, "light blue"),
            ("Fix Whitespace", self._on_fix_whitespace_all, "light green"),
            ("Embed Cover Art", self._on_embed_cover_art_all, "light yellow"),
            ("Get AI Suggestions", self._on_ai_suggestions, "#FF9500"),  # Orange for AI
            ("View Metadata", self._on_view_metadata, "light gray"),
            ("Refresh List", self._on_refresh_files, "light gray"),
        ]
        
        self.action_buttons = {}
        for label, command, color in actions:
            btn = ctk.CTkButton(
                right_frame,
                text=label,
                command=command,
                width=150,
                height=40,
                font=("Arial", 10, "bold"),
                hover_color=self._darken_color(color)
            )
            btn.pack(pady=5)
            self.action_buttons[label] = btn
        
        # ===== PROGRESS SECTION =====
        progress_frame = ctk.CTkFrame(self.root)
        progress_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        progress_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            progress_frame,
            text="Progress:",
            font=("Arial", 11, "bold")
        ).grid(row=0, column=0, sticky="w")
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready",
            text_color="gray",
            font=("Arial", 10)
        )
        self.progress_label.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame, height=20)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.progress_bar.set(0)
        
        # ===== LOG SECTION =====
        log_label_frame = ctk.CTkFrame(self.root)
        log_label_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(10, 0))
        log_label_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            log_label_frame,
            text="Activity Log:",
            font=("Arial", 11, "bold")
        ).pack(side="left")
        
        clear_log_btn = ctk.CTkButton(
            log_label_frame,
            text="Clear Log",
            command=self._on_clear_log,
            width=80,
            height=25,
            font=("Arial", 9)
        )
        clear_log_btn.pack(side="right", padx=(10, 0))
        
        # Log text box with scrollbar
        log_frame = ctk.CTkFrame(self.root)
        log_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=(5, 10))
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        log_scrollbar = ctk.CTkScrollbar(log_frame)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.log_textbox = tk.Text(
            log_frame,
            height=6,
            yscrollcommand=log_scrollbar.set,
            font=("Courier", 9),
            bg="#212121",
            fg="#00ff00",
            borderwidth=0,
            highlightthickness=0,
            wrap=tk.WORD
        )
        self.log_textbox.grid(row=0, column=0, sticky="nsew")
        log_scrollbar.configure(command=self.log_textbox.yview)
        
        # Configure grid weight for log section
        self.root.grid_rowconfigure(4, weight=1)
        
        self._log("Application started. Select a music folder to begin.")
    
    def _on_browse_folder(self):
        """Handle folder browser button click."""
        folder = filedialog.askdirectory(title="Select Music Folder")
        if folder:
            self.current_folder = Path(folder)
            self.folder_label.configure(text=str(self.current_folder))
            self._on_refresh_files()
            self._log(f"Loaded folder: {self.current_folder}")
    
    def _on_refresh_files(self):
        """Refresh the file list from current folder."""
        if not self.current_folder:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        
        try:
            self.file_listbox.delete(0, tk.END)
            supported_formats = self.config.get_supported_formats()
            
            # Get all audio files
            self.audio_files = []
            for format_ext in supported_formats:
                self.audio_files.extend(self.current_folder.glob(f"*{format_ext}"))
            
            self.audio_files.sort()
            
            # Populate listbox
            for file in self.audio_files:
                self.file_listbox.insert(tk.END, file.name)
            
            self.file_count_label.configure(text=f"Files: {len(self.audio_files)}")
            self._log(f"Found {len(self.audio_files)} audio files in folder.")
        except Exception as e:
            self._log(f"Error refreshing files: {e}")
            messagebox.showerror("Error", f"Failed to refresh files: {e}")
    
    def _on_validate_all(self):
        """Validate metadata for all files."""
        if not self.audio_files:
            messagebox.showwarning("Warning", "No audio files found.")
            return
        
        self._run_threaded_task(
            self._validate_all_worker,
            "Validating metadata for all files..."
        )
    
    def _validate_all_worker(self, progress_callback: Callable, log_callback: Callable):
        """Worker thread for validating all files."""
        total = len(self.audio_files)
        valid_count = 0
        issues_found = 0
        
        for idx, file in enumerate(self.audio_files):
            if not self.is_processing:
                break
            
            try:
                result = self.fixer.view_metadata(str(file))
                if result.success:
                    # Count issues if any
                    if result.data.get("issues", 0) > 0:
                        issues_found += result.data["issues"]
                    valid_count += 1
                
                progress = (idx + 1) / total
                progress_callback(progress, f"Validated {idx + 1}/{total}")
                log_callback(f"✓ {file.name}")
            except Exception as e:
                log_callback(f"✗ {file.name}: {e}")
        
        summary = f"Validation complete: {valid_count}/{total} files validated, {issues_found} issues found."
        log_callback(summary)
        progress_callback(1.0, summary)
    
    def _on_fix_whitespace_all(self):
        """Fix whitespace for all files."""
        if not self.audio_files:
            messagebox.showwarning("Warning", "No audio files found.")
            return
        
        self._run_threaded_task(
            self._fix_whitespace_worker,
            "Fixing whitespace in metadata..."
        )
    
    def _fix_whitespace_worker(self, progress_callback: Callable, log_callback: Callable):
        """Worker thread for fixing whitespace."""
        total = len(self.audio_files)
        fixed_count = 0
        
        for idx, file in enumerate(self.audio_files):
            if not self.is_processing:
                break
            
            try:
                result = self.fixer.fix_metadata(str(file))
                if result.success:
                    fixed_count += 1
                    log_callback(f"✓ Fixed: {file.name}")
                else:
                    log_callback(f"→ {file.name}: {result.message}")
                
                progress = (idx + 1) / total
                progress_callback(progress, f"Fixed {idx + 1}/{total}")
            except Exception as e:
                log_callback(f"✗ {file.name}: {e}")
        
        summary = f"Whitespace fix complete: {fixed_count}/{total} files updated."
        log_callback(summary)
        progress_callback(1.0, summary)
    
    def _on_embed_cover_art_all(self):
        """Embed cover art for all files."""
        if not self.audio_files:
            messagebox.showwarning("Warning", "No audio files found.")
            return
        
        # Ask user: internet or local?
        dialog_result = messagebox.askyesnocancel(
            "Cover Art Source",
            "Download cover art from Internet?\n\n"
            "Yes: Fetch from internet (recommended)\n"
            "No: Use local image file\n"
            "Cancel: Cancel operation"
        )
        
        if dialog_result is None:
            return
        
        if dialog_result:
            # Internet source - automatic
            self._run_threaded_task(
                lambda prog, log: self._embed_cover_internet_worker(prog, log),
                "Downloading cover art from internet..."
            )
        else:
            # Local file source
            cover_path = filedialog.askopenfilename(
                title="Select Cover Image",
                filetypes=[("Image Files", "*.jpg *.jpeg *.png"), ("All Files", "*.*")]
            )
            
            if not cover_path:
                return
            
            self._run_threaded_task(
                lambda prog, log: self._embed_cover_local_worker(prog, log, cover_path),
                "Embedding cover art from local file..."
            )
    
    def _embed_cover_internet_worker(self, progress_callback: Callable, log_callback: Callable):
        """Worker thread for downloading and embedding cover art from internet."""
        total = len(self.audio_files)
        embedded_count = 0
        skipped_count = 0
        
        for idx, file in enumerate(self.audio_files):
            if not self.is_processing:
                break
            
            try:
                # Get metadata to find artist and title
                metadata_result = self.fixer.view_metadata(str(file))
                if not metadata_result.success:
                    log_callback(f"→ {file.name}: Could not read metadata")
                    skipped_count += 1
                    progress = (idx + 1) / total
                    progress_callback(progress, f"Processed {idx + 1}/{total}")
                    continue
                
                metadata = metadata_result.data
                artist = metadata.get('artist', 'Unknown')
                title = metadata.get('title', file.stem)
                
                log_callback(f"⟳ Fetching cover for: {artist} - {title}")
                
                # Download cover from internet
                cover_bytes = self.fixer.download_cover_art_from_internet(artist, title)
                
                if not cover_bytes:
                    log_callback(f"→ {file.name}: No cover found online")
                    skipped_count += 1
                    progress = (idx + 1) / total
                    progress_callback(progress, f"Processed {idx + 1}/{total}")
                    continue
                
                # Embed the downloaded cover
                result = self.fixer.embed_cover_art_bytes(str(file), cover_bytes)
                if result.success:
                    embedded_count += 1
                    log_callback(f"✓ Cover embedded: {file.name}")
                else:
                    log_callback(f"✗ {file.name}: {result.message}")
                
                progress = (idx + 1) / total
                progress_callback(progress, f"Embedded {idx + 1}/{total}")
                
            except Exception as e:
                log_callback(f"✗ {file.name}: {e}")
        
        summary = f"Internet cover embedding complete: {embedded_count} embedded, {skipped_count} skipped, {total - embedded_count - skipped_count} errors."
        log_callback(summary)
        progress_callback(1.0, summary)
    
    def _embed_cover_local_worker(self, progress_callback: Callable, log_callback: Callable, cover_path: str):
        """Worker thread for embedding cover art from local file."""
        total = len(self.audio_files)
        embedded_count = 0
        
        for idx, file in enumerate(self.audio_files):
            if not self.is_processing:
                break
            
            try:
                result = self.fixer.embed_cover_art(str(file), cover_path)
                if result.success:
                    embedded_count += 1
                    log_callback(f"✓ Cover embedded: {file.name}")
                else:
                    log_callback(f"→ {file.name}: {result.message}")
                
                progress = (idx + 1) / total
                progress_callback(progress, f"Embedded {idx + 1}/{total}")
            except Exception as e:
                log_callback(f"✗ {file.name}: {e}")
        
        summary = f"Cover art embedding complete: {embedded_count}/{total} files updated."
        log_callback(summary)
        progress_callback(1.0, summary)

    
    def _on_view_metadata(self):
        """View metadata for selected file."""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file from the list.")
            return
        
        file = self.audio_files[selection[0]]
        
        try:
            result = self.fixer.view_metadata(str(file))
            if result.success:
                # Format metadata for display
                metadata = result.data
                info = f"File: {file.name}\n\n"
                for key, value in metadata.items():
                    if key != "issues":
                        info += f"{key}: {value}\n"
                
                if "issues" in metadata and metadata["issues"] > 0:
                    info += f"\n⚠️ Issues found: {metadata['issues']}"
                
                messagebox.showinfo("Metadata", info)
                self._log(f"Viewed metadata: {file.name}")
            else:
                messagebox.showerror("Error", result.message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read metadata: {e}")
    
    def _on_ai_suggestions(self):
        """Get AI suggestions for selected file."""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file from the list.")
            return
        
        file = self.audio_files[selection[0]]
        
        # Check if Ollama is available
        try:
            import ollama
        except ImportError:
            messagebox.showerror(
                "Error",
                "Ollama is not installed.\n\nInstall with: pip install ollama\n\n"
                "Also make sure Ollama server is running:\n"
                "ollama serve"
            )
            return
        
        # Run in thread to avoid freezing
        self._run_threaded_task(
            lambda prog, log: self._ai_suggestions_worker(prog, log, file),
            "Getting AI suggestions..."
        )
    
    def _ai_suggestions_worker(self, progress_callback, log_callback, file):
        """Worker thread for getting AI suggestions."""
        try:
            # Get current metadata
            metadata = self.fixer.get_metadata(file)
            if metadata is None:
                log_callback(f"Could not read metadata: {file.name}")
                return
            
            progress_callback(0.3, "Analyzing with AI...")
            log_callback(f"Analyzing: {file.name}")
            
            # Get AI suggestions
            suggestions = self.ai_manager.get_ai_suggestions(file.name, metadata)
            
            if suggestions is None:
                log_callback("Error: Could not get suggestions from AI")
                progress_callback(1.0, "Error getting suggestions")
                return
            
            progress_callback(0.7, "Opening suggestions window...")
            
            # Open suggestion window on main thread
            def show_suggestions():
                try:
                    from suggestion_window import SuggestionWindow
                    window = SuggestionWindow(self.root, metadata, suggestions)
                    self.root.wait_window(window)
                    
                    if window.approved_changes:
                        # Apply approved changes
                        final_metadata = metadata.copy()
                        
                        # Filter to only valid ID3 tags supported by mutagen's EasyID3
                        # Valid ID3 fields: artist, title, album, date, genre, tracknumber, albumartist, etc.
                        # Invalid (non-standard) fields: moods, confidence, notes, version_info
                        valid_id3_fields = {
                            'artist', 'title', 'album', 'date', 'genre', 'tracknumber',
                            'albumartist', 'composer', 'comment', 'copyright', 'lyricist',
                            'original_date', 'performer'
                        }
                        
                        filtered_changes = {}
                        for k, v in window.approved_changes.items():
                            # Skip non-standard fields
                            if k not in valid_id3_fields or v is None:
                                continue
                            
                            # Convert lists to comma-separated strings
                            if isinstance(v, list):
                                filtered_changes[k] = ', '.join(str(item) for item in v if item)
                            else:
                                filtered_changes[k] = str(v)
                        
                        final_metadata.update(filtered_changes)
                        
                        try:
                            result = self.fixer.set_metadata(file, final_metadata)
                            if result and result.success:
                                log_callback(f"✓ Applied AI suggestions to: {file.name}")
                            else:
                                error_msg = result.message if (result and hasattr(result, 'message')) else "Unknown error"
                                log_callback(f"✗ Failed to apply suggestions: {error_msg}")
                                logger.error(f"AI metadata write failed: {file.name} - {error_msg}")
                        except Exception as write_error:
                            log_callback(f"✗ Error writing metadata: {str(write_error)}")
                            logger.exception(f"Exception while writing metadata for {file.name}")
                    else:
                        log_callback(f"Suggestions cancelled for: {file.name}")
                except ImportError as ie:
                    log_callback("Error: Could not import SuggestionWindow")
                    logger.error(f"ImportError in suggestions window: {ie}")
                except Exception as e:
                    log_callback(f"Error applying suggestions: {str(e)}")
                    logger.exception("Exception in suggestion application")
                finally:
                    progress_callback(1.0, "Ready")
            
            self.root.after(0, show_suggestions)
            
        except Exception as e:
            log_callback(f"Error: {str(e)}")
            logger.exception(f"Exception in AI suggestions worker")
            progress_callback(1.0, "Error")
    
    def _run_threaded_task(self, worker_func: Callable, initial_message: str):
        """Run a long task in a separate thread to keep GUI responsive."""
        if self.is_processing:
            messagebox.showinfo("Info", "A task is already running. Please wait.")
            return
        
        self.is_processing = True
        self._set_buttons_enabled(False)
        self._log(initial_message)
        
        def progress_callback(value: float, message: str):
            """Called from worker thread to update progress."""
            self.update_queue.put(("progress", value, message))
        
        def log_callback(message: str):
            """Called from worker thread to add log messages."""
            self.update_queue.put(("log", message))
        
        def thread_worker():
            try:
                worker_func(progress_callback, log_callback)
            except Exception as e:
                log_callback(f"Error: {e}")
                logger.exception("Task error")
            finally:
                self.update_queue.put(("done", None))
        
        thread = Thread(target=thread_worker, daemon=True)
        thread.start()
    
    def _start_queue_monitor(self):
        """Monitor the update queue for thread-safe GUI updates."""
        try:
            while True:
                try:
                    msg_type, *data = self.update_queue.get_nowait()
                    
                    if msg_type == "progress":
                        progress_value, message = data
                        self.progress_bar.set(progress_value)
                        self.progress_label.configure(text=message)
                    
                    elif msg_type == "log":
                        self._log(data[0])
                    
                    elif msg_type == "done":
                        self.is_processing = False
                        self._set_buttons_enabled(True)
                        self.progress_bar.set(0)
                        self.progress_label.configure(text="Ready")
                
                except:
                    break
        finally:
            # Continue monitoring
            self.root.after(100, self._start_queue_monitor)
    
    def _set_buttons_enabled(self, enabled: bool):
        """Enable or disable all action buttons."""
        state = "normal" if enabled else "disabled"
        for btn in self.action_buttons.values():
            btn.configure(state=state)
        self.browse_btn.configure(state=state)
    
    def _log(self, message: str):
        """Add a message to the log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_textbox.insert(tk.END, log_entry)
        self.log_textbox.see(tk.END)
        logger.info(message)
    
    def _on_clear_log(self):
        """Clear the log window."""
        self.log_textbox.delete(1.0, tk.END)
        self._log("Log cleared.")
    
    @staticmethod
    def _darken_color(color: str) -> str:
        """Create a darker shade of a color (for hover effects)."""
        # Simple approximation - return the same color for now
        return color


def main():
    """Main entry point for the GUI application."""
    root = ctk.CTk()
    app = MetadataFixerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
