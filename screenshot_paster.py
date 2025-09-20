import sys
import os
import json
from datetime import datetime
from PIL import Image, ImageGrab
import pyperclip
import re
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QFrame, QGroupBox, QTreeWidget,
    QTreeWidgetItem, QFileDialog, QMessageBox, QDialog, QSpinBox, QScrollArea,
    QSizePolicy, QStyle
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QShortcut, QKeySequence, QAction

class ScreenshotPaster(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pic Q'er")
        self.setGeometry(100, 100, 900, 700)
        
        # Configuration
        self.save_directory = os.path.expanduser("~/Pictures/Screenshots")
        self.naming_pattern = "{date}_{time}_{counter}"
        self.pattern_elements = ["date", "time", "counter"]  # Track pattern as list
        self.custom_counters = {"counter": {"value": 1, "increment": 1}}  # Custom counters
        self.index_file = os.path.join(self.save_directory, "screenshot_index.json")
        
        # Ensure save directory exists
        os.makedirs(self.save_directory, exist_ok=True)
        
        # Load existing index
        self.load_index()
        
        self.setup_ui()
        self.bind_shortcuts()
        self.apply_native_styling()
        
    def setup_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Screenshot Utility for Windows")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Save Directory Section
        dir_group = QGroupBox("Save Directory")
        dir_layout = QHBoxLayout(dir_group)
        
        self.dir_entry = QLineEdit(self.save_directory)
        dir_layout.addWidget(self.dir_entry)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        
        main_layout.addWidget(dir_group)
        
        # Naming Pattern Section
        self.setup_pattern_section(main_layout)
        
        # Paste Area
        paste_group = QGroupBox("Paste Screenshot Here")
        paste_layout = QVBoxLayout(paste_group)
        
        self.paste_text = QTextEdit()
        self.paste_text.setMaximumHeight(150)
        self.paste_text.setPlainText("Paste your screenshot here and press Enter to save...")
        self.paste_text.keyPressEvent = self.paste_text_key_press
        self.paste_text.mousePressEvent = self.paste_text_mouse_press
        paste_layout.addWidget(self.paste_text)
        
        main_layout.addWidget(paste_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        paste_save_btn = QPushButton("Paste & Save")
        paste_save_btn.clicked.connect(self.paste_and_save)
        button_layout.addWidget(paste_save_btn)
        
        screenshot_btn = QPushButton("Take Screenshot")
        screenshot_btn.clicked.connect(self.take_screenshot)
        button_layout.addWidget(screenshot_btn)
        
        view_index_btn = QPushButton("View Index")
        view_index_btn.clicked.connect(self.view_index)
        button_layout.addWidget(view_index_btn)
        
        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.clicked.connect(self.open_folder)
        button_layout.addWidget(open_folder_btn)
        
        main_layout.addLayout(button_layout)
        
        # Status
        self.status_label = QLabel("Ready to paste screenshots")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Initialize pattern preview
        self.update_pattern_preview()
        
    def setup_pattern_section(self, main_layout):
        # Naming Pattern Section
        pattern_group = QGroupBox("Naming Pattern Builder")
        pattern_layout = QVBoxLayout(pattern_group)
        
        # Pattern preview
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(QLabel("Preview:"))
        self.pattern_preview = QLabel()
        self.pattern_preview.setStyleSheet("color: blue; font-weight: bold;")
        preview_layout.addWidget(self.pattern_preview)
        preview_layout.addStretch()
        pattern_layout.addLayout(preview_layout)
        
        # Current pattern display
        pattern_display_layout = QHBoxLayout()
        pattern_display_layout.addWidget(QLabel("Pattern:"))
        self.pattern_display = QLabel(self.naming_pattern)
        self.pattern_display.setStyleSheet("color: gray;")
        pattern_display_layout.addWidget(self.pattern_display)
        pattern_display_layout.addStretch()
        pattern_layout.addLayout(pattern_display_layout)
        
        # Variable buttons
        self.setup_pattern_builder(pattern_layout)
        
        main_layout.addWidget(pattern_group)
    
    def setup_pattern_builder(self, parent_layout):
        # Variable buttons section
        var_label = QLabel("Click to add variables:")
        parent_layout.addWidget(var_label)
        
        # Date/Time variables
        date_layout = QHBoxLayout()
        date_vars = [
            ("Date", "date", "YYYY-MM-DD"),
            ("Time", "time", "HH-MM-SS"), 
            ("Timestamp", "timestamp", "YYYY-MM-DD_HH-MM-SS"),
            ("Date Short", "date_short", "YYYYMMDD"),
            ("Time 12h", "time_12h", "HH-MM-SS AM/PM"),
            ("Year", "year", "YYYY")
        ]
        
        for label, var, desc in date_vars:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, v=var: self.add_pattern_element(v))
            date_layout.addWidget(btn)
        
        parent_layout.addLayout(date_layout)
        
        # Counter variables
        counter_label = QLabel("Counters:")
        parent_layout.addWidget(counter_label)
        
        counter_layout = QHBoxLayout()
        
        counter_btn = QPushButton("Counter")
        counter_btn.clicked.connect(lambda: self.add_pattern_element("counter"))
        counter_layout.addWidget(counter_btn)
        
        custom_counter_btn = QPushButton("+ Custom Counter")
        custom_counter_btn.clicked.connect(self.add_custom_counter)
        counter_layout.addWidget(custom_counter_btn)
        
        manage_counter_btn = QPushButton("Manage Counters")
        manage_counter_btn.clicked.connect(self.manage_counters)
        counter_layout.addWidget(manage_counter_btn)
        
        counter_layout.addStretch()
        parent_layout.addLayout(counter_layout)
        
        # Separators & Text
        sep_label = QLabel("Separators & Text:")
        parent_layout.addWidget(sep_label)
        
        separator_layout = QHBoxLayout()
        separators = [("_", "_"), ("-", "-"), (".", "."), (" ", "space"), ("Custom Text", "custom")]
        
        for text, sep in separators:
            btn = QPushButton(text)
            if sep == "custom":
                btn.clicked.connect(self.add_custom_text)
            else:
                btn.clicked.connect(lambda checked, s=sep: self.add_pattern_element(s))
            separator_layout.addWidget(btn)
        
        separator_layout.addStretch()
        parent_layout.addLayout(separator_layout)
        
        # Pattern control buttons
        control_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Pattern")
        clear_btn.clicked.connect(self.clear_pattern)
        control_layout.addWidget(clear_btn)
        
        reset_btn = QPushButton("Reset to Default")
        reset_btn.clicked.connect(self.reset_pattern)
        control_layout.addWidget(reset_btn)
        
        undo_btn = QPushButton("Undo Last")
        undo_btn.clicked.connect(self.undo_last_element)
        control_layout.addWidget(undo_btn)
        
        control_layout.addStretch()
        parent_layout.addLayout(control_layout)

    def bind_shortcuts(self):
        # Keyboard shortcuts
        paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        paste_shortcut.activated.connect(self.paste_and_save)
        
        screenshot_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        screenshot_shortcut.activated.connect(self.take_screenshot)
        
    def paste_text_key_press(self, event):
        # Handle Enter key in paste area
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.paste_and_save()
        else:
            # Call the original keyPressEvent
            QTextEdit.keyPressEvent(self.paste_text, event)
            
    def paste_text_mouse_press(self, event):
        # Clear placeholder text on click
        if self.paste_text.toPlainText().strip() == "Paste your screenshot here and press Enter to save...":
            self.paste_text.clear()
        # Call the original mousePressEvent
        QTextEdit.mousePressEvent(self.paste_text, event)
    
    # Pattern building methods
    def add_pattern_element(self, element):
        """Add an element to the pattern"""
        self.pattern_elements.append(element)
        self.update_pattern_from_elements()
        self.update_pattern_preview()
    
    def add_custom_counter(self):
        """Add a custom counter"""
        dialog = CustomCounterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, start_val, increment = dialog.get_values()
            if name in self.custom_counters:
                reply = QMessageBox.question(self, "Counter Exists", 
                                           f"Counter '{name}' already exists. Overwrite?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply != QMessageBox.StandardButton.Yes:
                    return
                    
            self.custom_counters[name] = {"value": start_val, "increment": increment}
            self.add_pattern_element(name)
    
    def add_custom_text(self):
        """Add custom text to pattern"""
        dialog = CustomTextDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            text = dialog.get_text()
            if text:
                self.add_pattern_element(text)
    
    def manage_counters(self):
        """Open counter management dialog"""
        dialog = CounterManagementDialog(self, self.custom_counters)
        dialog.exec()
    
    def clear_pattern(self):
        """Clear the current pattern"""
        self.pattern_elements = []
        self.update_pattern_from_elements()
        self.update_pattern_preview()
    
    def reset_pattern(self):
        """Reset to default pattern"""
        self.pattern_elements = ["date", "time", "counter"]
        self.update_pattern_from_elements()
        self.update_pattern_preview()
    
    def undo_last_element(self):
        """Remove the last added element"""
        if self.pattern_elements:
            self.pattern_elements.pop()
            self.update_pattern_from_elements()
            self.update_pattern_preview()
    
    def update_pattern_from_elements(self):
        """Update the naming pattern from elements list"""
        pattern_parts = []
        for element in self.pattern_elements:
            if element in ["date", "time", "timestamp", "date_short", "time_12h", "year"] or element in self.custom_counters:
                pattern_parts.append(f"{{{element}}}")
            elif element == "space":
                pattern_parts.append(" ")
            else:
                pattern_parts.append(element)
        
        self.naming_pattern = "".join(pattern_parts)
        self.pattern_display.setText(self.naming_pattern)
    
    def update_pattern_preview(self):
        """Update the pattern preview with current date/time"""
        try:
            preview = self.generate_filename_preview()
            self.pattern_preview.setText(preview)
        except Exception as e:
            self.pattern_preview.setText("Invalid pattern")
    
    def generate_filename_preview(self):
        """Generate a preview filename without incrementing counters"""
        pattern = self.naming_pattern
        
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        date_short_str = now.strftime("%Y%m%d")
        time_12h_str = now.strftime("%I-%M-%S %p")
        year_str = now.strftime("%Y")
        
        # Create format dict with all variables
        format_dict = {
            'date': date_str,
            'time': time_str,
            'timestamp': timestamp_str,
            'date_short': date_short_str,
            'time_12h': time_12h_str,
            'year': year_str
        }
        
        # Add custom counters
        for name, data in self.custom_counters.items():
            format_dict[name] = data['value']
        
        # Replace pattern variables
        try:
            filename = pattern.format(**format_dict)
        except KeyError as e:
            return f"Missing variable: {e}"
            
        # Ensure it has .png extension
        if filename and not filename.lower().endswith('.png'):
            filename += '.png'
            
        return filename
            
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", self.save_directory)
        if directory:
            self.save_directory = directory
            self.dir_entry.setText(directory)
            self.index_file = os.path.join(directory, "screenshot_index.json")
            self.load_index()
            
    def paste_and_save(self):
        try:
            # Get image from clipboard
            image = ImageGrab.grabclipboard()
            
            if image is None:
                # Try to get text from clipboard and check if it's a file path
                clipboard_text = pyperclip.paste()
                if os.path.isfile(clipboard_text):
                    image = Image.open(clipboard_text)
                else:
                    QMessageBox.warning(self, "No Image", "No image found in clipboard!")
                    return
                    
            if image:
                self.save_image(image)
            else:
                QMessageBox.warning(self, "No Image", "No image found in clipboard!")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error pasting image: {str(e)}")
            
    def take_screenshot(self):
        try:
            # Minimize the window temporarily
            self.showMinimized()
            QTimer.singleShot(500, self._capture_screenshot)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error taking screenshot: {str(e)}")
            
    def _capture_screenshot(self):
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            self.showNormal()  # Restore window
            self.save_image(screenshot)
        except Exception as e:
            self.showNormal()
            QMessageBox.critical(self, "Error", f"Error taking screenshot: {str(e)}")
            
    def save_image(self, image):
        # Generate filename based on pattern
        filename = self.generate_filename()
        filepath = os.path.join(self.save_directory, filename)
        
        # Save image
        image.save(filepath, "PNG")
        
        # Update index
        self.add_to_index(filename, filepath)
        
        # Update status
        self.status_label.setText(f"Saved: {filename}")
        
        # Clear paste area
        self.paste_text.clear()
        self.paste_text.setPlainText("Paste your screenshot here and press Enter to save...")
        
        QMessageBox.information(self, "Success", f"Screenshot saved as {filename}")
        
    def generate_filename(self):
        pattern = self.naming_pattern
        
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        date_short_str = now.strftime("%Y%m%d")
        time_12h_str = now.strftime("%I-%M-%S %p")
        year_str = now.strftime("%Y")
        
        # Create format dict with all variables
        format_dict = {
            'date': date_str,
            'time': time_str,
            'timestamp': timestamp_str,
            'date_short': date_short_str,
            'time_12h': time_12h_str,
            'year': year_str
        }
        
        # Add custom counters and increment them
        for name, data in self.custom_counters.items():
            format_dict[name] = data['value']
            # Increment counter
            self.custom_counters[name]['value'] += data.get('increment', 1)
        
        # Replace pattern variables
        filename = pattern.format(**format_dict)
        
        # Ensure it has .png extension
        if not filename.lower().endswith('.png'):
            filename += '.png'
        
        return filename
        
    def load_index(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self.screenshot_index = data.get('screenshots', [])
                    
                    # Load custom counters
                    saved_counters = data.get('custom_counters', {})
                    if saved_counters:
                        self.custom_counters = saved_counters
                    else:
                        # Migrate old counter format
                        old_counter = data.get('counter', 1)
                        self.custom_counters = {"counter": {"value": old_counter, "increment": 1}}
                    
                    # Load pattern elements if available
                    saved_elements = data.get('pattern_elements', [])
                    if saved_elements:
                        self.pattern_elements = saved_elements
                        self.update_pattern_from_elements()
                        
            except Exception as e:
                print(f"Error loading index: {e}")
                self.screenshot_index = []
                self.custom_counters = {"counter": {"value": 1, "increment": 1}}
        else:
            self.screenshot_index = []
            self.custom_counters = {"counter": {"value": 1, "increment": 1}}
            
    def add_to_index(self, filename, filepath):
        entry = {
            'filename': filename,
            'filepath': filepath,
            'created': datetime.now().isoformat(),
            'size': os.path.getsize(filepath)
        }
        
        self.screenshot_index.append(entry)
        self.save_index()
        
    def save_index(self):
        data = {
            'screenshots': self.screenshot_index,
            'custom_counters': self.custom_counters,
            'pattern_elements': self.pattern_elements,
            'naming_pattern': self.naming_pattern
        }
        
        with open(self.index_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def view_index(self):
        dialog = IndexViewDialog(self, self.screenshot_index)
        dialog.exec()
        
    def open_folder(self):
        try:
            os.startfile(self.save_directory)
        except:
            QMessageBox.critical(self, "Error", f"Could not open folder: {self.save_directory}")

    def apply_native_styling(self):
        """Apply native OS styling to the application"""
        # Remove any custom stylesheets to use pure native styling
        self.setStyleSheet("")
        
        # Set standard margins and spacing for a clean native look
        self.setContentsMargins(5, 5, 5, 5)
        
        # Use system default font
        system_font = QApplication.font()
        self.setFont(system_font)
        
        # Apply native styling to all child widgets
        self._apply_native_to_children()
    
    def _apply_native_to_children(self):
        """Apply native styling settings to all child widgets"""
        # Set minimum button heights for better native appearance
        for button in self.findChildren(QPushButton):
            button.setMinimumHeight(25)
            button.setStyleSheet("")  # Remove any custom styling
            
        # Ensure text widgets use native styling
        for text_edit in self.findChildren(QTextEdit):
            text_edit.setStyleSheet("")
            
        for line_edit in self.findChildren(QLineEdit):
            line_edit.setStyleSheet("")
            
        # Group boxes with native styling
        for group_box in self.findChildren(QGroupBox):
            group_box.setStyleSheet("")


class CustomCounterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom Counter")
        self.setFixedSize(400, 200)
        self.setStyleSheet("")  # Use native styling
        
        layout = QVBoxLayout(self)
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Counter Name:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Starting value
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Starting Value:"))
        self.start_spin = QSpinBox()
        self.start_spin.setRange(0, 99999)
        self.start_spin.setValue(1)
        start_layout.addWidget(self.start_spin)
        layout.addLayout(start_layout)
        
        # Increment
        inc_layout = QHBoxLayout()
        inc_layout.addWidget(QLabel("Increment:"))
        self.inc_spin = QSpinBox()
        self.inc_spin.setRange(1, 100)
        self.inc_spin.setValue(1)
        inc_layout.addWidget(self.inc_spin)
        layout.addLayout(inc_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("Add Counter")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_values(self):
        return self.name_edit.text().strip(), self.start_spin.value(), self.inc_spin.value()
    
    def accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Please enter a counter name")
            return
        super().accept()


class CustomTextDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Custom Text")
        self.setFixedSize(300, 150)
        self.setStyleSheet("")  # Use native styling
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Enter custom text:"))
        
        self.text_edit = QLineEdit()
        layout.addWidget(self.text_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.accept)
        button_layout.addWidget(add_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on text input and bind Enter key
        self.text_edit.setFocus()
        self.text_edit.returnPressed.connect(self.accept)
    
    def get_text(self):
        return self.text_edit.text().strip()


class CounterManagementDialog(QDialog):
    def __init__(self, parent=None, custom_counters=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Counters")
        self.setFixedSize(500, 400)
        self.setStyleSheet("")  # Use native styling
        self.custom_counters = custom_counters or {}
        
        layout = QVBoxLayout(self)
        
        # Tree widget for counters
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Counter', 'Current Value', 'Increment'])
        layout.addWidget(self.tree)
        
        self.refresh_tree()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset Selected")
        reset_btn.clicked.connect(self.reset_counter)
        button_layout.addWidget(reset_btn)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_counter)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_tree(self):
        self.tree.clear()
        for name, data in self.custom_counters.items():
            item = QTreeWidgetItem([name, str(data['value']), str(data['increment'])])
            self.tree.addTopLevelItem(item)
    
    def reset_counter(self):
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a counter to reset")
            return
        
        counter_name = current_item.text(0)
        reply = QMessageBox.question(self, "Reset Counter", 
                                   f"Reset counter '{counter_name}' to its starting value?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            original_start = self.custom_counters[counter_name].get('original_start', 1)
            self.custom_counters[counter_name]['value'] = original_start
            self.refresh_tree()
    
    def delete_counter(self):
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a counter to delete")
            return
        
        counter_name = current_item.text(0)
        
        if counter_name == "counter":
            QMessageBox.warning(self, "Cannot Delete", "Cannot delete the default counter")
            return
        
        reply = QMessageBox.question(self, "Delete Counter", 
                                   f"Delete counter '{counter_name}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.custom_counters[counter_name]
            self.refresh_tree()


class IndexViewDialog(QDialog):
    def __init__(self, parent=None, screenshot_index=None):
        super().__init__(parent)
        self.setWindowTitle("Screenshot Index")
        self.setFixedSize(600, 400)
        self.setStyleSheet("")  # Use native styling
        self.screenshot_index = screenshot_index or []
        
        layout = QVBoxLayout(self)
        
        # Tree widget for index
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Filename', 'Created', 'Size'])
        layout.addWidget(self.tree)
        
        # Populate tree
        for entry in self.screenshot_index:
            created = datetime.fromisoformat(entry['created']).strftime("%Y-%m-%d %H:%M:%S")
            size_mb = f"{entry['size'] / 1024 / 1024:.2f} MB"
            item = QTreeWidgetItem([entry['filename'], created, size_mb])
            self.tree.addTopLevelItem(item)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Pic Q'er")
    app.setOrganizationName("ScreenshotPaster")
    
    # Use native OS styling
    # Qt6 automatically uses native styling by default, but we can ensure it
    if sys.platform == "win32":
        try:
            app.setStyle('windowsvista')  # Modern Windows style
        except:
            try:
                app.setStyle('windows')  # Fallback to basic Windows style
            except:
                pass  # Use default style
    
    window = ScreenshotPaster()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()