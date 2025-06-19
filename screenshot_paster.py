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
        self.root.title("Screenshot Paster & Indexer")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Configuration
        self.save_directory = os.path.expanduser("~/Pictures/Screenshots")
        self.naming_pattern = "{date}_{time}_{counter}"
        self.counter = 1
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
        title_label = ttk.Label(main_frame, text="Screenshot Paster & Indexer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Save Directory Section
        ttk.Label(main_frame, text="Save Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dir_var = tk.StringVar(value=self.save_directory)
        dir_entry = ttk.Entry(main_frame, textvariable=self.dir_var, width=50)
        dir_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_directory).grid(row=1, column=2, pady=5)
        
        # Naming Pattern Section
        ttk.Label(main_frame, text="Naming Pattern:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.pattern_var = tk.StringVar(value=self.naming_pattern)
        pattern_entry = ttk.Entry(main_frame, textvariable=self.pattern_var, width=50)
        pattern_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Help", command=self.show_pattern_help).grid(row=2, column=2, pady=5)
        
        # Pattern variables info
        pattern_info = ttk.Label(main_frame, text="Available variables: {date}, {time}, {counter}, {timestamp}", 
                                font=("Arial", 8), foreground="gray")
        pattern_info.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        
        # Paste Area
        paste_frame = ttk.LabelFrame(main_frame, text="Paste Screenshot Here", padding="10")
        paste_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        paste_frame.columnconfigure(0, weight=1)
        
        self.paste_text = scrolledtext.ScrolledText(paste_frame, height=8, width=70)
        self.paste_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.paste_text.insert(tk.END, "Paste your screenshot here and press Enter to save...")
        self.paste_text.bind('<Key>', self.on_key_press)
        self.paste_text.bind('<Button-1>', self.on_click)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Paste & Save", command=self.paste_and_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Take Screenshot", command=self.take_screenshot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Index", command=self.view_index).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_var = tk.StringVar(value="Ready to paste screenshots")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Arial", 9))
        status_label.grid(row=6, column=0, columnspan=3, pady=(10, 0))
        
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
        pattern = self.pattern_var.get()
        
        # Get current date and time
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H-%M-%S")
        timestamp_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        
        # Replace pattern variables
        filename = pattern.format(
            date=date_str,
            time=time_str,
            counter=self.counter,
            timestamp=timestamp_str
        )
        
        # Ensure it has .png extension
        if not filename.lower().endswith('.png'):
            filename += '.png'
            
        # Increment counter
        self.counter += 1
        
        return filename
        
    def load_index(self):
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    data = json.load(f)
                    self.screenshot_index = data.get('screenshots', [])
                    self.counter = data.get('counter', 1)
            except:
                self.screenshot_index = []
                self.counter = 1
        else:
            self.screenshot_index = []
            self.counter = 1
            
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
            'counter': self.counter
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