from django.db import models


# 设备运行状况界面信息
class machineStatus(models.Model):
    # id = models.IntegerField(primary_key=True)
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    component_number = models.CharField(max_length=32, null=False)  # 部件编号
    component_name = models.CharField(max_length=32, null=False)  # 部件名称
    component_status = models.CharField(max_length=32, null=False)  # 部件运行状态
    monitor_status = models.BooleanField(default=False)  # 监测状态


class monitorValue(models.Model):
    # id = models.IntegerField(primary_key=True)  # id
    value_name = models.CharField(null=False, max_length=32)  # 监测物理量名称
    value_unit = models.CharField(null=False, max_length=32)  # 物理量单位
    value = models.IntegerField(null=False)  # 物理量数值


class faultCode(models.Model):
    # id = models.CharField(primary_key=True, max_length=32)  # id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    warning_time = models.CharField(max_length=32, null=False)  # 警告时间
    component_name = models.CharField(max_length=32, null=True)  # 部件名称
    fault_type = models.CharField(max_length=32, null=False)  # 报警类型
    fault_code = models.CharField(max_length=32, null=False)  # 报警代码


class sensorStatus(models.Model):
    # id = models.CharField(primary_key=True, max_length=32)  # id
    sensor_code = models.CharField(max_length=32, null=True)  # 传感器编号
    sensor_name = models.CharField(max_length=32, null=True)  # 传感器名称
    sensor_status = models.CharField(max_length=32, null=True)  # 传感器运行状况


class thermalDiagram(models.Model):
    # id = models.CharField(primary_key=True, max_length=32)  # 机床id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    machine_running_time = models.CharField(max_length=32, null=False)  # 机床加工时间
