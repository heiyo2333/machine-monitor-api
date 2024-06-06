from django.db import models


# 设备运行状况界面信息


class faultCode(models.Model):
    config_id = models.IntegerField(null=True)  # 机床配置表的id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    warning_time = models.CharField(max_length=32, null=False)  # 警告时间
    component_name = models.CharField(max_length=32, null=True)  # 部件名称
    fault_type = models.CharField(max_length=32, null=False)  # 报警类型
    fault_code = models.CharField(max_length=32, null=False)  # 报警代码


class thermalDiagram(models.Model):
    config_id = models.IntegerField(null=True)  # 机床配置表的id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    machine_time = models.CharField(max_length=32, null=False)  # 机床工作日期
    machine_running_time = models.CharField(max_length=32, null=False)  # 机床加工时间
