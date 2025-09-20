#!/usr/bin/env python3
"""
Build script to create a single executable file from the screenshot paster application.
Uses PyInstaller to bundle everything into a standalone .exe file.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_directories():
    """Clean up any existing build directories"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning up {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Remove .spec files
    for spec_file in Path('.').glob('*.spec'):
        print(f"Removing {spec_file}...")
        spec_file.unlink()

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building Screenshot Paster executable...")
    
    # PyInstaller command with options (using uv run)
    cmd = [
        'uv', 'run', 'pyinstaller',
        '--onefile',                    # Create a single executable file
        '--windowed',                   # Don't show console window (GUI app)
        '--name=ScreenshotPaster',      # Name of the executable
        '--add-data=README.md;.',       # Include README in the bundle
        '--hidden-import=PIL',          # Ensure PIL is included
        '--hidden-import=PIL.Image',    # Ensure PIL.Image is included
        '--hidden-import=PIL.ImageTk',  # Ensure PIL.ImageTk is included
        '--hidden-import=PIL.ImageGrab', # Ensure PIL.ImageGrab is included
        '--hidden-import=pyperclip',    # Ensure pyperclip is included
        '--clean',                      # Clean PyInstaller cache
        'screenshot_paster.py'          # Main script to compile
    ]
    
    try:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def post_build_cleanup():
    """Clean up build artifacts, keeping only the executable"""
    print("\nCleaning up build artifacts...")
    
    # Keep only the dist folder with the executable
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("Removed build directory")
    
    # Remove .spec file
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        spec_file.unlink()
        print(f"Removed {spec_file}")

def main():
    """Main build process"""
    print("=== Screenshot Paster Executable Builder ===\n")
    
    # Check if main script exists
    if not os.path.exists('screenshot_paster.py'):
        print("Error: screenshot_paster.py not found!")
        print("Make sure you're running this script from the project directory.")
        sys.exit(1)
    
    # Clean up previous builds
    clean_build_directories()
    
    # Build the executable
    success = build_executable()
    
    if success:
        # Clean up build artifacts
        post_build_cleanup()
        
        # Show results
        exe_path = Path('dist/ScreenshotPaster.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ SUCCESS!")
            print(f"📁 Executable created: {exe_path}")
            print(f"📊 File size: {size_mb:.1f} MB")
            print(f"\n🎉 Build Complete!")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"📦 Single executable file: dist/ScreenshotPaster.exe")
            print(f"🚀 Ready for distribution - no Python required!")
            print(f"💾 Standalone application with all dependencies included")
            print(f"\n📋 What you can do with this executable:")
            print(f"   • Copy to any Windows machine")
            print(f"   • Run without installing Python or dependencies")
            print(f"   • Share with users who don't have Python")
            print(f"   • Deploy to production environments")
            print(f"\n⚡ To test: Run 'dist\\ScreenshotPaster.exe' or double-click it")
        else:
            print("\n❌ Build completed but executable not found in expected location.")
    else:
        print("\n❌ Build failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
