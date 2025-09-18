import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
from datetime import datetime
from PIL import Image, ImageTk, ImageGrab
import pyperclip
import re
from pathlib import Path

class ScreenshotPaster:
    def __init__(self, root):
        self.root = root
        self.root.title("Pic Q'er")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configuration
        self.save_directory = os.path.expanduser("~/Pictures/Screenshots")
        self.naming_pattern = "{date}_{time}_{counter}"
        self.pattern_elements = ["date", "time", "counter"]  # New: track pattern as list
        self.custom_counters = {"counter": {"value": 1, "increment": 1}}  # New: custom counters
        self.index_file = os.path.join(self.save_directory, "screenshot_index.json")
        
        # Ensure save directory exists
        os.makedirs(self.save_directory, exist_ok=True)
        
        # Load existing index
        self.load_index()
        
        self.setup_ui()
        self.bind_shortcuts()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Screenshot Utility for Windows", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Save Directory Section
        ttk.Label(main_frame, text="Save Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dir_var = tk.StringVar(value=self.save_directory)
        dir_entry = ttk.Entry(main_frame, textvariable=self.dir_var, width=50)
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_directory).grid(row=1, column=2, pady=5)
        
        # Naming Pattern Section
        pattern_frame = ttk.LabelFrame(main_frame, text="Naming Pattern Builder", padding="10")
        pattern_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        pattern_frame.columnconfigure(1, weight=1)
        
        # Pattern preview
        ttk.Label(pattern_frame, text="Preview:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pattern_preview = tk.StringVar()
        preview_label = ttk.Label(pattern_frame, textvariable=self.pattern_preview, 
                                 font=("Arial", 10, "bold"), foreground="blue")
        preview_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Current pattern display
        ttk.Label(pattern_frame, text="Pattern:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pattern_display = tk.StringVar(value=self.naming_pattern)
        pattern_label = ttk.Label(pattern_frame, textvariable=self.pattern_display, 
                                 font=("Arial", 9), foreground="gray")
        pattern_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Variable buttons
        self.setup_pattern_builder(pattern_frame)
        
        # Paste Area
        paste_frame = ttk.LabelFrame(main_frame, text="Paste Screenshot Here", padding="10")
        paste_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        paste_frame.columnconfigure(0, weight=1)
        
        self.paste_text = scrolledtext.ScrolledText(paste_frame, height=8, width=70)
        self.paste_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.paste_text.insert(tk.END, "Paste your screenshot here and press Enter to save...")
        self.paste_text.bind('<Key>', self.on_key_press)
        self.paste_text.bind('<Button-1>', self.on_click)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Paste & Save", command=self.paste_and_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Take Screenshot", command=self.take_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Index", command=self.view_index).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to paste screenshots")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 9))
        status_label.grid(row=7, column=0, columnspan=3, pady=(10, 0))
        
        # Initialize pattern preview
        self.update_pattern_preview()
        
    def setup_pattern_builder(self, parent):
        # Variable buttons frame
        var_frame = ttk.Frame(parent)
        var_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(var_frame, text="Click to add variables:").grid(row=0, column=0, columnspan=6, sticky=tk.W, pady=(0, 5))
        
        # Date/Time variables
        date_vars = [
            ("Date", "date", "YYYY-MM-DD"),
            ("Time", "time", "HH-MM-SS"), 
            ("Timestamp", "timestamp", "YYYY-MM-DD_HH-MM-SS"),
            ("Date Short", "date_short", "YYYYMMDD"),
            ("Time 12h", "time_12h", "HH-MM-SS AM/PM"),
            ("Year", "year", "YYYY")
        ]
        
        for i, (label, var, desc) in enumerate(date_vars):
            btn = ttk.Button(var_frame, text=label, 
                           command=lambda v=var: self.add_pattern_element(v))
            btn.grid(row=1, column=i, padx=2, pady=2, sticky="ew")
            
        # Counter variables
        ttk.Label(var_frame, text="Counters:").grid(row=2, column=0, columnspan=6, sticky=tk.W, pady=(10, 5))
        
        counter_frame = ttk.Frame(var_frame)
        counter_frame.grid(row=3, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=5)
        
        # Default counter
        ttk.Button(counter_frame, text="Counter", 
                  command=lambda: self.add_pattern_element("counter")).pack(side=tk.LEFT, padx=2)
        
        # Custom counter button
        ttk.Button(counter_frame, text="+ Custom Counter", 
                  command=self.add_custom_counter).pack(side=tk.LEFT, padx=2)
        
        # Manage counters button
        ttk.Button(counter_frame, text="Manage Counters", 
                  command=self.manage_counters).pack(side=tk.LEFT, padx=2)
        
        # Custom text and separators
        ttk.Label(var_frame, text="Separators & Text:").grid(row=4, column=0, columnspan=6, sticky=tk.W, pady=(10, 5))
        
        separator_frame = ttk.Frame(var_frame)
        separator_frame.grid(row=5, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=5)
        
        separators = [("_", "_"), ("-", "-"), (".", "."), (" ", "space"), ("Custom Text", "custom")]
        for text, sep in separators:
            if sep == "custom":
                ttk.Button(separator_frame, text=text, 
                          command=self.add_custom_text).pack(side=tk.LEFT, padx=2)
            else:
                ttk.Button(separator_frame, text=text, 
                          command=lambda s=sep: self.add_pattern_element(s)).pack(side=tk.LEFT, padx=2)
        
        # Pattern control buttons
        control_frame = ttk.Frame(var_frame)
        control_frame.grid(row=6, column=0, columnspan=6, sticky=(tk.W, tk.E), pady=(10, 5))
        
        ttk.Button(control_frame, text="Clear Pattern", 
                  command=self.clear_pattern).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Reset to Default", 
                  command=self.reset_pattern).pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Undo Last", 
                  command=self.undo_last_element).pack(side=tk.LEFT, padx=2)

    def bind_shortcuts(self):
        self.root.bind('<Control-v>', lambda e: self.paste_and_save())
        self.root.bind('<Control-s>', lambda e: self.take_screenshot())
        
    def on_key_press(self, event):
        if event.keysym == 'Return':
            self.paste_and_save()
            return 'break'
            
    def on_click(self, event):
        if self.paste_text.get("1.0", tk.END).strip() == "Paste your screenshot here and press Enter to save...":
            self.paste_text.delete("1.0", tk.END)
    
    # Pattern building methods
    def add_pattern_element(self, element):
        """Add an element to the pattern"""
        self.pattern_elements.append(element)
        self.update_pattern_from_elements()
        self.update_pattern_preview()
    
    def add_custom_counter(self):
        """Add a custom counter"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Custom Counter")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Counter Name:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        name_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=name_var, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Starting Value:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        start_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=start_var, width=20).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(dialog, text="Increment:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        inc_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=inc_var, width=20).grid(row=2, column=1, padx=10, pady=5)
        
        def save_counter():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("Invalid Input", "Please enter a counter name")
                return
            try:
                start_val = int(start_var.get())
                increment = int(inc_var.get())
            except ValueError:
                messagebox.showwarning("Invalid Input", "Please enter valid numbers")
                return
                
            if name in self.custom_counters:
                if not messagebox.askyesno("Counter Exists", f"Counter '{name}' already exists. Overwrite?"):
                    return
                    
            self.custom_counters[name] = {"value": start_val, "increment": increment}
            self.add_pattern_element(name)
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(button_frame, text="Add Counter", command=save_counter).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_custom_text(self):
        """Add custom text to pattern"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Custom Text")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Enter custom text:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        text_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=text_var, width=30)
        entry.grid(row=1, column=0, padx=10, pady=5)
        entry.focus()
        
        def save_text():
            text = text_var.get().strip()
            if text:
                self.add_pattern_element(text)
                dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=2, column=0, pady=10)
        ttk.Button(button_frame, text="Add", command=save_text).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        entry.bind('<Return>', lambda e: save_text())
    
    def manage_counters(self):
        """Open counter management dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Manage Counters")
        dialog.geometry("500x400")
        
        # Create treeview for counters
        columns = ('Counter', 'Current Value', 'Increment')
        tree = ttk.Treeview(dialog, columns=columns, show='headings', height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Populate tree
        def refresh_tree():
            tree.delete(*tree.get_children())
            for name, data in self.custom_counters.items():
                tree.insert('', tk.END, values=(name, data['value'], data['increment']))
        
        refresh_tree()
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def reset_counter():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a counter to reset")
                return
            item = tree.item(selection[0])
            counter_name = item['values'][0]
            
            if messagebox.askyesno("Reset Counter", f"Reset counter '{counter_name}' to its starting value?"):
                # Find original increment to determine starting value
                original_start = self.custom_counters[counter_name].get('original_start', 1)
                self.custom_counters[counter_name]['value'] = original_start
                refresh_tree()
        
        def delete_counter():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select a counter to delete")
                return
            item = tree.item(selection[0])
            counter_name = item['values'][0]
            
            if counter_name == "counter":
                messagebox.showwarning("Cannot Delete", "Cannot delete the default counter")
                return
                
            if messagebox.askyesno("Delete Counter", f"Delete counter '{counter_name}'?"):
                del self.custom_counters[counter_name]
                refresh_tree()
        
        ttk.Button(button_frame, text="Reset Selected", command=reset_counter).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=delete_counter).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
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
        self.pattern_display.set(self.naming_pattern)
    
    def update_pattern_preview(self):
        """Update the pattern preview with current date/time"""
        try:
            preview = self.generate_filename_preview()
            self.pattern_preview.set(preview)
        except Exception as e:
            self.pattern_preview.set("Invalid pattern")
    
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
        directory = filedialog.askdirectory(initialdir=self.save_directory)
        if directory:
            self.save_directory = directory
            self.dir_var.set(directory)
            self.index_file = os.path.join(directory, "screenshot_index.json")
            self.load_index()
            
    def show_pattern_help(self):
        help_text = """Naming Pattern Variables:
        
{date} - Current date (YYYY-MM-DD)
{time} - Current time (HH-MM-SS)
{counter} - Sequential counter
{timestamp} - Full timestamp (YYYY-MM-DD_HH-MM-SS)

Examples:
- {date}_{time}_{counter} → 2024-01-15_14-30-25_1.png
- screenshot_{counter} → screenshot_1.png
- {timestamp} → 2024-01-15_14-30-25.png"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Naming Pattern Help")
        help_window.geometry("400x300")
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
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
                    messagebox.showwarning("No Image", "No image found in clipboard!")
                    return
                    
            if image:
                self.save_image(image)
            else:
                messagebox.showwarning("No Image", "No image found in clipboard!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error pasting image: {str(e)}")
            
    def take_screenshot(self):
        try:
            # Minimize the window temporarily
            self.root.iconify()
            self.root.after(500, self._capture_screenshot)
        except Exception as e:
            messagebox.showerror("Error", f"Error taking screenshot: {str(e)}")
            
    def _capture_screenshot(self):
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            self.root.deiconify()  # Restore window
            self.save_image(screenshot)
        except Exception as e:
            self.root.deiconify()
            messagebox.showerror("Error", f"Error taking screenshot: {str(e)}")
            
    def save_image(self, image):
        # Generate filename based on pattern
        filename = self.generate_filename()
        filepath = os.path.join(self.save_directory, filename)
        
        # Save image
        image.save(filepath, "PNG")
        
        # Update index
        self.add_to_index(filename, filepath)
        
        # Update status
        self.status_var.set(f"Saved: {filename}")
        
        # Clear paste area
        self.paste_text.delete("1.0", tk.END)
        self.paste_text.insert(tk.END, "Paste your screenshot here and press Enter to save...")
        
        messagebox.showinfo("Success", f"Screenshot saved as {filename}")
        
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
        index_window = tk.Toplevel(self.root)
        index_window.title("Screenshot Index")
        index_window.geometry("600x400")
        
        # Create treeview
        columns = ('Filename', 'Created', 'Size')
        tree = ttk.Treeview(index_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            
        # Add data
        for entry in self.screenshot_index:
            created = datetime.fromisoformat(entry['created']).strftime("%Y-%m-%d %H:%M:%S")
            size_mb = f"{entry['size'] / 1024 / 1024:.2f} MB"
            tree.insert('', tk.END, values=(entry['filename'], created, size_mb))
            
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(index_window, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
    def open_folder(self):
        try:
            os.startfile(self.save_directory)
        except:
            messagebox.showerror("Error", f"Could not open folder: {self.save_directory}")

def main():
    root = tk.Tk()
    app = ScreenshotPaster(root)
    root.mainloop()

if __name__ == "__main__":
    main() 