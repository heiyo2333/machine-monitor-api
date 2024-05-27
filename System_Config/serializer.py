from rest_framework import serializers



# 配置信息响应
class ConfigInformationSerializer(serializers.Serializer):
    machine_ip = serializers.CharField(label="机床IP")
    machine_port = serializers.IntegerField(label="端口号")
    tool_number = serializers.IntegerField(label="刀位数量")
    vib_serial_port = serializers.CharField(label="振动传感器串口")
    cur_serial_port = serializers.CharField(label="电流传感器串口")
    monitor_channel_data = serializers.CharField(label="监控配置数据")
    alarm_cancel_method = serializers.CharField(label="报警取消方式，0：延时取消，1：IO输入取消")
    delay_cancel = serializers.IntegerField(label="延时取消-延时")
    io_input_cancel_port = serializers.IntegerField(label="IO输入取消-端口")
    alarm_data_delay1 = serializers.IntegerField(label="报警数据正延时")
    alarm_data_delay2 = serializers.IntegerField(label="报警数据负延时")
    data_save_method = serializers.CharField(label="数据保存方式，0：不保存，1：连续保存，2：分时段保存，3：IO触发保存")
    data_save_data = serializers.CharField(label="分时段保存——数据")
    io_input_save_port = serializers.IntegerField(label="IO触发保存端口")
    self_starting = serializers.IntegerField(label="自启动，0：否，1：是")


# 修改配置请求
class ConfigUpdateSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(help_text="系统配置id", )
    machine_ip = serializers.CharField(help_text="机床IP")
    machine_port = serializers.IntegerField(help_text="端口号")
    tool_number = serializers.IntegerField(help_text="刀位数量")
    vib_serial_port = serializers.CharField(help_text="振动传感器串口")
    cur_serial_port = serializers.CharField(help_text="电流传感器串口")
    monitor_channel_data = serializers.CharField(help_text="监控配置数据")
    alarm_cancel_method = serializers.CharField(help_text="报警取消方式，0：延时取消，1：IO输入取消")
    delay_cancel = serializers.IntegerField(required=False, help_text="延时取消-延时")
    io_input_cancel_port = serializers.IntegerField(required=False, help_text="IO输入取消-端口")
    alarm_data_delay1 = serializers.IntegerField(help_text="报警数据正延时")
    alarm_data_delay2 = serializers.IntegerField(help_text="报警数据负延时")
    data_save_method = serializers.CharField(help_text="数据保存方式，0：不保存，1：连续保存，2：分时段保存，3：IO触发保存")
    data_save_data = serializers.CharField(required=False, help_text="分时段保存——数据")
    io_input_save_port = serializers.IntegerField(required=False, help_text="IO触发保存端口")
    self_starting = serializers.IntegerField(help_text="自启动，0：否，1：是")
    home_monitor_number = serializers.IntegerField(help_text="首页信号显示数量")
    learning_monitor_number = serializers.IntegerField(help_text="自适应学习信号显示数量")
    failure_monitor_number = serializers.IntegerField(help_text="异常监测信号显示数量")


# 新增配置请求
class ConfigAddSerializer(serializers.Serializer):
    machine_ip = serializers.CharField(help_text="机床IP")
    machine_port = serializers.IntegerField(help_text="端口号")
    tool_number = serializers.IntegerField(help_text="刀位数量")
    vib_serial_port = serializers.CharField(help_text="振动传感器串口")
    cur_serial_port = serializers.CharField(help_text="电流传感器串口")
    monitor_channel_data = serializers.CharField(help_text="监控配置数据")
    alarm_cancel_method = serializers.CharField(help_text="报警取消方式，0：延时取消，1：IO输入取消")
    delay_cancel = serializers.IntegerField(required=False, help_text="延时取消-延时")
    io_input_cancel_port = serializers.IntegerField(required=False, help_text="IO输入取消-端口")
    alarm_data_delay1 = serializers.IntegerField(help_text="报警数据正延时")
    alarm_data_delay2 = serializers.IntegerField(help_text="报警数据负延时")
    data_save_method = serializers.CharField(help_text="数据保存方式，0：不保存，1：连续保存，2：分时段保存，3：IO触发保存")
    data_save_data = serializers.CharField(required=False, help_text="分时段保存——数据")
    io_input_save_port = serializers.IntegerField(required=False, help_text="IO触发保存端口")
    self_starting = serializers.IntegerField(help_text="自启动，0：否，1：是")
    home_monitor_number = serializers.IntegerField(help_text="首页信号显示数量")
    learning_monitor_number = serializers.IntegerField(help_text="自适应学习信号显示数量")
    failure_monitor_number = serializers.IntegerField(help_text="异常监测信号显示数量")
