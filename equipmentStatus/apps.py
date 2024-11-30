from django.apps import AppConfig


class MachinerunningconditionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'equipmentStatus'

    # def ready(self):
    #     import scheduler  # 确保这里的路径是正确的
