from django.apps import AppConfig

class SampleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sample'
    enabled = True  # <-- flag untuk modul aktif
