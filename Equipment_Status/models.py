from django.db import models
from django.utils import timezone


# 警告及故障代码
class faultCode(models.Model):
    config_id = models.IntegerField(null=True)  # 机床配置id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    warning_time = models.CharField(max_length=32, null=False)  # 警告时间
    component_id = models.IntegerField(null=True) # 部件id
    component_name = models.CharField(max_length=32, null=True)  # 部件名称
    fault_type = models.CharField(max_length=32, null=False)  # 报警类型
    fault_code = models.CharField(max_length=32, null=False)  # 报警代码


# 加工时间热力图
class thermalDiagram(models.Model):
    config_id = models.IntegerField(null=True)  # 机床配置id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    machine_process_date = models.DateField(default=timezone.now)  # 机床工作日期
    machine_running_time = models.CharField(max_length=32, null=False)  # 机床加工时间
