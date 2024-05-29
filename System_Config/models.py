from django.db import models
# 机床配置
class systemConfig(models.Model):
    # id = models.IntegerField(primary_key=True)  # id
    machine_code = models.CharField(max_length=32, null=True)  # 机床编号
    machine_name = models.CharField(max_length=32, null=True)  # 机床名称
    machine_type = models.CharField(max_length=32, null=True)  # 机床型号
    machine_description = models.CharField(max_length=32, null=True)  # 机床描述
    manager = models.CharField(max_length=32, null=True)  # 负责人
    machine_ip = models.CharField(max_length=32, null=True)  # 机床ip
    machine_port = models.IntegerField(null=True)  # 端口号
    tool_number = models.IntegerField(null=True)  # 刀位数量
    database_name = models.CharField(max_length=32, null=True)  # 时序数据库名称
    alarm_data_delay_positive = models.IntegerField(null=True)  # 正延时
    alarm_data_delay_negative = models.IntegerField(null=True)  # 负延时
    is_apply = models.BooleanField(default=0)  # 应用配置

# 传感器配置
class sensorConfig(models.Model):
    id = models.CharField(primary_key=True, max_length=32)  # 传感器编号
    sensor_name = models.CharField(max_length=32, null=True)  # 传感器名称
    frequency = models.IntegerField(null=True)  # 采样频率
    channel_number = models.IntegerField(null=True)  # 通道数
    sensor_status = models.BooleanField(default=True)  # 状态


# 通道配置
class channelConfig(models.Model):
    sensor_name = models.CharField(max_length=32, null=True)  # 传感器名称
    channel_name = models.CharField(null=True, max_length=32)  # 通道名称
    overrun_times = models.IntegerField(null=True)  # 超限次数
    channel_field = models.CharField(max_length=32, null=True)  # 对应字段
    is_monitor = models.BooleanField(default=False)  # 是否监控
    channel = models.ForeignKey(sensorConfig, db_constraint=True, on_delete=models.CASCADE)  # 外键
