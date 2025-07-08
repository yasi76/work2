@echo off
REM Healthcare Startup Discovery System - Windows Installation Script
REM This script sets up the system in a virtual environment on Windows

echo ===========================================================
echo Healthcare Startup Discovery System - Windows Installation
echo ===========================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is required but not found
    echo Please install Python 3.7 or later from https://python.org
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Try minimal installation first
echo Installing minimal dependencies...
python -m pip install -r requirements-minimal.txt

REM Test basic functionality
echo Testing basic installation...
python -c "print('Testing basic imports...')"
python -c "import aiohttp; print('✓ aiohttp')"
python -c "import pandas; print('✓ pandas')"
python -c "import validators; print('✓ validators')"

REM Try to install full requirements (optional)
echo.
echo Attempting full installation (optional dependencies)...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Warning: Some optional dependencies failed to install
    echo The system will work with reduced functionality
)

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; import ssl; ssl._create_default_https_context = ssl._create_unverified_context; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); print('NLTK data downloaded')"

REM Create directories
echo Creating directories...
if not exist "output" mkdir output
if not exist "logs" mkdir logs
if not exist "cache" mkdir cache

REM Create .env file
if not exist ".env" (
    echo Creating .env file...
    echo # Healthcare Startup Discovery System Configuration > .env
    echo # >> .env
    echo # Optional API keys for enhanced functionality: >> .env
    echo # CRUNCHBASE_API_KEY=your_crunchbase_api_key_here >> .env
    echo # LINKEDIN_API_KEY=your_linkedin_api_key_here >> .env
    echo # >> .env
    echo # System configuration: >> .env
    echo # LOG_LEVEL=INFO >> .env
    echo # MAX_CONCURRENT_REQUESTS=10 >> .env
    echo # DEFAULT_DELAY=1.0 >> .env
)

REM Test the installation
echo Testing installation...
python -c "from nlp_processor import HealthcareNLPProcessor; from url_validator import URLValidator; nlp = HealthcareNLPProcessor(); validator = URLValidator(); print('✓ Core modules working'); print('✓ Installation successful!')"

echo.
echo ==========================================
echo INSTALLATION COMPLETED SUCCESSFULLY!
echo ==========================================
echo.
echo To run the healthcare startup discovery:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Run the discovery system:
echo    python main.py
echo.
echo 3. Or run the demo:
echo    python demo.py
echo.
echo 4. Check the generated output files for results
echo.
echo For more information, see README.md
echo.

call venv\Scripts\deactivate.bat
pause