from rest_framework import serializers
from System_Config.models import sensorConfig

# 新增配置请求
class ConfigAddSerializer(serializers.Serializer):
    machine_code = serializers.CharField(label="机床编号")
    machine_name = serializers.CharField(help_text="机床名称")
    machine_type = serializers.CharField(help_text="机床型号")
    machine_description = serializers.CharField(help_text="机床描述")
    manager = serializers.CharField(help_text="负责人")
    machine_ip = serializers.CharField(help_text="机床ip")
    machine_port = serializers.IntegerField(help_text="端口号")
    tool_number = serializers.IntegerField(help_text="刀位数量")
    database_name = serializers.CharField(help_text="时序数据库名称")
    alarm_data_delay_positive = serializers.IntegerField(help_text="正延时")
    alarm_data_delay_negative = serializers.IntegerField(help_text="负延时")
    machine_image = serializers.ImageField(help_text="机床图片")

#修改配置请求
class ConfigUpdateSerializer(serializers.Serializer):
    id=serializers.CharField(help_text="ID")
    config_id = serializers.IntegerField(help_text="系统配置id", )
    machine_code = serializers.CharField(label="机床编号")
    machine_name = serializers.CharField(help_text="机床名称")
    machine_type = serializers.CharField(help_text="机床型号")
    machine_description = serializers.CharField(help_text="机床描述")
    manager = serializers.CharField(help_text="负责人")
    machine_ip = serializers.CharField(help_text="机床ip")
    machine_port = serializers.IntegerField(help_text="端口号")
    tool_number = serializers.IntegerField(help_text="刀位数量")
    database_name = serializers.CharField(help_text="时序数据库名称")
    alarm_data_delay_positive = serializers.IntegerField(help_text="正延时")
    alarm_data_delay_negative = serializers.IntegerField(help_text="负延时")
    machine_image=serializers.ImageField(help_text="机床图片")

#删除配置请求
class ConfigDeleteSerializer(serializers.Serializer):
    id=serializers.CharField(help_text="ID")


# 应用配置请求
class ConfigApplySerializer(serializers.Serializer):
    id=serializers.CharField(help_text="ID")

#配置列表响应
class ConfigListSerializer(serializers.Serializer):
    label = serializers.CharField(label="配置序号")
    key = serializers.IntegerField(label="配置id")
    is_apply = serializers.BooleanField(label="是否应用配置")

#配置信息响应
class ConfigInformationSerializer(serializers.Serializer):
    id=serializers.CharField(label="ID")
    machine_code = serializers.CharField(label="机床编号")
    machine_name = serializers.CharField(label="机床名称")
    machine_type = serializers.CharField(label="机床型号")
    machine_description = serializers.CharField(help_text="机床描述")
    manager = serializers.CharField(label="负责人")
    machine_ip = serializers.CharField(label="机床ip")
    machine_port = serializers.IntegerField(label="端口号")
    tool_number = serializers.IntegerField(label="刀位数量")
    database_name = serializers.CharField(label="时序数据库名称")
    alarm_data_delay_positive = serializers.IntegerField(label="正延时")
    alarm_data_delay_negative = serializers.IntegerField(label="负延时")
    machine_image=serializers.ImageField(label="机床图片")
#传感器
class sensorSerializer(serializers.Serializer):
    id=serializers.CharField(label="id")
    sensor_code = serializers.CharField(label="传感器编号", max_length=32)  # 传感器编号
    sensor_name = serializers.CharField(max_length=32, label="传感器名称")  # 传感器名称
    frequency = serializers.IntegerField(label="采样频率")  # 采样频率
    channel_number = serializers.IntegerField(label="通道数")  # 通道数
    remark = serializers.CharField(max_length=32, label="备注") #备注
#传感器新增请求
class sensorUpdateserializer(serializers.Serializer):

    sensor_code = serializers.CharField(label="传感器编号", max_length=32)  # 传感器编号
    sensor_name = serializers.CharField(max_length=32, label="传感器名称")  # 传感器名称
    frequency = serializers.IntegerField(label="采样频率")  # 采样频率
    channel_number = serializers.IntegerField(label="通道数")  # 通道数
    remark = serializers.CharField(max_length=32, label="备注")  # 备注

#传感器删除请求

class sensorDeleteserializer(serializers.Serializer):
    id=serializers.CharField(label="id")


#开始监控
class monitor_onSerializer(serializers.Serializer):
    id=serializers.CharField(label="id")


#结束监控
class monitor_offSerializer(serializers.Serializer):
    id=serializers.CharField(label="id")



#通道配置修改
class channelConfigSerializer(serializers.Serializer):
    id=serializers.CharField(label="id")
    sensor_name=serializers.CharField(label="传感器名称", max_length=32)
    channel_name=serializers.CharField(label="通道名称", max_length=32)
    overrun_times=serializers.IntegerField(label="超限次数")
    channel_field=serializers.CharField(label="对应字段", max_length=32)


#通道配置显示
class channelListSerializer(serializers.Serializer):
    sensor_code=serializers.CharField(label="传感器编号", max_length=32)
    sensor_name = serializers.CharField(label="传感器名称", max_length=32)
    channel_name = serializers.CharField(label="通道名称", max_length=32)
    overrun_times = serializers.IntegerField(label="超限次数")
    channel_field = serializers.CharField(label="对应字段", max_length=32)
    is_monitor=serializers.BooleanField(label="是否监控")




