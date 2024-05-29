from rest_framework import serializers


# 新增配置请求
class ConfigAddSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="ID")
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

#修改配置请求
class ConfigUpdateSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(help_text="系统配置id")
    id = serializers.CharField(help_text="ID")
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

#删除配置请求
class ConfigDeleteSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(help_text="系统配置id", )

# 应用配置请求
class ConfigApplySerializer(serializers.Serializer):
    config_id = serializers.IntegerField(help_text="系统配置id", )

#配置列表响应
class ConfigListSerializer(serializers.Serializer):
    label = serializers.CharField(label="配置序号")
    key = serializers.IntegerField(label="配置id")
    is_apply = serializers.BooleanField(label="是否应用配置")

#配置信息响应
class ConfigInformationSerializer(serializers.Serializer):
    id = serializers.CharField(label="ID")
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

