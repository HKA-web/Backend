import os
import importlib
from pathlib import Path
from django.urls import path, include
from rest_framework import routers

router = routers.DefaultRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
apps_to_scan = []

for item in os.listdir(BASE_DIR):
    item_path = BASE_DIR / item
    if item_path.is_dir() and (item_path / "apps.py").exists():
        try:
            mod_apps = importlib.import_module(f"{item}.apps")
            # Cari class AppConfig di apps.py
            for attr_name in dir(mod_apps):
                attr = getattr(mod_apps, attr_name)
                if hasattr(attr, "enabled"):  
                    if getattr(attr, "enabled", True):  # hanya kalau enabled=True
                        apps_to_scan.append(item)
        except Exception:
            continue

# --- Scan urls.py hanya untuk module normal (enabled=True) ---
for app in apps_to_scan:
    try:
        mod = importlib.import_module(f"{app}.urls")
        if hasattr(mod, "router"):
            router.registry.extend(mod.router.registry)
    except ModuleNotFoundError:
        continue

urlpatterns = [
    path("api/", include(router.urls)),
]
