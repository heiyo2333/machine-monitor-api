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

