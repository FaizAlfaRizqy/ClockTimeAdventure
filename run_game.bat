@echo off
echo ================================
echo  Classic RPG - Python Version
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan!
    echo Silakan install Python dari: https://www.python.org/
    pause
    exit /b 1
)

REM Check if pygame is installed
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo Pygame belum terinstall. Installing...
    pip install pygame
    echo.
)

echo Starting game...
echo.
python main.py

pause
