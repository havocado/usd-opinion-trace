#!/usr/bin/env python3
"""USD Opinion Trace GUI - PySide6 interface for tracing USD attribute opinions."""

import json
import sys
import os

# Add src to path so we can import opinion_trace
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QCheckBox, QSpinBox,
    QFileDialog, QGroupBox, QFormLayout, QMessageBox, QComboBox,
    QCompleter, QTabWidget, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor, QPalette


def apply_dark_theme(app: QApplication):
    """Apply a dark color theme to the application."""
    app.setStyle("Fusion")
    
    dark_palette = QPalette()
    
    # Base colors
    dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Base, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.AlternateBase, QColor(55, 55, 55))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ToolTipText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Text, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.Button, QColor(55, 55, 55))
    dark_palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Link, QColor(100, 149, 237))
    dark_palette.setColor(QPalette.Highlight, QColor(70, 130, 180))
    dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    # Disabled colors
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
    
    app.setPalette(dark_palette)
    
    # Additional stylesheet for finer control
    app.setStyleSheet("""
        QGroupBox {
            border: 1px solid #555;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #ddd;
        }
        QLineEdit, QComboBox, QSpinBox, QTextEdit {
            background-color: #3a3a3a;
            border: 1px solid #555;
            border-radius: 3px;
            padding: 4px;
            color: #ddd;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
            border: 1px solid #6495ED;
        }
        QPushButton {
            background-color: #4a4a4a;
            border: 1px solid #555;
            border-radius: 4px;
            padding: 6px 12px;
            color: #ddd;
        }
        QPushButton:hover {
            background-color: #5a5a5a;
            border: 1px solid #6495ED;
        }
        QPushButton:pressed {
            background-color: #3a3a3a;
        }
        QTabWidget::pane {
            border: 1px solid #555;
            border-radius: 3px;
        }
        QTabBar::tab {
            background-color: #3a3a3a;
            border: 1px solid #555;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
            color: #bbb;
        }
        QTabBar::tab:selected {
            background-color: #4a4a4a;
            color: #fff;
        }
        QTabBar::tab:hover:!selected {
            background-color: #454545;
        }
        QSplitter::handle {
            background-color: #555;
        }
        QCheckBox {
            color: #ddd;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #555;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #666;
        }
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #555;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            height: 0;
            width: 0;
        }
    """)


def apply_light_theme(app: QApplication):
    """Apply a light color theme to the application."""
    app.setStyle("Fusion")
    
    light_palette = QPalette()
    
    # Base colors
    light_palette.setColor(QPalette.Window, QColor(240, 240, 240))
    light_palette.setColor(QPalette.WindowText, QColor(30, 30, 30))
    light_palette.setColor(QPalette.Base, QColor(255, 255, 255))
    light_palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    light_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    light_palette.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
    light_palette.setColor(QPalette.Text, QColor(30, 30, 30))
    light_palette.setColor(QPalette.Button, QColor(240, 240, 240))
    light_palette.setColor(QPalette.ButtonText, QColor(30, 30, 30))
    light_palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
    light_palette.setColor(QPalette.Link, QColor(0, 100, 200))
    light_palette.setColor(QPalette.Highlight, QColor(70, 130, 180))
    light_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    # Disabled colors
    light_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(150, 150, 150))
    light_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(150, 150, 150))
    light_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(150, 150, 150))
    
    app.setPalette(light_palette)
    
    # Additional stylesheet for finer control
    app.setStyleSheet("""
        QGroupBox {
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: #333;
        }
        QLineEdit, QComboBox, QSpinBox, QTextEdit {
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 3px;
            padding: 4px;
            color: #333;
        }
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {
            border: 1px solid #4a90d9;
        }
        QPushButton {
            background-color: #e8e8e8;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 6px 12px;
            color: #333;
        }
        QPushButton:hover {
            background-color: #d8d8d8;
            border: 1px solid #4a90d9;
        }
        QPushButton:pressed {
            background-color: #c8c8c8;
        }
        QTabWidget::pane {
            border: 1px solid #ccc;
            border-radius: 3px;
        }
        QTabBar::tab {
            background-color: #e8e8e8;
            border: 1px solid #ccc;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 6px 12px;
            color: #555;
        }
        QTabBar::tab:selected {
            background-color: #fff;
            color: #333;
        }
        QTabBar::tab:hover:!selected {
            background-color: #f0f0f0;
        }
        QSplitter::handle {
            background-color: #ccc;
        }
        QCheckBox {
            color: #333;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
        }
        QScrollBar:vertical {
            background-color: #f0f0f0;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #c0c0c0;
            border-radius: 6px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background-color: #a0a0a0;
        }
        QScrollBar:horizontal {
            background-color: #f0f0f0;
            height: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal {
            background-color: #c0c0c0;
            border-radius: 6px;
            min-width: 20px;
        }
        QScrollBar::add-line, QScrollBar::sub-line {
            height: 0;
            width: 0;
        }
    """)


# Theme color definitions for HTML content
DARK_THEME_COLORS = {
    'bg_header': '#3a3a3a',
    'bg_winning': '#1a3d1a',
    'bg_user_blocked': '#4a3a1a',
    'text': '#dcdcdc',
    'text_muted': '#888',
    'status_win': '#4ade80',
    'status_warn': '#fbbf24',
    'code_bg': '#2d2d2d',
    'warning_header': '#fbbf24',
    'arc_type': '#60a5fa',
    'blocked_path': '#9ca3af',
    'is_for_desc': '#4ade80',
    'condition': '#d1d5db',
    'arrow': '#22d3ee',
    'action': '#93c5fd',
    'emphasis': '#c4b5fd',
    'bg_accent': '#3a3a3a',
    'hr_color': '#555',
}

LIGHT_THEME_COLORS = {
    'bg_header': '#f0f0f0',
    'bg_winning': '#d4edda',
    'bg_user_blocked': '#fff3cd',
    'text': '#1e1e1e',
    'text_muted': '#666',
    'status_win': '#28a745',
    'status_warn': '#d97706',
    'code_bg': '#f5f5f5',
    'warning_header': '#b45309',
    'arc_type': '#0369a1',
    'blocked_path': '#6b7280',
    'is_for_desc': '#15803d',
    'condition': '#374151',
    'arrow': '#0891b2',
    'action': '#1e40af',
    'emphasis': '#7c3aed',
    'bg_accent': '#f3f4f6',
    'hr_color': '#ccc',
}

from opinion_trace.extraction import extract_opinions
from opinion_trace.diagnosis import diagnose
from opinion_trace.helpful_texts import HELPFUL_TEXTS


class StageLoaderThread(QThread):
    """Background thread to load prims and attributes from a USD stage."""
    finished = Signal(list, dict)  # prims list, prim->attrs dict
    error = Signal(str)
    
    def __init__(self, stage_path: str, max_prims: int = 5000):
        super().__init__()
        self.stage_path = stage_path
        self.max_prims = max_prims
    
    def run(self):
        try:
            from pxr import Usd
            stage = Usd.Stage.Open(self.stage_path)
            if not stage:
                self.error.emit(f"Failed to open stage: {self.stage_path}")
                return
            
            prims = []
            prim_attrs = {}  # prim_path -> list of attribute names
            
            for prim in stage.Traverse():
                if len(prims) >= self.max_prims:
                    break
                prim_path = str(prim.GetPath())
                prims.append(prim_path)
                
                # Collect attributes for this prim
                attrs = [attr.GetName() for attr in prim.GetAttributes()]
                if attrs:
                    prim_attrs[prim_path] = sorted(attrs)
            
            self.finished.emit(sorted(prims), prim_attrs)
            
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window for USD Opinion Trace."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("USD Opinion Trace by havocado")
        self.setMinimumSize(1200, 700)
        
        # Theme state
        self.dark_mode = True
        self._app = QApplication.instance()
        
        # Cache for prim->attributes mapping
        self.prim_attrs_cache = {}
        self.loader_thread = None
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # =====================================================================
        # LEFT COLUMN: Input, Run Button, Opinion Stack, JSON
        # =====================================================================
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # Input section
        input_group = QGroupBox("Query Parameters")
        input_form = QFormLayout(input_group)
        input_form.setSpacing(8)
        
        # Stage file picker (auto-loads on Enter or focus loss)
        stage_row = QHBoxLayout()
        self.stage_input = QLineEdit()
        self.stage_input.setPlaceholderText("/path/to/stage.usd")
        self.stage_input.editingFinished.connect(self.on_stage_editing_finished)
        self._last_loaded_stage = ""  # Track to avoid duplicate loads
        stage_browse = QPushButton("Browse...")
        stage_browse.setFixedWidth(80)
        stage_browse.clicked.connect(self.browse_stage)
        stage_row.addWidget(self.stage_input)
        stage_row.addWidget(stage_browse)
        input_form.addRow("Stage File:", stage_row)
        
        # Prim path input - editable combobox
        self.prim_path_input = QComboBox()
        self.prim_path_input.setEditable(True)
        self.prim_path_input.setInsertPolicy(QComboBox.NoInsert)
        self.prim_path_input.lineEdit().setPlaceholderText("/World/Chair")
        self.prim_path_input.setMaxVisibleItems(15)
        # Use the combobox's built-in completer (avoids dual-popup conflicts)
        self.prim_completer = self.prim_path_input.completer()
        self.prim_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.prim_completer.setFilterMode(Qt.MatchContains)
        self.prim_completer.setCompletionMode(QCompleter.PopupCompletion)
        # Update attributes when prim selection changes
        self.prim_path_input.currentTextChanged.connect(self.on_prim_changed)
        input_form.addRow("Prim Path:", self.prim_path_input)
        
        # Attribute input - editable combobox
        self.attribute_input = QComboBox()
        self.attribute_input.setEditable(True)
        self.attribute_input.setInsertPolicy(QComboBox.NoInsert)
        self.attribute_input.lineEdit().setPlaceholderText("xformOp:translate")
        self.attribute_input.setMaxVisibleItems(15)
        # Use the combobox's built-in completer (avoids dual-popup conflicts)
        self.attr_completer = self.attribute_input.completer()
        self.attr_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.attr_completer.setFilterMode(Qt.MatchContains)
        self.attr_completer.setCompletionMode(QCompleter.PopupCompletion)
        input_form.addRow("Attribute:", self.attribute_input)
        
        # Layer file picker
        layer_row = QHBoxLayout()
        self.layer_input = QLineEdit()
        self.layer_input.setPlaceholderText("my_edits.usd (identifier or basename)")
        layer_browse = QPushButton("Browse...")
        layer_browse.setFixedWidth(80)
        layer_browse.clicked.connect(self.browse_layer)
        layer_row.addWidget(self.layer_input)
        layer_row.addWidget(layer_browse)
        input_form.addRow("User Layer:", layer_row)
        
        # Time input (optional)
        time_row = QHBoxLayout()
        self.time_checkbox = QCheckBox("Use time code:")
        self.time_checkbox.toggled.connect(self.time_spinbox_set_enabled)
        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(-10000, 100000)
        self.time_spinbox.setValue(1)
        self.time_spinbox.setEnabled(False)
        time_row.addWidget(self.time_checkbox)
        time_row.addWidget(self.time_spinbox)
        time_row.addStretch()
        input_form.addRow("Time:", time_row)
        
        # Stack-only checkbox
        self.stack_only_checkbox = QCheckBox("Stack only (no diagnosis)")
        input_form.addRow("Options:", self.stack_only_checkbox)
        
        left_layout.addWidget(input_group)
        
        # Run button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.run_button = QPushButton("Run Trace")
        self.run_button.setFixedSize(120, 35)
        self.run_button.clicked.connect(self.run_trace)
        button_layout.addWidget(self.run_button)
        button_layout.addStretch()
        left_layout.addLayout(button_layout)
        
        # Opinion Stack results
        stack_group = QGroupBox("Opinion Stack")
        stack_layout = QVBoxLayout(stack_group)
        
        self.stack_display = QTextEdit()
        self.stack_display.setReadOnly(True)
        self.stack_display.setFont(QFont("Sans Serif", 10))
        self.stack_display.setPlaceholderText("Opinion stack will appear here...")
        stack_layout.addWidget(self.stack_display)
        
        # Copy stack button
        copy_stack_layout = QHBoxLayout()
        copy_stack_layout.addStretch()
        copy_stack_button = QPushButton("Copy Stack")
        copy_stack_button.clicked.connect(lambda: self.copy_to_clipboard(self.stack_display))
        copy_stack_layout.addWidget(copy_stack_button)
        stack_layout.addLayout(copy_stack_layout)
        
        left_layout.addWidget(stack_group, stretch=1)
        
        # =====================================================================
        # RIGHT COLUMN: Diagnosis and JSON Details in tabs
        # =====================================================================
        right_group = QGroupBox("Analysis")
        right_layout = QVBoxLayout(right_group)
        
        # Tab widget for Diagnosis and JSON
        self.right_tabs = QTabWidget()
        
        # Diagnosis tab
        diagnosis_widget = QWidget()
        diagnosis_layout = QVBoxLayout(diagnosis_widget)
        diagnosis_layout.setContentsMargins(0, 0, 0, 0)
        
        self.diagnosis_display = QTextEdit()
        self.diagnosis_display.setReadOnly(True)
        self.diagnosis_display.setFont(QFont("Sans Serif", 10))
        self.diagnosis_display.setPlaceholderText("Diagnosis will appear here...\n\nSpecify a User Layer and run the trace to see diagnosis.")
        diagnosis_layout.addWidget(self.diagnosis_display)
        
        # Copy diagnosis button
        copy_diag_layout = QHBoxLayout()
        copy_diag_layout.addStretch()
        copy_diag_button = QPushButton("Copy Diagnosis")
        copy_diag_button.clicked.connect(lambda: self.copy_to_clipboard(self.diagnosis_display))
        copy_diag_layout.addWidget(copy_diag_button)
        diagnosis_layout.addLayout(copy_diag_layout)
        
        self.right_tabs.addTab(diagnosis_widget, "Diagnosis")
        
        # JSON Details tab
        json_widget = QWidget()
        json_layout = QVBoxLayout(json_widget)
        json_layout.setContentsMargins(0, 0, 0, 0)
        
        self.json_display = QTextEdit()
        self.json_display.setReadOnly(True)
        self.json_display.setFont(QFont("monospace", 9))
        self.json_display.setPlaceholderText("JSON results will appear here...")
        json_layout.addWidget(self.json_display)
        
        # Copy JSON button
        copy_json_layout = QHBoxLayout()
        copy_json_layout.addStretch()
        copy_json_button = QPushButton("Copy JSON")
        copy_json_button.clicked.connect(lambda: self.copy_to_clipboard(self.json_display))
        copy_json_layout.addWidget(copy_json_button)
        json_layout.addLayout(copy_json_layout)
        
        self.right_tabs.addTab(json_widget, "JSON Details")
        
        right_layout.addWidget(self.right_tabs)
        
        # =====================================================================
        # Add columns to main layout with splitter
        # =====================================================================
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_column)
        splitter.addWidget(right_group)
        splitter.setSizes([600, 600])
        
        # Main vertical layout to hold splitter and bottom bar
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(splitter, stretch=1)
        
        # Bottom bar with dark mode toggle
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()
        self.dark_mode_button = QPushButton("Light Mode")
        self.dark_mode_button.setFixedWidth(120)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)
        bottom_bar.addWidget(self.dark_mode_button)
        content_layout.addLayout(bottom_bar)
        
        main_layout.addLayout(content_layout)
    
    def browse_stage(self):
        """Open file dialog to select USD stage file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select USD Stage",
            "",
            "USD Files (*.usd *.usda *.usdc *.usdz);;All Files (*)"
        )
        if file_path:
            self.stage_input.setText(file_path)
            # Auto-load stage contents after selecting
            self.load_stage_contents()
    
    def on_stage_editing_finished(self):
        """Auto-load stage when user finishes editing (Enter or focus loss)."""
        stage_path = self.stage_input.text().strip()
        # Only load if path changed and is non-empty
        if stage_path and stage_path != self._last_loaded_stage:
            self.load_stage_contents()
    
    def load_stage_contents(self):
        """Load prims and attributes from the stage in background."""
        stage_path = self.stage_input.text().strip()
        if not stage_path:
            return
        
        if not os.path.exists(stage_path):
            QMessageBox.warning(self, "Error", f"Stage file not found: {stage_path}")
            return
        
        self._last_loaded_stage = stage_path
        
        # Clear existing data
        self.prim_path_input.clear()
        self.attribute_input.clear()
        self.prim_attrs_cache.clear()
        
        # Update UI to show loading state
        self.prim_path_input.lineEdit().setPlaceholderText("Loading prims...")
        
        # Start background loading
        self.loader_thread = StageLoaderThread(stage_path)
        self.loader_thread.finished.connect(self.on_stage_loaded)
        self.loader_thread.error.connect(self.on_stage_load_error)
        self.loader_thread.start()
    
    def on_stage_loaded(self, prims: list, prim_attrs: dict):
        """Handle successful stage loading."""
        self.prim_attrs_cache = prim_attrs
        
        # Populate prim combobox
        self.prim_path_input.addItems(prims)
        
        # Reset placeholder
        self.prim_path_input.lineEdit().setPlaceholderText("/World/Chair")
        self.prim_path_input.setCurrentIndex(-1)  # Clear selection
        self.prim_path_input.lineEdit().clear()
        
        # Show count in status
        count_msg = f"Loaded {len(prims)} prims"
        if len(prims) >= 5000:
            count_msg += " (truncated)"
        self.stack_display.setPlainText(count_msg)
    
    def on_stage_load_error(self, error_msg: str):
        """Handle stage loading error."""
        self._last_loaded_stage = ""  # Allow retry
        self.prim_path_input.lineEdit().setPlaceholderText("/World/Chair")
        QMessageBox.warning(self, "Load Error", f"Failed to load stage:\n{error_msg}")
    
    def on_prim_changed(self, prim_path: str):
        """Update attribute dropdown when prim selection changes."""
        self.attribute_input.clear()
        
        if prim_path in self.prim_attrs_cache:
            attrs = self.prim_attrs_cache[prim_path]
            self.attribute_input.addItems(attrs)
            self.attribute_input.setCurrentIndex(-1)
            self.attribute_input.lineEdit().clear()
    
    def browse_layer(self):
        """Open file dialog to select USD layer file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select USD Layer",
            "",
            "USD Files (*.usd *.usda *.usdc *.usdz);;All Files (*)"
        )
        if file_path:
            self.layer_input.setText(file_path)
    
    def time_spinbox_set_enabled(self, checked: bool):
        """Enable/disable time spinbox based on checkbox state."""
        self.time_spinbox.setEnabled(checked)
    
    def validate_inputs(self) -> tuple[bool, str]:
        """Validate required inputs."""
        if not self.stage_input.text().strip():
            return False, "Stage file is required"
        if not self.prim_path_input.currentText().strip():
            return False, "Prim path is required"
        if not self.attribute_input.currentText().strip():
            return False, "Attribute name is required"
        if not self.stack_only_checkbox.isChecked() and not self.layer_input.text().strip():
            return False, "User layer is required (or enable 'Stack only')"
        return True, ""
    
    def run_trace(self):
        """Execute the opinion trace and display results."""
        # Validate inputs
        valid, error_msg = self.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        # Gather inputs
        stage_path = self.stage_input.text().strip()
        prim_path = self.prim_path_input.currentText().strip()
        attribute = self.attribute_input.currentText().strip()
        user_layer = self.layer_input.text().strip() if not self.stack_only_checkbox.isChecked() else None
        time_code = self.time_spinbox.value() if self.time_checkbox.isChecked() else None
        stack_only = self.stack_only_checkbox.isChecked()
        
        self.stack_display.clear()
        self.diagnosis_display.clear()
        self.json_display.clear()
        self.stack_display.setPlainText("Running trace...")
        QApplication.processEvents()
        
        try:
            # Phase 1: Extract
            extraction = extract_opinions(stage_path, prim_path, attribute, time_code)
            
            if extraction.error:
                result = {"error": extraction.error}
                self.stack_display.setPlainText(f"Error: {extraction.error}")
            else:
                # Phase 2: Diagnose (unless stack-only)
                diagnosis_result = None
                if not stack_only and user_layer:
                    diagnosis_result = diagnose(extraction, user_layer)
                
                # Phase 3: Build output
                result = self.build_output(extraction, diagnosis_result, user_layer)
                
                # Display opinion stack (left column)
                stack_text = self.build_stack_html(extraction, user_layer, diagnosis_result)
                self.stack_display.setHtml(stack_text)
                
                # Display diagnosis (right column)
                diagnosis_text = self.build_diagnosis_html(extraction, diagnosis_result, user_layer)
                self.diagnosis_display.setHtml(diagnosis_text)
            
            # Display JSON result
            output_json = json.dumps(result, indent=2, default=str)
            self.json_display.setPlainText(output_json)
            
        except Exception as e:
            error_result = {
                "error": {
                    "code": "UNEXPECTED_ERROR",
                    "message": str(e)
                }
            }
            self.stack_display.setPlainText(f"Unexpected Error: {str(e)}")
            self.json_display.setPlainText(json.dumps(error_result, indent=2))
    
    def build_stack_html(self, extraction, user_layer: str | None, diagnosis=None) -> str:
        """Build HTML for the Opinion Stack panel (left column)."""
        lines = []
        
        # Get current theme colors
        c = self.get_theme_colors()
        COLOR_BG_HEADER = c['bg_header']
        COLOR_BG_WINNING = c['bg_winning']
        COLOR_BG_USER_BLOCKED = c['bg_user_blocked']
        COLOR_TEXT = c['text']
        COLOR_TEXT_MUTED = c['text_muted']
        COLOR_STATUS_WIN = c['status_win']
        COLOR_STATUS_WARN = c['status_warn']
        COLOR_CODE_BG = c['code_bg']
        COLOR_HR = c['hr_color']
        
        # Opinion stack table
        if not extraction.opinions:
            lines.append(f"<p style='color: {COLOR_TEXT};'><i>No opinions found for this attribute.</i></p>")
        else:
            lines.append("<table style='border-collapse: collapse; width: 100%;'>")
            lines.append(f"<tr style='background-color: {COLOR_BG_HEADER};'>"
                         f"<th style='padding: 6px; text-align: left; color: {COLOR_TEXT};'>#</th>"
                         f"<th style='padding: 6px; text-align: left; color: {COLOR_TEXT};'>Layer</th>"
                         f"<th style='padding: 6px; text-align: left; color: {COLOR_TEXT};'>Arc</th>"
                         f"<th style='padding: 6px; text-align: left; color: {COLOR_TEXT};'>Value</th>"
                         f"<th style='padding: 6px; text-align: left; color: {COLOR_TEXT};'>Status</th>"
                         "</tr>")
            
            for o in extraction.opinions:
                # Determine row styling
                is_user = user_layer and user_layer in (o.layer_identifier, o.layer_name)
                if o.index == 0:
                    row_style = f"background-color: {COLOR_BG_WINNING};"
                    status = "✓ WINNING"
                    status_color = COLOR_STATUS_WIN
                elif is_user:
                    row_style = f"background-color: {COLOR_BG_USER_BLOCKED};"
                    status = "⚠ BLOCKED"
                    status_color = COLOR_STATUS_WARN
                else:
                    row_style = ""
                    status = "blocked"
                    status_color = COLOR_TEXT_MUTED
                
                # Truncate value for display
                val_str = str(o.value)
                if len(val_str) > 40:
                    val_str = val_str[:40] + "..."
                
                # Layer name with user indicator
                layer_display = o.layer_name
                if is_user:
                    layer_display += " <b>(your layer)</b>"
                
                # Blocked indicator
                if o.is_blocked:
                    val_str = "<i>BLOCKED</i>"
                
                lines.append(f"<tr style='{row_style}'>"
                             f"<td style='padding: 6px; color: {COLOR_TEXT};'>{o.index}</td>"
                             f"<td style='padding: 6px; color: {COLOR_TEXT};'>{layer_display}</td>"
                             f"<td style='padding: 6px; color: {COLOR_TEXT};'>{o.arc_type or 'direct'}</td>"
                             f"<td style='padding: 6px;'><code style='background-color: {COLOR_CODE_BG}; padding: 2px 4px; border-radius: 3px; color: {COLOR_TEXT};'>{val_str}</code></td>"
                             f"<td style='padding: 6px; color: {status_color};'>{status}</td>"
                             "</tr>")
            
            lines.append("</table>")
        
        lines.append(f"<hr style='border-color: {COLOR_HR};'>")
        
        # Header section (moved to bottom)
        lines.append(f"<h4 style='color: {COLOR_TEXT};'>Opinion Trace for <code style='background-color: {COLOR_CODE_BG}; padding: 2px 4px; border-radius: 3px; color: {COLOR_TEXT};'>{extraction.attr_name}</code></h4>")
        lines.append(f"<p style='color: {COLOR_TEXT};'><b>Prim:</b> <code style='background-color: {COLOR_CODE_BG}; padding: 2px 4px; border-radius: 3px;'>{extraction.prim_path}</code></p>")
        
        # Resolved value
        value_str = str(extraction.resolved_value)
        if len(value_str) > 100:
            value_str = value_str[:100] + "..."
        lines.append(f"<p style='color: {COLOR_TEXT};'><b>Resolved Value:</b> <code style='background-color: {COLOR_CODE_BG}; padding: 2px 4px; border-radius: 3px;'>{value_str}</code> "
                     f"<span style='color: {COLOR_TEXT_MUTED};'>({extraction.resolved_value_type})</span></p>")
        
        # Time code if specified
        if extraction.time_code is not None:
            lines.append(f"<p style='color: {COLOR_TEXT};'><b>Time Code:</b> {extraction.time_code}</p>")
        
        return "".join(lines)
    
    def build_diagnosis_html(self, extraction, diagnosis, user_layer: str | None) -> str:
        """Build HTML for the Diagnosis panel (right column)."""
        # Get current theme colors
        c = self.get_theme_colors()
        COLOR_WARNING_HEADER = c['warning_header']
        COLOR_ARC_TYPE = c['arc_type']
        COLOR_BLOCKED_PATH = c['blocked_path']
        COLOR_IS_FOR_DESC = c['is_for_desc']
        COLOR_CONDITION = c['condition']
        COLOR_ARROW = c['arrow']
        COLOR_ACTION = c['action']
        COLOR_EMPHASIS = c['emphasis']
        COLOR_BG_ACCENT = c['bg_accent']
        COLOR_TEXT = c['text']
        COLOR_HR = c['hr_color']
        
        lines = []
        
        if not diagnosis:
            lines.append(f"<p style='color: {COLOR_TEXT};'><i>No diagnosis available.</i></p>")
            lines.append(f"<p style='color: {COLOR_BLOCKED_PATH};'>Enable diagnosis by specifying a User Layer "
                         "and unchecking 'Stack only'.</p>")
            return "".join(lines)
        
        # Get diagnosis as dict
        if hasattr(diagnosis, '__dict__'):
            d = diagnosis.__dict__
        else:
            d = diagnosis if isinstance(diagnosis, dict) else {}
        
        # User layer found status - main status indicator
        user_found = d.get('user_layer_found', False)
        blocker = d.get('blocker_layer')
        
        if user_found:
            if blocker:
                # User layer is blocked - use warning header color
                lines.append(f"<p style='color: {COLOR_WARNING_HEADER}; font-weight: bold; font-size: 14px;'>"
                             "⚠️ Your opinion is being blocked!</p>")
            else:
                # User layer is winning
                lines.append(f"<p style='color: {COLOR_IS_FOR_DESC}; font-weight: bold; font-size: 14px;'>"
                             "✓ Your opinion is winning</p>")
        else:
            lines.append(f"<p style='color: {COLOR_WARNING_HEADER};'>"
                         "ℹ️ User layer not found in opinion stack</p>")
        
        # Reason - use emphasis color for key terms
        reason = d.get('reason')
        if reason:
            reason_display = reason.replace("_", " ").title()
            lines.append(f"<p style='color: {COLOR_TEXT};'><b>Reason:</b> <span style='color: {COLOR_EMPHASIS};'>{reason_display}</span></p>")
        
        # Blocking layer info - use blocked path color
        if blocker:
            blocker_index = d.get('blocker_index', '?')
            lines.append(f"<p style='color: {COLOR_TEXT};'><b>Blocked by:</b> <code style='background-color: {COLOR_BG_ACCENT}; padding: 2px 4px; border-radius: 3px; color: {COLOR_BLOCKED_PATH};'>{blocker}</code> "
                         f"<span style='color: {COLOR_BLOCKED_PATH};'>(index {blocker_index})</span></p>")
        
        lines.append(f"<hr style='border-color: {COLOR_HR};'>")
        
        # Arc descriptions and detail (reason code content)
        reason = d.get('reason', '')
        if reason:
            from opinion_trace.reason_codes import get_arc_descriptions, get_scenarios, get_detail
            
            # Show arc descriptions (for arc type comparisons)
            arc_descs = get_arc_descriptions(reason)
            if arc_descs:
                for arc_name, desc in arc_descs.items():
                    lines.append(
                        f"<p><b style='color: {COLOR_ARC_TYPE};'>{arc_name.title()}</b> "
                        f"<span style='color: {COLOR_IS_FOR_DESC};'>is for: {desc}</span></p>"
                    )
            
            # Show detail text (for non-arc-type reasons like sublayer_order, layer_muted, etc.)
            detail = get_detail(reason)
            if detail and not arc_descs:  # Only show detail if no arc_descriptions
                lines.append(
                    f"<p style='color: {COLOR_CONDITION};'>{detail}</p>"
                )
            
            # Scenarios (new format)
            scenarios = get_scenarios(reason)
            if scenarios:
                for scenario in scenarios:
                    if isinstance(scenario, dict):
                        condition = scenario.get('condition', '')
                        action = scenario.get('action', '')
                        if condition and action:
                            lines.append(
                                f"<p><span style='color: {COLOR_CONDITION};'>If you want {condition}:</span><br/>"
                                f"&nbsp;&nbsp;<span style='color: {COLOR_ARROW}; font-weight: bold;'>→</span> "
                                f"<span style='color: {COLOR_ACTION};'>{action}</span></p>"
                            )
                    else:
                        # Fallback for old format (string)
                        lines.append(f"<li style='color: {COLOR_CONDITION};'>{scenario}</li>")
        
        # Suggestions (old format fallback)
        suggestions = d.get('suggestions', [])
        if suggestions and not reason:
            lines.append(f"<p style='color: {COLOR_TEXT};'><b style='color: {COLOR_EMPHASIS};'>Suggestions:</b></p>")
            lines.append("<ul style='color: {COLOR_TEXT};'>")
            for suggestion in suggestions:
                lines.append(f"<li style='color: {COLOR_ACTION};'>{suggestion}</li>")
            lines.append("</ul>")
        
        # LIVRPS order violation explanation
        if d.get('does_not_follow_livrps_order', False):
            livrps_info = HELPFUL_TEXTS.get('livrps_out_of_order', {})
            title = livrps_info.get('title', 'LIVRPS Order Information')
            text = livrps_info.get('text', '')
            if text:
                lines.append("<hr>")
                lines.append(f"<p><b style='color: {COLOR_WARNING_HEADER};'>⚠️ {title}</b></p>")
                # Convert newlines to <br> and handle paragraph breaks with consistent styling
                para_style = f"color: {COLOR_CONDITION}; font-size: 11px;"
                formatted_text = text.replace('\n\n', f'</p><p style="margin-top: 10px; {para_style}">').replace('\n', '<br>')
                lines.append(f"<p style='{para_style}'>{formatted_text}</p>")
        
        return "".join(lines)
    
    def build_output(self, extraction, diagnosis, user_layer: str | None) -> dict:
        """Build output dictionary from extraction and diagnosis results."""
        return {
            "query": {
                "stage": extraction.stage_path,
                "prim_path": extraction.prim_path,
                "attribute": extraction.attr_name,
                "user_layer": user_layer,
                "time": extraction.time_code,
            },
            "resolved_value": extraction.resolved_value,
            "resolved_value_type": extraction.resolved_value_type,
            "opinions": [
                {
                    "index": o.index,
                    "layer": o.layer_name,
                    "layer_identifier": o.layer_identifier,
                    "arc_type": o.arc_type,
                    "value": o.value,
                    "has_timesamples": o.has_timesamples,
                    "is_blocked": o.is_blocked,
                    "status": "winning" if o.index == 0 else "blocked",
                    "is_user_layer": user_layer and user_layer in (o.layer_identifier, o.layer_name),
                    "is_direct": o.is_direct,
                }
                for o in extraction.opinions
            ],
            "diagnosis": diagnosis.__dict__ if diagnosis else None,
            "error": extraction.error,
        }
    
    def copy_to_clipboard(self, text_edit: QTextEdit):
        """Copy text from a QTextEdit to clipboard."""
        text = text_edit.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
    
    def get_theme_colors(self) -> dict:
        """Get the current theme's color dictionary."""
        return DARK_THEME_COLORS if self.dark_mode else LIGHT_THEME_COLORS
    
    def toggle_dark_mode(self):
        """Toggle between dark and light mode."""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            apply_dark_theme(self._app)
            self.dark_mode_button.setText("Light Mode")
        else:
            apply_light_theme(self._app)
            self.dark_mode_button.setText("Dark Mode")
        
        # Re-render HTML content if there's existing content
        if self.stack_display.toPlainText() and "Running trace" not in self.stack_display.toPlainText():
            # Trigger a re-run if we have valid inputs
            try:
                valid, _ = self.validate_inputs()
                if valid:
                    self.run_trace()
            except:
                pass  # Ignore errors, just don't re-render


def main():
    """Main GUI entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("USD Opinion Trace")
    
    # Apply dark theme
    apply_dark_theme(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()