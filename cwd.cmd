@echo off
REM === Aktifkan virtualenv ===
call "%~dp0env\Scripts\activate.bat"

REM === Jalankan Django dengan argumen yang diketik ===
python manage.py %*

REM === Tetap buka CMD jika tanpa argumen ===
if "%~1"=="" (
    cmd /k
)
