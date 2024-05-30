from rest_framework import serializers


# 算法配置、部件配置查询序列化器


class EquipmentStatusSerializer(serializers.Serializer):
    machine_code = serializers.CharField(label="机床编号", max_length=32)
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
    component_number = serializers.CharField(label="部件编号", max_length=32)  # 部件编号
    component_name = serializers.CharField(label="部件名称", max_length=32)  # 部件名称
    component_status = serializers.CharField(label="部件运行状态", max_length=32)  # 部件运行状态
    monitor_status = serializers.BooleanField(label="是否监测")  # 监测状态
    # cutterPosition = serializers.IntegerField(label="刀位号")  # 刀位号
    # is_used = serializers.BooleanField(label="是否使用")  # 是否使用


class MonitorValueSerializer(serializers.Serializer):
    value_name = serializers.CharField(label="物理量名称", max_length=32)  # 物理量名称
    value_unit = serializers.CharField(label="物理量单位", max_length=32)  # 物理量单位
    value = serializers.IntegerField(label="物理量数值")  # 物理量数值


class SensorStatusSerializer(serializers.Serializer):
    sensor_code = serializers.CharField(label="传感器编号", max_length=32)  # 传感器编号
    sensor_name = serializers.CharField(label="传感器名称", max_length=32)  # 传感器名称
    sensor_status = serializers.CharField(label="传感器运行状况", max_length=32)  # 传感器运行状况


class FaultCodeSerializer(serializers.Serializer):
    machine_code = serializers.CharField(label="机床编号", max_length=32)  # 机床编号
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
    warning_time = serializers.CharField(label="警告时间", max_length=32)  # 警告时间
    component_name = serializers.CharField(label="部件名称", max_length=32)  # 部件名称
    fault_type = serializers.CharField(label="报警类型", max_length=32)  # 报警类型
    fault_code = serializers.CharField(label="报警代码", max_length=32)  # 报警代码


class ThermalDiagramSerializer(serializers.Serializer):
    machine_code = serializers.CharField(label="机床编号", max_length=32)  # 机床编号
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
    machine_running_time = serializers.CharField(label="机床加工时间", max_length=32)  # 机床加工时间
