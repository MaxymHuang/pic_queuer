import sys
from PyQt6.QtWidgets import QApplication
from screenshot_paster import ScreenshotPaster

def main():
    print("Starting Screenshot Paster & Indexer...")
    app = QApplication(sys.argv)
    app.setApplicationName("Pic Q'er")
    app.setOrganizationName("ScreenshotPaster")
    
    # Use native OS styling
    # Qt6 automatically uses native styling by default, but we can ensure it
    import sys
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
