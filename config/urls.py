from django.contrib import admin
from django.urls import path, include, re_path
from django.apps import apps
from django.http import HttpResponseRedirect
import importlib

urlpatterns = [
    path("admin/", admin.site.urls),
]

for app_config in apps.get_app_configs():
    try:
        importlib.import_module(f"{app_config.name}.urls")
        urlpatterns.append(
            path(f"{app_config.label}/", include(f"{app_config.name}.urls"))
        )
    except ModuleNotFoundError:
        pass

urlpatterns.append(
    re_path(r"^$", lambda request: HttpResponseRedirect("/admin/"))
)
