import os
import sys
import yaml
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run a service module'

    def add_arguments(self, parser):
        parser.add_argument('service_name', type=str, help='Name of the service/module')
        parser.add_argument('--port', type=int, help='Optional port to run the service')

    def handle(self, *args, **options):
        service_name = options['service_name']
        port = options.get('port')

        # --- Fix path config.yaml ---
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        CONFIG_FILE = os.path.join(BASE_DIR, "config.yaml")

        if not os.path.exists(CONFIG_FILE):
            self.stderr.write(f"[ERROR] config.yaml not found at {CONFIG_FILE}")
            sys.exit(1)

        with open(CONFIG_FILE) as f:
            CONFIG = yaml.safe_load(f)

        DEBUG = CONFIG['server']['debug']
        HOST = CONFIG['server'].get('host', '0.0.0.0')
        PORT = port or CONFIG['server'].get('port', 8000)

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

        if DEBUG:
            from django.core.management import execute_from_command_line
            self.stdout.write(f"[DEBUG] Running {service_name} on {HOST}:{PORT}")
            execute_from_command_line([sys.argv[0], 'runserver', f'{HOST}:{PORT}'])
        else:
            self.stdout.write(f"[PROD] Running {service_name} on {HOST}:{PORT}")
            os.system(f"daphne -u /tmp/{service_name}.sock config.asgi:application")
