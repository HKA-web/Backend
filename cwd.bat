@echo off
REM === Aktifkan virtualenv ===
call "%~dp0venv\Scripts\activate.bat"

REM === Jalankan Django dengan argumen yang diketik ===
python manage.py %*

REM === Tetap buka CMD jika tanpa argumen ===
if "%~1"=="" (
    echo.
    echo Gunakan: cwd [command]
    echo Contoh: cwd runserver, cwd runhuey authentication
    cmd /k
)
