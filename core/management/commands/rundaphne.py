import os
import sys
import subprocess
import platform
import multiprocessing
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Menjalankan Django ASGI server menggunakan Gunicorn (Linux) atau Uvicorn (Windows)"

    def handle(self, *args, **options):
        try:
            # Ambil konfigurasi dari settings (bisa juga dari YAML parser kamu)
            host = getattr(settings, "ASGI_HOST", "0.0.0.0")
            port = getattr(settings, "ASGI_PORT", 8000)
            debug = getattr(settings, "DEBUG", False)

            # --- Ambil worker dari konfigurasi atau hitung otomatis ---
            # misalnya kamu punya settings.SERVER_CONFIG dari YAML
            server_conf = getattr(settings, "SERVER_CONFIG", {})
            raw_workers = server_conf.get("workers", "auto")

            if str(raw_workers).lower() == "auto":
                cpu_count = multiprocessing.cpu_count()
                workers = (2 * cpu_count) + 1
            else:
                workers = int(raw_workers)

            # --- LOG INFORMASI SERVER ---
            self.stdout.write(self.style.SUCCESS("🚀 Menjalankan ASGI Server"))
            self.stdout.write(f"Host     : {host}")
            self.stdout.write(f"Port     : {port}")
            self.stdout.write(f"Workers  : {workers}  (auto: {raw_workers})")
            self.stdout.write(f"Mode     : {'DEBUG' if debug else 'PRODUCTION'}")
            self.stdout.write(f"Alamat   : http://{host}:{port}")
            self.stdout.write("==========================================")

            # --- Jalankan server sesuai OS ---
            if platform.system().lower().startswith("win"):
                cmd = [
                    sys.executable, "-m", "uvicorn",
                    "config.asgi:application",
                    "--host", host,
                    "--port", str(port),
                    "--workers", str(workers),
                    "--log-level", "debug" if debug else "info",
                ]
            else:
                cmd = [
                    "gunicorn",
                    "config.asgi:application",
                    "-k", "uvicorn.workers.UvicornWorker",
                    "-w", str(workers),
                    "-b", f"{host}:{port}",
                    "--timeout", "120",
                    "--log-level", "debug" if debug else "info",
                ]

            subprocess.call(cmd)

        except Exception as e:
            raise CommandError(f"❌ Terjadi error saat menjalankan server: {e}")
