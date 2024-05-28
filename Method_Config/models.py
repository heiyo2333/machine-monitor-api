from django.db import models


# 监测信号展示界面信息
class methodConfig(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 算法id
    algorithm_name = models.CharField(max_length=32, null=True)  # 算法名称
    algorithm_channel_number = models.IntegerField(null=True)  # 算法通道数
    remark = models.CharField(max_length=32, null=True)  # 备注


class componentConfig(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 部件id
    machine_number = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    component_name = models.CharField(max_length=32, null=True)  # 部件名称
    algorithm_name = models.CharField(max_length=32, null=True)  # 算法名称
    input_channel = models.CharField(max_length=32, null=True)  # 算法输入通道
    remark = models.CharField(max_length=32, null=True)  # 备注
    algorithm_id = models.CharField(max_length=32, null=True)  # 算法id
    sensor_id = models.CharField(max_length=32, null=True)  # 传感器id
    channel_id = models.IntegerField(null=True)  # 通道id


class algorithmChannel(models.Model):
    id = models.IntegerField(primary_key=True)  # 算法id
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    component_name = models.CharField(max_length=32, null=True)  # 部件名称
    algorithm_name = models.CharField(max_length=32, null=True)  # 算法名称
    input_channel = models.CharField(max_length=32, null=True)  # 算法输入通道
    remark = models.CharField(max_length=32, null=True)  # 备注
    algorithm_channel = models.ForeignKey(componentConfig, db_constraint=True, on_delete=models.CASCADE)  # 外键
