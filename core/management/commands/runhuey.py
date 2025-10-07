import os
import sys
from importlib import import_module
import yaml
from django.core.management.base import BaseCommand
from huey.consumer import Consumer
from huey import RedisHuey

class Command(BaseCommand):
    help = "Run Huey worker for a module"

    def add_arguments(self, parser):
        parser.add_argument('module_name', type=str, help='Module name to run worker for')
        parser.add_argument('--workers', type=int, help='Number of worker threads (optional)')
        parser.add_argument('--port', type=int, help='Optional port to run the service')
        
    def handle(self, *args, **options):
        module_name = options['module_name']
        workers = options.get('workers')

        # --- Tentukan root project ---
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        CONFIG_FILE = os.path.join(BASE_DIR, "config.yaml")

        if not os.path.exists(CONFIG_FILE):
            self.stderr.write(f"[ERROR] config.yaml tidak ditemukan di {CONFIG_FILE}")
            sys.exit(1)

        with open(CONFIG_FILE, "r") as f:
            CONFIG = yaml.safe_load(f)

        redis_url = CONFIG.get("channels", {}).get("redis_url", "redis://127.0.0.1:6379/0")

        # --- Import module tasks ---
        try:
            tasks_module = import_module(f"{module_name}.tasks")
        except ModuleNotFoundError:
            self.stderr.write(f"[ERROR] Module {module_name}.tasks tidak ditemukan")
            sys.exit(1)

        # --- Ambil jumlah worker ---
        default_workers = CONFIG.get("workers", {}).get(module_name, {}).get("workers", 1)
        worker_count = workers or default_workers

        # --- Ambil instance huey dari module tasks ---
        if not hasattr(tasks_module, "huey"):
            self.stderr.write(f"[ERROR] Module {module_name}.tasks tidak memiliki instance 'huey'")
            sys.exit(1)

        huey = getattr(tasks_module, "huey")

        # --- Jalankan worker ---
        self.stdout.write(f"[HUEY] Starting worker for queue '{module_name}' with {worker_count} workers")
        consumer = Consumer(huey, worker_type="thread", workers=worker_count)
        consumer.run()
