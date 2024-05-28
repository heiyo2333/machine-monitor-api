from django.db import models
from System_Config.models import systemConfig
from System_Config.models import sensorConfig


# 设备运行状况界面信息
class machineStatus(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 机床id
    monitor_status = models.BooleanField(default=False)  # 全部开始监测状态
    component_name = models.CharField(max_length=32, null=False)  # 部件名称
    component_number = models.CharField(max_length=32, null=False)  # 部件编号
    component_status = models.CharField(max_length=32, null=False)  # 部件运行状态
    open_state = models.BooleanField(default=False)  # 开启状态


class temperaturePowerAcceleration(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 机床id
    machine_temperature = models.CharField(max_length=32, null=False)  # 机床运行温度
    machine_power = models.CharField(max_length=32, null=False)  # 机床运行功率
    machine_acceleration = models.CharField(max_length=32, null=False)  # 机床主轴加速度


class warningWithFaultCode(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 机床id
    warning_time = models.CharField(max_length=32, null=False)  # 警告时间
    warning_component = models.CharField(max_length=32, null=False)  # 警告部件
    fault_type = models.CharField(max_length=32, null=False)  # 报警类型
    fault_code = models.CharField(max_length=32, null=False)  # 报警代码


class thermalDiagram(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 机床id
    machine_running_time = models.CharField(max_length=32, null=False)  # 机床加工时间


class sensorRunningCondition(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 传感器id
    sensor_name = models.CharField(max_length=32, null=False)  # 传感器名称
    sensor_status = models.CharField(max_length=32, null=False)  # 传感器运行状况
