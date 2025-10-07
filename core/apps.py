# core/apps.py
import os
import sys
import importlib
from django.apps import AppConfig
import subprocess

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        command = sys.argv[1] if len(sys.argv) > 1 else None

        # === Bersihkan layar ===
        try:
            if os.name == "nt":  # Windows
                os.system("cls")
            else:  # Linux / Mac
                os.system("clear")
        except Exception:
            pass

        # === Cek port dari sys.argv ===
        port = 8000
        if "--port" in sys.argv:
            try:
                port = int(sys.argv[sys.argv.index("--port") + 1])
            except Exception:
                port = 8000  # fallback default
        print(f"\n[INFO] === Django starting with command: {command}, port: {port} ===\n")

        for module_name in os.listdir(BASE_DIR):
            module_path = os.path.join(BASE_DIR, module_name)
            if not os.path.isdir(module_path) or module_name.startswith((".", "_")):
                continue

            try:
                mod_apps = importlib.import_module(f"{module_name}.apps")
                for attr in dir(mod_apps):
                    cls = getattr(mod_apps, attr)
                    if isinstance(cls, type) and hasattr(cls, "enabled"):

                        # === Mode runserver → hanya enabled ===
                        if command == "runserver":
                            if getattr(cls, "enabled", False):
                                print(f"  ✔ {module_name}")

                        # === Mode runservice → hanya modul target ===
                        elif command == "runservice":
                            if len(sys.argv) > 2 and sys.argv[2] == module_name:
                                print(f"  🚀 {module_name}")
            except ModuleNotFoundError:
                continue

        print("=========================================\n")
