#!/usr/bin/env python3
"""
SuggestionWindow: A popup GUI component for displaying and approving AI metadata suggestions.

This window presents AI-suggested metadata changes in an easy-to-review format,
allowing users to accept or reject individual suggestions before applying them.
"""

import customtkinter as ctk
from typing import Dict, Optional, Any


class SuggestionWindow(ctk.CTkToplevel):
    """
    A popup window to display AI-generated metadata suggestions and get user approval.
    
    Features:
    - Side-by-side comparison of current vs. suggested values
    - Per-suggestion checkboxes (pre-checked)
    - Clear visual indication of which fields have changes
    - Modal dialog (blocks main window until closed)
    - Returns approved changes via approved_changes attribute
    """
    
    def __init__(self, parent, current_metadata: Dict[str, Any], suggested_metadata: Dict[str, Any]):
        """
        Initialize the suggestion window.
        
        Args:
            parent: Parent CTk window
            current_metadata: Current metadata values (dict with artist, title, album, etc.)
            suggested_metadata: AI-suggested values (dict with same keys)
        """
        super().__init__(parent)
        
        self.title("AI Metadata Suggestions")
        self.geometry("900x500")
        self.minsize(700, 300)
        
        self.current_metadata = current_metadata
        self.suggested_metadata = suggested_metadata
        self.approved_changes: Optional[Dict[str, Any]] = None
        self.checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content with scrollbar
        self.grid_rowconfigure(2, weight=0)  # Buttons
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
        self._populate_suggestions()
        
        # Make the window modal (blocks interaction with the main window)
        self.grab_set()
        self.focus()
    
    def _create_widgets(self):
        """Create the main UI components."""
        
        # === HEADER ===
        header_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="AI Metadata Suggestions",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        info_label = ctk.CTkLabel(
            header_frame,
            text="Review suggestions below. Checked items will be applied.",
            font=("Arial", 10),
            text_color="gray"
        )
        info_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=15, pady=(0, 10))
        
        # === SCROLLABLE FRAME FOR SUGGESTIONS ===
        # Create a frame with scrollbar for the suggestions
        scroll_frame = ctk.CTkFrame(self)
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        scroll_frame.grid_rowconfigure(0, weight=1)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas with scrollbar (to handle many suggestions)
        canvas = ctk.CTkCanvas(
            scroll_frame,
            bg=self._get_canvas_color(),
            highlightthickness=0
        )
        scrollbar = ctk.CTkScrollbar(scroll_frame, command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas, fg_color="transparent")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.scrollable_frame = scrollable_frame
        
        # === BUTTONS ===
        button_frame = ctk.CTkFrame(self)
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=15)
        button_frame.grid_columnconfigure(0, weight=1)
        
        action_button_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        action_button_frame.grid(row=0, column=1, sticky="e")
        
        apply_button = ctk.CTkButton(
            action_button_frame,
            text="Apply Changes",
            command=self._on_apply,
            fg_color="#2d9b6b",
            hover_color="#1d6b3b"
        )
        apply_button.pack(side="left", padx=5)
        
        cancel_button = ctk.CTkButton(
            action_button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="#555555",
            hover_color="#333333"
        )
        cancel_button.pack(side="left", padx=5)
    
    def _populate_suggestions(self):
        """Populate the window with suggestion rows."""
        
        row = 0
        
        # Define which fields to display and in what order
        # Only show valid ID3 metadata fields, skip AI-only fields like moods/confidence
        display_fields = ['artist', 'title', 'album', 'genre', 'date', 'tracknumber']
        
        for field in display_fields:
            suggested_value = self.suggested_metadata.get(field, "")
            current_value = str(self.current_metadata.get(field, ""))
            
            # Skip if no suggestion
            if not suggested_value:
                continue
            
            # For list fields like moods, join them
            if isinstance(suggested_value, list):
                suggested_display = ", ".join(str(v) for v in suggested_value)
            else:
                suggested_display = str(suggested_value)
            
            # Only show if there's a meaningful difference
            if suggested_display.lower() == current_value.lower():
                continue
            
            # Create a suggestion row
            self._create_suggestion_row(row, field, current_value, suggested_value, suggested_display)
            row += 1
        
        # Show a message if no suggestions
        if row == 0:
            no_suggestions_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No suggestions to display.",
                font=("Arial", 11),
                text_color="gray"
            )
            no_suggestions_label.grid(row=0, column=0, columnspan=4, pady=20, sticky="w")
    
    def _create_suggestion_row(
        self,
        row: int,
        field: str,
        current_value: str,
        suggested_value: Any,
        suggested_display: str
    ):
        """
        Create a single row for a suggestion.
        
        Layout:
        [Checkbox] [Field Name] [Current Value] [Suggested Value]
        """
        
        # Checkbox (pre-checked)
        checkbox = ctk.CTkCheckBox(
            self.scrollable_frame,
            text="",
            width=30
        )
        checkbox.select()  # Pre-check it
        checkbox.grid(row=row, column=0, padx=(0, 10), pady=8, sticky="w")
        self.checkboxes[field] = checkbox
        
        # Field name label
        field_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=f"{field.replace('_', ' ').title()}:",
            font=("Arial", 11, "bold"),
            width=100
        )
        field_label.grid(row=row, column=1, sticky="w", padx=5, pady=8)
        
        # Current value
        current_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=current_value if current_value else "(empty)",
            font=("Courier", 10),
            text_color="gray60",
            wraplength=250,
            justify="left"
        )
        current_label.grid(row=row, column=2, sticky="w", padx=10, pady=8)
        
        # Arrow or separator
        arrow_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="→",
            font=("Arial", 12),
            text_color="gray70"
        )
        arrow_label.grid(row=row, column=3, sticky="w", padx=10, pady=8)
        
        # Suggested value (highlighted)
        suggested_label = ctk.CTkLabel(
            self.scrollable_frame,
            text=suggested_display,
            font=("Courier", 10, "bold"),
            text_color="#00FF00" if self._get_appearance_mode() == "dark" else "#008000",
            wraplength=250,
            justify="left"
        )
        suggested_label.grid(row=row, column=4, sticky="w", padx=5, pady=8)
    
    def _on_apply(self):
        """
        Collect user-approved changes and close the window.
        """
        self.approved_changes = {}
        
        display_fields = ['artist', 'title', 'album', 'genre', 'date', 'tracknumber']
        
        for field in display_fields:
            if field in self.checkboxes:
                checkbox = self.checkboxes[field]
                # If checkbox is checked (get() returns 1 for checked, 0 for unchecked)
                if checkbox.get() == 1:
                    self.approved_changes[field] = self.suggested_metadata[field]
        
        self.destroy()
    
    @staticmethod
    def _get_canvas_color():
        """Get the appropriate canvas background color based on appearance mode."""
        try:
            mode = ctk.get_appearance_mode()
            return "#212121" if mode == "dark" else "#f0f0f0"
        except:
            return "#212121"
    
    @staticmethod
    def _get_appearance_mode():
        """Get the current appearance mode (dark or light)."""
        try:
            return ctk.get_appearance_mode()
        except:
            return "dark"
