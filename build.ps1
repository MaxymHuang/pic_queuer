# Screenshot Paster Executable Builder (PowerShell)
# This script builds a single executable file using PyInstaller

Write-Host "==========================================="
Write-Host "   Screenshot Paster Executable Builder"
Write-Host "==========================================="
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found Python: $pythonVersion"
} catch {
    Write-Host "❌ Error: Python not found!"
    Write-Host "Please make sure Python is installed and in your PATH."
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "screenshot_paster.py")) {
    Write-Host "❌ Error: screenshot_paster.py not found!"
    Write-Host "Please run this script from the project directory."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "🔨 Starting build process..."
Write-Host ""

# Run the build script
try {
    python build_exe.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Build completed successfully!"
        
        # Check if executable was created
        if (Test-Path "dist\ScreenshotPaster.exe") {
            $exeSize = (Get-Item "dist\ScreenshotPaster.exe").Length / 1MB
            Write-Host "📁 Executable: dist\ScreenshotPaster.exe"
            Write-Host "📊 Size: $([math]::Round($exeSize, 1)) MB"
            Write-Host ""
            Write-Host "🎉 You can now distribute this single file!"
            Write-Host "No Python installation required on target machines."
        }
    } else {
        Write-Host "❌ Build failed. Check error messages above."
    }
} catch {
    Write-Host "❌ An error occurred during the build process:"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "Press Enter to exit..."
Read-Host

