from django.db import models


# 机床配置
class systemConfig(models.Model):
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
    machine_image = models.ImageField(null=True, upload_to='Machine/MachineImage/')  #机床图片


# 传感器配置
class sensorConfig(models.Model):
    sensor_code = models.CharField(max_length=32, null=True)  # 传感器编号
    sensor_name = models.CharField(max_length=32, null=True)  # 传感器名称
    frequency = models.IntegerField(null=True)  # 采样频率
    channel_number = models.IntegerField(null=True)  # 通道数
    measurement = models.CharField(max_length=32, null=True)  # 传感器数据库字段
    remark = models.CharField(max_length=32, null=True)  # 备注
    sensor_status = models.BooleanField(default=0)  # 状态 1：开启 0：关闭
    operational_status = models.BooleanField(default=True)  # 运行状态
    thread_flag = models.BooleanField(default=0)  # 多线程标志位
    time_out = models.IntegerField(null=True)  # 超时时间
    receive_number = models.IntegerField(null=True)  # 接收数据数量
    sensor_image = models.ImageField(null=True, upload_to='Sensor/SensorImage/')  # 传感器图片
    sensor_port = models.IntegerField(null=True)  # 传感器端口号
    command_code = models.CharField(max_length=32, null=True)  # 传感器操作指令
    config_id = models.CharField(max_length=32, null=True)


# 通道配置
class channelConfig(models.Model):
    sensor_name = models.CharField(max_length=32, null=True)  # 传感器名称
    sensor_code = models.CharField(max_length=32, null=True)  # 传感器名称
    channel_name = models.CharField(null=True, max_length=32)  # 通道名称
    overrun_times = models.IntegerField(null=True)  # 超限次数
    unit = models.CharField(max_length=32, null=True)  # 单位
    channel_field = models.CharField(max_length=32, null=True)  # 对应字段
    is_monitor = models.BooleanField(default=False)  # 是否监控
    channel = models.ForeignKey(sensorConfig, db_constraint=True, on_delete=models.CASCADE)  # 外键
    remark = models.CharField(max_length=32, null=True)  # 备注


# class context(models.Model):
#     name = models.CharField(max_length=4, null=True)  # 名称
#     value = models.CharField(max_length=4, null=True)  # 值
#     type = models.CharField(max_length=4, null=True)  # 类型
class sensorStatusContext(models.Model):
    type = models.CharField(max_length=32, null=True)  # 状态类型：是否配置
    value = models.CharField(max_length=32, null=True)  # 状态名称
