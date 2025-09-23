import sys
import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Load config
CONFIG_FILE = os.path.join(BASE_DIR, "config.yaml")
with open(CONFIG_FILE) as f:
    CONFIG = yaml.safe_load(f)

DEBUG = CONFIG['server'].get('debug', True)
HOST = CONFIG['server'].get('host', '0.0.0.0')

# Ambil argumen: service_name + optional port
service_name = sys.argv[1] if len(sys.argv) > 1 else None
port_arg = sys.argv[2] if len(sys.argv) > 2 else None

if not service_name:
    print("Usage: python runservice.py <service_name> [port]")
    sys.exit(1)

PORT = int(port_arg) if port_arg else CONFIG['server'].get('port', 8000)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Run server
if DEBUG:
    from django.core.management import execute_from_command_line
    print(f"[DEBUG] Running {service_name} on {HOST}:{PORT}")
    execute_from_command_line([sys.argv[0], 'runserver', f'{HOST}:{PORT}'])
else:
    print(f"[PROD] Running {service_name} on {HOST}:{PORT}")
    socket_file = f"/tmp/{service_name}.sock"
    os.system(f"daphne -u {socket_file} config.asgi:application")
