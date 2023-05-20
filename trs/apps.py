from django.apps import AppConfig


class TRSConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trs'
    
    def ready(self):
        import trs.signals
