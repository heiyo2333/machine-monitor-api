from django.db import models


# 系统配置
class SystemConfiguration(models.Model):
    machine_ip = models.CharField(max_length=32, null=True)  # 机床ip
    machine_port = models.CharField(max_length=32, null=True)  # 端口号
    tool_number = models.IntegerField(null=True)  # 刀位数量
    vib_serial_port = models.CharField(max_length=32, null=True)  # 振动传感器串口
    cur_serial_port = models.CharField(max_length=32, null=True)  # 电流传感器串口
    alarm_cancel_method = models.CharField(max_length=32, null=True)  # 报警取消方式
    delay_cancel = models.IntegerField(null=True)  # 延时取消-延时
    io_input_cancel_port = models.IntegerField(null=True)  # IO输入取消-端口
    alarm_data_delay_positive = models.IntegerField(null=True)  # 报警数据正延时
    alarm_data_delay_negative = models.IntegerField(null=True)  # 报警数据延时
    data_save_method = models.CharField(max_length=32, null=True)  # 数据保存方式
    io_input_save_port = models.IntegerField(null=True)  # IO触发保存端口
    self_starting = models.BooleanField(default=False)  # 自启动
    is_apply = models.BooleanField(default=False)  # 应用配置
    # 监控数量
    home_monitor_number = models.IntegerField(null=True, default=2000)  # 主页监控数据量
    learning_monitor_number = models.IntegerField(null=True, default=2000)  # 自适应学习页面监控数据量
    failure_monitor_number = models.IntegerField(null=True, default=1000)  # 故障监测页面监控数据量
    database_name = models.CharField(max_length=32, null=True)  # 时序数据库名称