from django.urls import path, include
from rest_framework import routers
import importlib

router = routers.DefaultRouter()

apps_to_scan = ['authentication', 'core', 'services']
for app in apps_to_scan:
    try:
        mod = importlib.import_module(f'{app}.urls')
        if hasattr(mod, 'router'):
            router.registry.extend(mod.router.registry)
    except ModuleNotFoundError:
        continue

urlpatterns = [
    path('api/', include(router.urls)),
]
