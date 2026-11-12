@echo off
title GDrive Manager
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\python.exe" main.py
) else (
    echo Virtual environment not found. Please run setup first.
    pause
)
