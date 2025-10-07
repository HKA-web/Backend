from django.apps import AppConfig

class WhatsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'whatsapp'
    enabled = True  # <-- flag untuk modul aktif
