import os
import importlib
import pkgutil
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# === Inisialisasi Django dulu ===
django_asgi_app = get_asgi_application()

# === Setelah Django siap baru boleh akses apps ===
from django.apps import apps

# === Dynamic WebSocket discovery ===
websocket_urlpatterns = []

for app_config in apps.get_app_configs():
    try:
        routing_module = importlib.import_module(f"{app_config.name}.routing")
        if hasattr(routing_module, "websocket_urlpatterns"):
            websocket_urlpatterns += routing_module.websocket_urlpatterns
    except ModuleNotFoundError:
        continue  # skip apps yang tidak punya routing.py

# === Buat ProtocolTypeRouter ===
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
