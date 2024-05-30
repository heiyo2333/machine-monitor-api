from django.db import models


# 算法配置
class methodConfig(models.Model):
    algorithm_code = models.CharField(max_length=32, null=True)  # 算法编号
    algorithm_name = models.CharField(max_length=32, null=True)  # 算法名称
    algorithm_channel_number = models.IntegerField(null=True)  # 算法通道数
    algorithm_file = models.FileField(upload_to='AlgorithmFile/', null=True)  # 算法文件
    remark = models.CharField(max_length=32, null=True)  # 备注


# 部件配置主表
class componentConfig(models.Model):
    config_id = models.IntegerField(null=True)  # 机床所在配置的id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    component_name = models.CharField(max_length=32, null=True)  # 部件名称
    algorithm_id = models.IntegerField(max_length=32, null=True)  # 算法id
    algorithm_name = models.CharField(max_length=32, null=True)  # 算法名称
    algorithm_channel = models.CharField(max_length=32, null=True)  # 算法输入通道1
    remark = models.CharField(max_length=32, null=True)  # 备注


# 部件配置附表
class algorithmChannel(models.Model):
    sensor_id = models.IntegerField(max_length=32, null=True)  # 传感器id
    sensor_name = models.CharField(max_length=32, null=True)  # 传感器名称
    channe_id = models.IntegerField(max_length=32, null=True)  # 通道id
    channe_name = models.CharField(max_length=32, null=True)  # 通道名称
    algorithm_channel = models.ForeignKey(componentConfig, db_constraint=True, on_delete=models.CASCADE)  # 外键

