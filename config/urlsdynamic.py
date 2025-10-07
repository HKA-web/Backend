# core/dynamic_urls.py
from django.urls import path, include
from rest_framework import routers
import importlib
import os

router = routers.DefaultRouter()

# Ambil nama service dari ENV (diset di runservice.py)
service_name = os.environ.get("RUNSERVICE_MODULE")

if service_name:
    try:
        mod = importlib.import_module(f"{service_name}.urls")
        if hasattr(mod, "router"):
            router.registry.extend(mod.router.registry)
    except ModuleNotFoundError:
        pass

urlpatterns = [
    path("api/", include(router.urls)),
]
