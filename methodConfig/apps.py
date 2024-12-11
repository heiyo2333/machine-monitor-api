from django.apps import AppConfig


class MonitoringsignaldisplayConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'methodConfig'

    def ready(self):
        import methodConfig.scheduler
