import sys
import os
import yaml
import subprocess

# -------------------------------
# Set root project ke sys.path
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# -------------------------------
# Load config.yaml
# -------------------------------
CONFIG_FILE = os.path.join(BASE_DIR, "config.yaml")
with open(CONFIG_FILE) as f:
    CONFIG = yaml.safe_load(f)

# -------------------------------
# Ambil queue/module dari argumen
# -------------------------------
queue_name = sys.argv[1] if len(sys.argv) > 1 else None
if not queue_name:
    print("Usage: python runhuey <queue_name>")
    sys.exit(1)

# -------------------------------
# Set Django environment
# -------------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# -------------------------------
# Cek module tasks
# -------------------------------
try:
    __import__(f"{queue_name}.tasks")
except ModuleNotFoundError:
    print(f"[ERROR] Module {queue_name}.tasks tidak ditemukan!")
    sys.exit(1)

# -------------------------------
# Jalankan worker Huey via subprocess
# -------------------------------
print(f"[HUEY] Starting worker for queue '{queue_name}'")
subprocess.run([
    sys.executable, "-m", "huey.bin.huey_consumer",
    f"{queue_name}.tasks.huey"
])
