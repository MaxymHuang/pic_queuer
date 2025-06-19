# Screenshot Paster & Indexer Launcher
Write-Host "Starting Screenshot Paster & Indexer..." -ForegroundColor Green

try {
    # Check if Python is installed
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python from https://python.org" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan
    
    # Check if requirements are installed
    Write-Host "Checking dependencies..." -ForegroundColor Yellow
    python -c "import PIL, pyperclip" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    
    # Run the application
    Write-Host "Launching application..." -ForegroundColor Green
    python screenshot_paster.py
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
} 