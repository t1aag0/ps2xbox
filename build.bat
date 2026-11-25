@echo off
title Building PS2Xbox.exe
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Get it from https://www.python.org/downloads/
    echo During setup, tick "Add python.exe to PATH", then run this file again.
    pause
    exit /b 1
)

echo Installing what the build needs...
python -m pip install --upgrade pygame vgamepad pystray pillow pyinstaller || goto :fail

echo Building PS2Xbox.exe...
python -m PyInstaller --noconfirm --clean --onefile --noconsole ^
    --name PS2Xbox ^
    --collect-all vgamepad ^
    --hidden-import pystray._win32 ^
    ps2xbox.py || goto :fail

echo.
echo Done! Your app is here: %~dp0dist\PS2Xbox.exe
explorer dist
pause
exit /b 0

:fail
echo.
echo Something went wrong. Copy the messages above and send them to me.
pause
exit /b 1
