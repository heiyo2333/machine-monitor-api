from rest_framework import serializers


# 设备运行状况查询序列化器
class EquipmentStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="id")
    machine_code = serializers.CharField(label="机床编号", max_length=32)
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
    component_code = serializers.CharField(label="部件编号", max_length=32)  # 部件编号
    component_name = serializers.CharField(label="部件名称", max_length=32)  # 部件名称
    component_status = serializers.CharField(label="部件运行状态", max_length=32)  # 部件运行状态
    monitor_status = serializers.BooleanField(label="是否监测")  # 监测状态


# 传感器状态查询序列化器
class SensorStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="传感器配置表id")
    sensor_code = serializers.CharField(label="传感器编号", max_length=32)  # 传感器编号
    sensor_name = serializers.CharField(label="传感器名称", max_length=32)  # 传感器名称
    operational_status = serializers.CharField(label="传感器运行状况", max_length=32)  # 传感器运行状况


# 警告及故障代码查询序列化器
class FaultCodeSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(label="config_id")
    machine_code = serializers.CharField(label="机床编号", max_length=32)  # 机床编号
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
    warning_time = serializers.CharField(label="警告时间", max_length=32)  # 警告时间
    component_name = serializers.CharField(label="部件名称", max_length=32)  # 部件名称
    fault_type = serializers.CharField(label="报警类型", max_length=32)  # 报警类型
    fault_code = serializers.CharField(label="报警代码", max_length=32)  # 报警代码


# 警告及故障代码填写请求序列化器
class AddFaultCodeSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(label="config_id")
    warning_time = serializers.CharField(label="警告时间", max_length=32)  # 警告时间
    fault_type = serializers.CharField(label="报警类型", max_length=32)  # 报警类型
    fault_code = serializers.CharField(label="报警代码", max_length=32)  # 报警代码


# 机床加工热力图查询序列化器
class ThermalDiagramSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(label="config_id")
    machine_code = serializers.CharField(label="机床编号", max_length=32)  # 机床编号
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
    machine_time = serializers.CharField(label="机床工作日期", max_length=32)  # 机床工作日期
    machine_running_time = serializers.CharField(label="机床加工时间", max_length=32)  # 机床加工时间


# 机床加工热力图填写请求序列化器
class AddThermalDiagramSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(label="config_id")
    machine_time = serializers.CharField(label="机床工作日期", max_length=32)  # 机床工作日期
    machine_running_time = serializers.CharField(label="机床加工时间", max_length=32)  # 机床加工时间


# 部件树查询序列化器
class ComponentTreeSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="id")
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
    component_name = serializers.CharField(label="部件名称", max_length=32)  # 部件名称


# 开始监控
class monitor_onSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="id")


# 结束监控
class monitor_offSerializer(serializers.Serializer):
    id = serializers.IntegerField(label="id")


# 部件选择下拉框请求序列化器
class componentSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(label="系统配置id")  # (实际上是系统配置的id)
    component_name = serializers.CharField(label="部件名称", max_length=32)  # 部件名称
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
