from django.db import models

import systemConfig.models


# 算法配置
class algorithmConfig(models.Model):
    algorithm_code = models.CharField(max_length=32, null=True)  # 算法编号
    algorithm_name = models.CharField(max_length=32, null=True)  # 算法名称
    algorithm_channel_number = models.IntegerField(null=True)  # 算法通道数
    algorithm_file = models.FileField(upload_to='AlgorithmFile/', null=True)  # 算法文件
    remark = models.CharField(max_length=32, null=True)  # 备注
    algorithm_monitor_status = models.BooleanField(default=False)  # 算法监测状态
    config = models.ForeignKey(systemConfig.models.systemConfig, db_constraint=True, on_delete=models.CASCADE, null=True)  # 外键


# 算法附表：算法下的部件
class algorithmChannel(models.Model):
    algorithm = models.ForeignKey(algorithmConfig, db_constraint=True, on_delete=models.CASCADE)  # 外键
    # channel_id = models.IntegerField(null=True)  # 算法编号
    channel = models.ForeignKey(systemConfig.models.channelConfig, db_constraint=True, on_delete=models.CASCADE, null=True)  # 外键


# 部件配置主表
class componentConfig(models.Model):
    config_id = models.IntegerField(null=True)  # 机床所在配置的id
    component_code = models.CharField(max_length=32, null=False)  # 部件编号
    component_name = models.CharField(max_length=32, null=True)  # 部件名称
    remark = models.CharField(max_length=32, null=True)  # 备注
    component_status = models.BooleanField(max_length=32, null=False, default=0)  # 部件运行状态
    monitor_status = models.BooleanField(default=False)  # 监测状态
    x_axis = models.CharField(max_length=65535, null=True)  # 横坐标
    y_pre_axis = models.CharField(max_length=65535, null=True)  # 纵坐标1
    y_last_axis = models.CharField(max_length=65535, null=True)  # 纵坐标2
    middle_value = models.IntegerField(default=40)  # 中期阈值
    last_value = models.IntegerField(default=20)  # 末期阈值


# 部件附表：部件下的传感器
class componentSensor(models.Model):
    component = models.ForeignKey(componentConfig, db_constraint=True, on_delete=models.CASCADE)  # 外键
    # sensor_id = models.IntegerField(null=True)  # 传感器id
    sensor = models.ForeignKey(systemConfig.models.sensorConfig, db_constraint=True, on_delete=models.CASCADE, null=True)  # 外键
