from django.db import models


# 监测信号展示界面信息
class methodConfig(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 机床id
    algorithm_name = models.CharField(max_length=32, null=True)  # 部件名称
    algorithm_channel_number = models.IntegerField(null=True)  # 传感器名称
    remark = models.CharField(max_length=32, null=True)  # 通道名称


class componentConfig(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    machine_name = models.CharField(max_length=32, null=True)
    component_name = models.CharField(max_length=32, null=True)
    algorithm_name = models.CharField(max_length=32, null=True)
    input_channel = models.CharField(max_length=32, null=True)
    remark = models.CharField(max_length=32, null=True)
    components = models.ForeignKey()
