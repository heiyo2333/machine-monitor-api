from django.db import models

# 监测信号展示界面信息
class algorithmConfiguration(models.Model):
    id = models.CharField(primary_key=True, null=True)  # 机床id
    algorithm_name = models.CharField(max_length=32, null=True)  # 部件名称
    algorithm_channel_number = models.IntegerField(null=True)  # 传感器名称
    remark = models.CharField(max_length=32, null=True)  # 通道名称
