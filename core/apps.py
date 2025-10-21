import os
import sys
import importlib
import multiprocessing
import math
from django.apps import AppConfig

# ==========================================
# 🧠 Fungsi utilitas: alokasi worker otomatis
# ==========================================
def get_total_workers(config):
    workers = config.get("server", {}).get("workers", 1)
    if str(workers).lower() == "auto":
        return multiprocessing.cpu_count()
    return int(workers)
    
def allocate_workers_by_priority(config: dict) -> dict:
    """
    Mengalokasikan worker per modul berdasar priority.
    Semakin kecil priority, semakin besar jatah worker.
    """
    server_conf = config.get("server", {})
    workers_conf = config.get("workers", {})

    cpu_count = multiprocessing.cpu_count()
    raw_total = server_conf.get("workers", "auto")

    # Hitung total worker
    if str(raw_total).lower() == "auto":
        total_workers = (2 * cpu_count) + 1
    else:
        total_workers = int(raw_total)

    # Jika tidak ada workers_conf → kembalikan kosong
    if not workers_conf:
        return {}

    # Ambil priority tiap modul
    priorities = {m: conf.get("priority", 10) for m, conf in workers_conf.items()}

    # Balik priority jadi bobot
    weights = {m: 1 / p if p > 0 else 1 for m, p in priorities.items()}
    total_weight = sum(weights.values())

    allocation = {}
    for module, weight in weights.items():
        allocated = max(1, round((weight / total_weight) * total_workers))
        allocation[module] = allocated

    # Pastikan total tidak melebihi kapasitas
    total_alloc = sum(allocation.values())
    if total_alloc > total_workers:
        sorted_mods = sorted(priorities.items(), key=lambda x: x[1], reverse=True)
        for mod, _ in sorted_mods:
            if total_alloc <= total_workers:
                break
            if allocation[mod] > 1:
                allocation[mod] -= 1
                total_alloc -= 1

    return allocation

# ==========================================
# ⚙️ Class utama CoreConfig
# ==========================================
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        command = sys.argv[1] if len(sys.argv) > 1 else None

        # === Hindari banner di proses worker/server ===
        if any(x in sys.argv[0].lower() for x in ["daphne", "gunicorn", "uvicorn"]):
            return
        if command in ["-b", "-k", "-w"]:
            return

        # === Bersihkan layar ===
        try:
            os.system("cls" if os.name == "nt" else "clear")
        except Exception:
            pass

        # === Deteksi host & port dari berbagai sumber ===
        from django.conf import settings

        host = None
        port = None

        # 1️⃣ Cek argumen gaya --port / -p
        for flag in ("--port", "-p"):
            if flag in sys.argv:
                try:
                    port = int(sys.argv[sys.argv.index(flag) + 1])
                    break
                except (IndexError, ValueError):
                    continue

        # 2️⃣ Cek argumen gaya host:port (misal: 0.0.0.0:8001)
        if port is None or host is None:
            for arg in sys.argv:
                if ":" in arg:
                    parts = arg.split(":")
                    try:
                        # Format bisa 0.0.0.0:8001 atau [::1]:8002
                        port_candidate = int(parts[-1])
                        port = port_candidate
                        host_candidate = ":".join(parts[:-1])
                        if host_candidate:
                            host = host_candidate
                        break
                    except ValueError:
                        continue

        # 3️⃣ Ambil dari settings (YAML)
        if host is None:
            host = getattr(settings, "SERVER_HOST", "127.0.0.1")
        if port is None:
            try:
                port = int(getattr(settings, "SERVER_PORT", 8000))
            except Exception:
                port = 8000

        # 4️⃣ Pastikan valid
        if not isinstance(port, int):
            port = 8000
        if not isinstance(host, str):
            host = "127.0.0.1"

        # === Banner startup ===
        print(f"\n[INFO] === Django starting with command: {command}, host: {host}, port: {port} ===\n")

        # === Scan setiap module di BASE_DIR ===
        for module_name in os.listdir(BASE_DIR):
            module_path = os.path.join(BASE_DIR, module_name)
            if not os.path.isdir(module_path) or module_name.startswith((".", "_")):
                continue

            try:
                mod_apps = importlib.import_module(f"{module_name}.apps")
                for attr in dir(mod_apps):
                    cls = getattr(mod_apps, attr)
                    if isinstance(cls, type) and hasattr(cls, "enabled"):
                        if command == "runserver":
                            if getattr(cls, "enabled", False):
                                print(f"  ✔ {module_name}")
                        elif command == "runservice":
                            if len(sys.argv) > 2 and sys.argv[2] == module_name:
                                print(f"  🚀 {module_name}")
            except ModuleNotFoundError:
                continue

        print("=========================================\n")
