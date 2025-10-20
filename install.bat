@echo off
REM ================================================
REM  Script untuk membuat Virtual Environment (venv)
REM  dan menginstall dependencies dari requirements.txt
REM  Menggunakan Python dari folder bin/
REM ================================================

REM Set path Python dari folder bin
set PYTHON_BIN=%~dp0bin\python\python.exe

if not exist "%PYTHON_BIN%" (
    echo [ERROR] Python tidak ditemukan di %PYTHON_BIN%
    pause
    exit /b 1
)

REM Membuat virtual environment
echo [INFO] Membuat virtual environment...
"%PYTHON_BIN%" -m venv venv

REM Aktivasi venv
echo [INFO] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip ke versi terbaru
echo [INFO] Upgrade pip...
python -m pip install --upgrade pip

REM Install requirements.txt
if exist requirements.txt (
    echo [INFO] Menginstall dependencies dari requirements.txt...
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt tidak ditemukan!
)

echo [INFO] Selesai! venv siap digunakan.
pause
