from django.db import models
from django.utils import timezone


# 警告及故障代码
class faultCode(models.Model):
    config_id = models.IntegerField(null=True)  # 机床配置id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    warning_time = models.CharField(max_length=32, null=False)  # 警告时间
    component_id = models.IntegerField(null=True)  # 部件id
    component_name = models.CharField(max_length=32, null=True)  # 部件名称
    fault_type = models.CharField(max_length=32, null=False)  # 报警类型
    fault_code = models.CharField(max_length=32, null=False)  # 报警代码


# 加工时间热力图
class thermalDiagram(models.Model):
    config_id = models.IntegerField(null=True)  # 机床配置id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    machine_process_date = models.DateField(default=timezone.now)  # 机床工作日期
    machine_running_time = models.FloatField(max_length=32, null=False)  # 机床加工时间


# 加工时间热力图
class machineParameter(models.Model):
    config_id = models.IntegerField(null=True)  # 机床配置id
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    machine_t = models.FloatField(max_length=32, null=False)  # 机床温度
    machine_p = models.FloatField(max_length=32, null=False)  # 机床功率
    machine_a = models.FloatField(max_length=32, null=False)  # 机床加速度
    machine_t_unit = models.CharField(max_length=32, null=False)  # 温度单位
    machine_p_unit = models.CharField(max_length=32, null=False)  # 功率单位
    machine_a_unit = models.CharField(max_length=32, null=False)  # 加速度单位
    # machine_t_min = models.CharField(max_length=32, null=False)  # 温度最小值
    machine_t_max = models.CharField(max_length=32, null=False)  # 温度最大值
    # machine_p_min = models.CharField(max_length=32, null=False)  # 功率最小值
    machine_p_max = models.CharField(max_length=32, null=False)  # 功率最大值
    # machine_a_min = models.CharField(max_length=32, null=False)  # 加速度最小值
    machine_a_max = models.CharField(max_length=32, null=False)  # 加速度最大值

