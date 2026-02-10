@echo off
SETLOCAL EnableExtensions EnableDelayedExpansion

REM --- Configuration ---
SET "VENV_DIR=.venv"
SET "PYTHON_EXE=python"
SET "REQUIREMENTS_FILE=requirements.txt"
SET "MAIN_SCRIPT=main:app"

REM --- Check for Python ---
where %PYTHON_EXE% >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b 1
)

REM --- Virtual Environment Setup ---
IF NOT EXIST "%VENV_DIR%\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    IF EXIST "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
    %PYTHON_EXE% -m venv %VENV_DIR%
    IF %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [INFO] Virtual environment created successfully.
)

REM --- Activate Venv ---
IF EXIST "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
) ELSE (
    echo [ERROR] Virtual environment scripts not found at "%VENV_DIR%\Scripts\activate.bat".
    pause
    exit /b 1
)

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM --- Install Dependencies ---
echo [INFO] Checking dependencies...
pip install -r %REQUIREMENTS_FILE%
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

REM --- Run Application ---
echo.
echo [INFO] Starting Barcode Scanner...
echo [INFO] Press Ctrl+C to stop.
echo.
python -m uvicorn %MAIN_SCRIPT% --reload --host 127.0.0.1 --port 8000

REM --- Deactivate on Exit ---
if defined VIRTUAL_ENV deactivate
ENDLOCAL
