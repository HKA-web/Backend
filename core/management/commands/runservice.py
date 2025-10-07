import os
import sys
import yaml
import importlib
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Run an independent service module (only if enabled=False)'

    def add_arguments(self, parser):
        parser.add_argument('service_name', type=str, help='Name of the service/module')
        parser.add_argument('--port', type=int, help='Optional port to run the service')

    def handle(self, *args, **options):
        service_name = options['service_name']
        port = options.get('port')

        # --- Fix path config.yaml ---
        BASE_DIR = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        CONFIG_FILE = os.path.join(BASE_DIR, "config.yaml")

        if not os.path.exists(CONFIG_FILE):
            self.stderr.write(f"[ERROR] config.yaml not found at {CONFIG_FILE}")
            sys.exit(1)

        with open(CONFIG_FILE) as f:
            CONFIG = yaml.safe_load(f)

        DEBUG = CONFIG['server'].get('debug', True)
        HOST = CONFIG['server'].get('host', '0.0.0.0')
        PORT = port or CONFIG['server'].get('port', 8000)

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

        # --- Import apps.py untuk cek enabled ---
        try:
            mod_apps = importlib.import_module(f"{service_name}.apps")
        except ModuleNotFoundError:
            self.stderr.write(f"[ERROR] Module '{service_name}' not found.")
            sys.exit(1)

        # Cari class turunan AppConfig
        app_config_class = None
        for name, obj in mod_apps.__dict__.items():
            if hasattr(obj, "__bases__") and "AppConfig" in [b.__name__ for b in obj.__bases__]:
                app_config_class = obj
                break

        if not app_config_class:
            self.stderr.write(f"[ERROR] No AppConfig class found in {service_name}.apps")
            sys.exit(1)

        # --- Ambil flag enabled ---
        enabled = getattr(app_config_class, "enabled", True)

        # Jika enabled=True -> TOLAK
        if enabled:
            self.stderr.write(
                f"[DENIED] Module '{service_name}' is a NORMAL module (enabled=True) "
                "and cannot be run with runservice."
            )
            sys.exit(1)

        self.stdout.write(
            f"[OK] Module '{service_name}' is independent (enabled=False). Running service..."
        )

        # --- Inject dynamic urls ---
        os.environ["RUNSERVICE_MODULE"] = service_name

        # Override ROOT_URLCONF supaya hanya load modul ini
        from django.conf import settings
        settings.ROOT_URLCONF = "config.urlsdynamic"

        # --- Jalankan service ---
        if DEBUG:
            from django.core.management import execute_from_command_line
            self.stdout.write(f"[DEBUG] Running {service_name} on {HOST}:{PORT}")
            execute_from_command_line([sys.argv[0], 'runserver', f'{HOST}:{PORT}'])
        else:
            self.stdout.write(f"[PROD] Running {service_name} on {HOST}:{PORT}")
            os.system(f"daphne -b {HOST} -p {PORT} config.asgi:application")
