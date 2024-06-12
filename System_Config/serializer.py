import os
from random import random

from rest_framework import serializers

from System_Config import models
from System_Config.models import sensorConfig

# 新增配置请求
class ConfigAddSerializer(serializers.Serializer):
    machine_code = serializers.CharField(label="机床编号",max_length=32)
    machine_name = serializers.CharField(help_text="机床名称",max_length=32)
    machine_type = serializers.CharField(help_text="机床型号",max_length=32)
    machine_description = serializers.CharField(help_text="机床描述",max_length=32)
    manager = serializers.CharField(help_text="负责人",max_length=32)
    machine_ip = serializers.CharField(help_text="机床ip",max_length=32)
    machine_port = serializers.IntegerField(help_text="端口号")
    tool_number = serializers.IntegerField(help_text="刀位数量")
    database_name = serializers.CharField(help_text="时序数据库名称",max_length=32)
    alarm_data_delay_positive = serializers.IntegerField(help_text="正延时")
    alarm_data_delay_negative = serializers.IntegerField(help_text="负延时")
    machine_image = serializers.ImageField(help_text="机床图片")

#修改配置请求
class ConfigUpdateSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(help_text="系统配置id")
    machine_code = serializers.CharField(label="机床编号",max_length=32)
    machine_name = serializers.CharField(help_text="机床名称",max_length=32)
    machine_type = serializers.CharField(help_text="机床型号",max_length=32)
    machine_description = serializers.CharField(help_text="机床描述",max_length=32)
    manager = serializers.CharField(help_text="负责人",max_length=32)
    machine_ip = serializers.CharField(help_text="机床ip",max_length=32)
    machine_port = serializers.IntegerField(help_text="端口号")
    tool_number = serializers.IntegerField(help_text="刀位数量")
    database_name = serializers.CharField(help_text="时序数据库名称",max_length=32)
    alarm_data_delay_positive = serializers.IntegerField(help_text="正延时")
    alarm_data_delay_negative = serializers.IntegerField(help_text="负延时")
    machine_image=serializers.ImageField(help_text="机床图片")
    def save(self):
        config_id = self.validated_data['config_id']
        new_image = self.validated_data['machine_image']

        # 获取现有的learning_file对象
        learning_file = models.systemConfig.objects.get(config_id=config_id)

        _, file_extension = os.path.splitext(new_image.name)

        # 从本地文件系统中删除现有文件
        if learning_file.machine_image:
            os.remove(learning_file.machine_image.path)

        # count = random.randint(1, 50)
        # # 生成新的文件名
        # new_image_name = f"{learning_file.software_number}-加工图纸-{count}{file_extension}"

        # 直接更新数据库中的图片字段
        learning_file.machine_image.save(new_image, save=True)
        learning_file.save()


#删除配置请求
class ConfigDeleteSerializer(serializers.Serializer):
    id=serializers.CharField(help_text="ID")


#应用配置请求
class ConfigApplySerializer(serializers.Serializer):
    id=serializers.CharField(help_text="ID")

#拉取配置信息
class ConfigListSerializer(serializers.Serializer):
    label = serializers.CharField(label="配置序号")
    key = serializers.IntegerField(label="配置id")
    is_apply = serializers.BooleanField(label="是否应用配置")
    machine_name=serializers.CharField(label="机床名称",max_length=32)
    machine_code=serializers.CharField(label="机床编号",max_length=32)

#配置信息查询
class ConfigInformationSerializer(serializers.Serializer):
    id=serializers.CharField(label="ID")
    machine_code = serializers.CharField(label="机床编号",max_length=32)
    machine_name = serializers.CharField(label="机床名称",max_length=32)
    machine_type = serializers.CharField(label="机床型号",max_length=32)
    machine_description = serializers.CharField(help_text="机床描述",max_length=32)
    manager = serializers.CharField(label="负责人",max_length=32)
    machine_ip = serializers.CharField(label="机床ip",max_length=32)
    machine_port = serializers.IntegerField(label="端口号")
    tool_number = serializers.IntegerField(label="刀位数量")
    database_name = serializers.CharField(label="时序数据库名称",max_length=32)
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
    remark = serializers.CharField(max_length=32, label="备注",required=False) #备注
    sensor_image=serializers.ImageField(label="传感器图片")
    machine_name=serializers.CharField(label="机床名称",max_length=32)
    machine_code=serializers.CharField(label="机床编号",max_length=32)
    config_id=serializers.CharField(label="系统配置id",max_length=32)
#传感器查询
class sensorQuerysserializer(serializers.Serializer):
    id = serializers.CharField(label="id")
    sensor_code = serializers.CharField(label="传感器编号", max_length=32)  # 传感器编号
    sensor_name = serializers.CharField(max_length=32, label="传感器名称")  # 传感器名称
    frequency = serializers.IntegerField(label="采样频率")  # 采样频率
    channel_number = serializers.IntegerField(label="通道数")  # 通道数
    remark = serializers.CharField(max_length=32, label="备注", required=False)  # 备注
    sensor_image = serializers.ImageField(label="传感器图片")
    machine_name = serializers.CharField(label="机床名称", max_length=32)
    machine_code = serializers.CharField(label="机床编号", max_length=32)
    config_id = serializers.CharField(label="系统配置id", max_length=32,required=True)
#传感器新增请求
class sensorUpdateserializer(serializers.Serializer):
    sensor_code = serializers.CharField(label="传感器编号", max_length=32)  # 传感器编号
    sensor_name = serializers.CharField(max_length=32, label="传感器名称")  # 传感器名称
    frequency = serializers.IntegerField(label="采样频率")  # 采样频率
    channel_number = serializers.IntegerField(label="通道数")  # 通道数
    remark = serializers.CharField(max_length=32, label="备注",required=False)  # 备注
    sensor_image = serializers.ImageField(label="传感器图片")
    machine_name = serializers.CharField(label="机床名称", max_length=32)
    machine_code = serializers.CharField(label="机床编号", max_length=32)
    config_id = serializers.CharField(label="系统配置id", max_length=32)
    def save(self):
        sensor_code = self.validated_data['sensor_code']
        new_image = self.validated_data['sensor_image']

        # 获取现有的learning_file对象
        sensor = models.sensorConfig.objects.get(sensor_code=sensor_code)

        _, file_extension = os.path.splitext(new_image.name)

        # 从本地文件系统中删除现有文件
        if sensor.sensor_image:
            os.remove(sensor.sensor_image.path)

        # count = random.randint(1, 50)
        # # 生成新的文件名
        # new_image_name = f"{learning_file.software_number}-加工图纸-{count}{file_extension}"

        # 直接更新数据库中的图片字段
        sensor.sensor_image.save(new_image, save=True)
        sensor.save()

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




