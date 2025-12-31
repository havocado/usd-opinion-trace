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
    QCompleter, QTabWidget
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

from opinion_trace.extraction import extract_opinions
from opinion_trace.diagnosis import diagnose


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
        self.setWindowTitle("USD Opinion Trace")
        self.setMinimumSize(700, 650)
        
        # Cache for prim->attributes mapping
        self.prim_attrs_cache = {}
        self.loader_thread = None
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Input section
        input_group = QGroupBox("Query Parameters")
        input_layout = QFormLayout(input_group)
        input_layout.setSpacing(8)
        
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
        input_layout.addRow("Stage File:", stage_row)
        
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
        input_layout.addRow("Prim Path:", self.prim_path_input)
        
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
        input_layout.addRow("Attribute:", self.attribute_input)
        
        # Layer file picker
        layer_row = QHBoxLayout()
        self.layer_input = QLineEdit()
        self.layer_input.setPlaceholderText("my_edits.usd (identifier or basename)")
        layer_browse = QPushButton("Browse...")
        layer_browse.setFixedWidth(80)
        layer_browse.clicked.connect(self.browse_layer)
        layer_row.addWidget(self.layer_input)
        layer_row.addWidget(layer_browse)
        input_layout.addRow("User Layer:", layer_row)
        
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
        input_layout.addRow("Time:", time_row)
        
        # Stack-only checkbox
        self.stack_only_checkbox = QCheckBox("Stack only (no diagnosis)")
        input_layout.addRow("Options:", self.stack_only_checkbox)
        
        main_layout.addWidget(input_group)
        
        # Run button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.run_button = QPushButton("Run Trace")
        self.run_button.setFixedSize(120, 35)
        self.run_button.clicked.connect(self.run_trace)
        button_layout.addWidget(self.run_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Output section with tabs
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        
        # Create tab widget for Summary and JSON views
        self.output_tabs = QTabWidget()
        
        # Summary tab - human-friendly output
        self.summary_display = QTextEdit()
        self.summary_display.setReadOnly(True)
        self.summary_display.setFont(QFont("Sans Serif", 10))
        self.summary_display.setPlaceholderText("Human-friendly diagnosis will appear here...")
        self.output_tabs.addTab(self.summary_display, "Summary")
        
        # JSON tab - detailed output
        self.json_display = QTextEdit()
        self.json_display.setReadOnly(True)
        self.json_display.setFont(QFont("monospace", 10))
        self.json_display.setPlaceholderText("JSON results will appear here...")
        self.output_tabs.addTab(self.json_display, "JSON Details")
        
        output_layout.addWidget(self.output_tabs)
        
        # Copy button
        copy_layout = QHBoxLayout()
        copy_layout.addStretch()
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_output)
        copy_layout.addWidget(copy_button)
        output_layout.addLayout(copy_layout)
        
        main_layout.addWidget(output_group, stretch=1)
    
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
        self.summary_display.setPlainText(count_msg)
    
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
        
        self.summary_display.clear()
        self.json_display.clear()
        self.summary_display.setPlainText("Running trace...")
        QApplication.processEvents()
        
        try:
            # Phase 1: Extract
            extraction = extract_opinions(stage_path, prim_path, attribute, time_code)
            
            if extraction.error:
                result = {"error": extraction.error}
                self.summary_display.setPlainText(f"Error: {extraction.error}")
            else:
                # Phase 2: Diagnose (unless stack-only)
                diagnosis_result = None
                if not stack_only and user_layer:
                    diagnosis_result = diagnose(extraction, user_layer)
                
                # Phase 3: Build output
                result = self.build_output(extraction, diagnosis_result, user_layer)
                
                # Display human-friendly summary
                summary_text = self.build_human_summary(extraction, diagnosis_result, user_layer)
                self.summary_display.setHtml(summary_text)
            
            # Display JSON result
            output_json = json.dumps(result, indent=2, default=str)
            self.json_display.setPlainText(output_json)
            
            # Switch to Summary tab
            self.output_tabs.setCurrentIndex(0)
            
        except Exception as e:
            error_result = {
                "error": {
                    "code": "UNEXPECTED_ERROR",
                    "message": str(e)
                }
            }
            self.summary_display.setPlainText(f"Unexpected Error: {str(e)}")
            self.json_display.setPlainText(json.dumps(error_result, indent=2))
    
    def build_human_summary(self, extraction, diagnosis, user_layer: str | None) -> str:
        """Build human-friendly HTML summary from extraction and diagnosis results."""
        lines = []
        
        # Opinion stack first
        lines.append("<h4>Opinion Stack</h4>")
        if not extraction.opinions:
            lines.append("<p><i>No opinions found for this attribute.</i></p>")
        else:
            lines.append("<table style='border-collapse: collapse; width: 100%;'>")
            lines.append("<tr style='background-color: #f0f0f0;'>"
                         "<th style='padding: 6px; text-align: left;'>#</th>"
                         "<th style='padding: 6px; text-align: left;'>Layer</th>"
                         "<th style='padding: 6px; text-align: left;'>Arc</th>"
                         "<th style='padding: 6px; text-align: left;'>Value</th>"
                         "<th style='padding: 6px; text-align: left;'>Status</th>"
                         "</tr>")
            
            for o in extraction.opinions:
                # Determine row styling
                is_user = user_layer and user_layer in (o.layer_identifier, o.layer_name)
                if o.index == 0:
                    row_style = "background-color: #d4edda;"  # Green for winning
                    status = "✓ WINNING"
                    status_color = "green"
                elif is_user:
                    row_style = "background-color: #fff3cd;"  # Yellow for user layer
                    status = "⚠ BLOCKED"
                    status_color = "orange"
                else:
                    row_style = ""
                    status = "blocked"
                    status_color = "gray"
                
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
                             f"<td style='padding: 6px;'>{o.index}</td>"
                             f"<td style='padding: 6px;'>{layer_display}</td>"
                             f"<td style='padding: 6px;'>{o.arc_type or 'direct'}</td>"
                             f"<td style='padding: 6px;'><code>{val_str}</code></td>"
                             f"<td style='padding: 6px; color: {status_color};'>{status}</td>"
                             "</tr>")
            
            lines.append("</table>")
        
        lines.append("<hr>")
        
        # Header section
        lines.append(f"<h4>Opinion Trace for <code>{extraction.attr_name}</code></h4>")
        lines.append(f"<p><b>Prim:</b> <code>{extraction.prim_path}</code></p>")
        
        # Resolved value
        value_str = str(extraction.resolved_value)
        if len(value_str) > 100:
            value_str = value_str[:100] + "..."
        lines.append(f"<p><b>Resolved Value:</b> <code>{value_str}</code> "
                     f"<span style='color: gray;'>({extraction.resolved_value_type})</span></p>")
        
        # Time code if specified
        if extraction.time_code is not None:
            lines.append(f"<p><b>Time Code:</b> {extraction.time_code}</p>")
        
        # Diagnosis section
        if diagnosis:
            lines.append("<hr>")
            lines.append("<h4>Diagnosis</h4>")
            
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
                    # User layer is blocked
                    lines.append("<p style='color: #d9534f; font-weight: bold; font-size: 14px;'>"
                                 "⚠️ Your opinion is being blocked!</p>")
                else:
                    # User layer is winning
                    lines.append("<p style='color: #5cb85c; font-weight: bold; font-size: 14px;'>"
                                 "✓ Your opinion is winning</p>")
            else:
                lines.append("<p style='color: #f0ad4e;'>"
                             "ℹ️ User layer not found in opinion stack</p>")
            
            # Reason
            reason = d.get('reason')
            if reason:
                reason_display = reason.replace("_", " ").title()
                lines.append(f"<p><b>Reason:</b> {reason_display}</p>")
            
            # Reason detail
            reason_detail = d.get('reason_detail')
            if reason_detail:
                lines.append(f"<p style='color: #666;'>{reason_detail}</p>")
            
            # Blocking layer info
            if blocker:
                blocker_index = d.get('blocker_index', '?')
                lines.append(f"<p><b>Blocked by:</b> <code>{blocker}</code> "
                             f"(index {blocker_index})</p>")
            
            # Suggestions
            suggestions = d.get('suggestions', [])
            if suggestions:
                lines.append("<p><b>💡 Suggestions:</b></p>")
                lines.append("<ul>")
                for suggestion in suggestions:
                    lines.append(f"<li>{suggestion}</li>")
                lines.append("</ul>")
        
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
    
    def copy_output(self):
        """Copy output text from current tab to clipboard."""
        current_tab = self.output_tabs.currentIndex()
        if current_tab == 0:
            text = self.summary_display.toPlainText()
        else:
            text = self.json_display.toPlainText()
        
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)


def main():
    """Main GUI entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("USD Opinion Trace")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()