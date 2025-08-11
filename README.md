# Screenshot Utility Tool
A lightweight, interactive desktop application for pasting screenshots with automatic indexing and customizable naming patterns.

## Features

- **Paste Screenshots**: Paste screenshots from clipboard with a simple Enter key press
- **Take Screenshots**: Capture full-screen screenshots directly from the app
- **Customizable Naming**: Define your own naming patterns using variables
- **Automatic Indexing**: All screenshots are automatically indexed with metadata
- **File Management**: Browse and organize your screenshot directory
- **Keyboard Shortcuts**: Quick access with Ctrl+V and Ctrl+S

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python screenshot_paster.py
   ```

## Usage

### Basic Usage

1. **Paste Screenshot**:
   - Copy a screenshot to your clipboard (Ctrl+PrintScreen or Snipping Tool)
   - Open the app and press Enter in the paste area
   - Or use Ctrl+V shortcut

2. **Take Screenshot**:
   - Click "Take Screenshot" button
   - Or use Ctrl+S shortcut
   - The app will minimize briefly to capture the screen

### Naming Patterns

Customize how your screenshots are named using these variables:

- `{date}` - Current date (YYYY-MM-DD)
- `{time}` - Current time (HH-MM-SS)
- `{counter}` - Sequential counter
- `{timestamp}` - Full timestamp (YYYY-MM-DD_HH-MM-SS)

**Examples**:
- `{date}_{time}_{counter}` → `2024-01-15_14-30-25_1.png`
- `screenshot_{counter}` → `screenshot_1.png`
- `{timestamp}` → `2024-01-15_14-30-25.png`

### Configuration

- **Save Directory**: Choose where screenshots are saved (default: ~/Pictures/Screenshots)
- **Naming Pattern**: Set your preferred naming convention
- **Index File**: Automatically maintained JSON file with screenshot metadata

### Features

- **Automatic Indexing**: Each screenshot is logged with filename, path, creation time, and file size
- **View Index**: Browse all saved screenshots with metadata
- **Open Folder**: Quickly access the screenshot directory
- **Status Updates**: Real-time feedback on operations

## File Structure

```
pic_queuer/
├── screenshot_paster.py    # Main application
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── [screenshot_directory]/
    ├── screenshot_index.json  # Automatic index file
    └── [screenshot files]     # Your saved screenshots
```

## Keyboard Shortcuts

- `Ctrl+V` - Paste and save screenshot from clipboard
- `Ctrl+S` - Take a new screenshot
- `Enter` - Save pasted screenshot (when focus is in paste area)

## Requirements

- Python 3.6+
- tkinter (usually included with Python)
- Pillow (PIL) for image processing
- pyperclip for clipboard access

## Troubleshooting

**"No image found in clipboard"**
- Make sure you've copied a screenshot to your clipboard
- Try using Snipping Tool or PrintScreen + Ctrl+C

**Permission errors**
- Ensure you have write permissions to the save directory
- Try changing the save directory to a location you have access to

**Screenshot not capturing properly**
- Make sure no other applications are using the screen capture
- Try running the app as administrator if needed

## License

This project is open source and available under the MIT License. 
