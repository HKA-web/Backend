import sys
import signal
from importlib import import_module
from django.conf import settings
from django.core.management.base import BaseCommand
from huey.consumer import Consumer
from core.apps import allocate_workers_by_priority, get_total_workers


class Command(BaseCommand):
    help = "Menjalankan Huey worker untuk modul tertentu (berdasarkan priority config)"

    def add_arguments(self, parser):
        parser.add_argument("module_name", type=str, help="Nama modul Huey (misal: authentication)")
        parser.add_argument("--workers", type=int, help="Override jumlah thread worker")
        parser.add_argument("--verbose", action="store_true", help="Aktifkan logging verbose")

    def handle(self, *args, **options):
        module_name = options["module_name"]
        override_workers = options.get("workers")
        verbose = options.get("verbose", False)

        # --- Ambil konfigurasi dari settings.py ---
        config_yaml = getattr(settings, "CONFIG", {})  # FIX: sebelumnya CONFIG_YAML, sekarang CONFIG
        redis_url = config_yaml.get("channels", {}).get("redis_url", "redis://127.0.0.1:6379/0")

        # --- Hitung total CPU & alokasi per modul ---
        total_workers = get_total_workers(config_yaml)
        allocation = allocate_workers_by_priority(config_yaml)

        allocated_workers = allocation.get(module_name, 1)
        worker_count = override_workers or allocated_workers

        # --- Import modul tasks ---
        try:
            tasks_module = import_module(f"{module_name}.tasks")
        except ModuleNotFoundError:
            self.stderr.write(self.style.ERROR(f"[ERROR] Module '{module_name}.tasks' tidak ditemukan"))
            sys.exit(1)

        if not hasattr(tasks_module, "huey"):
            self.stderr.write(self.style.ERROR(f"[ERROR] '{module_name}.tasks' tidak punya instance 'huey'"))
            sys.exit(1)

        huey = getattr(tasks_module, "huey")

        # --- Tampilkan informasi ---
        self.stdout.write(self.style.SUCCESS(
            f"🚀 Menjalankan {worker_count} worker untuk modul '{module_name}'"
        ))
        if verbose:
            self.stdout.write(f"[INFO] Redis URL: {redis_url}")
            self.stdout.write(f"[INFO] Total CPU Workers: {total_workers}")
            self.stdout.write(f"[INFO] Alokasi penuh: {allocation}")

        # --- Jalankan Huey consumer ---
        consumer = Consumer(huey, worker_type="thread", workers=worker_count)

        def shutdown_handler(signum, frame):
            self.stdout.write(self.style.WARNING(f"⛔ Worker '{module_name}' dihentikan"))
            consumer.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        consumer.run()
