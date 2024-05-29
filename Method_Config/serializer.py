from rest_framework import serializers


# 算法配置、部件配置查询序列化器


class MethodConfigDisplaySerializer(serializers.Serializer):
    id = serializers.CharField(label="算法编号", max_length=32)
    algorithm_name = serializers.CharField(label="算法名称", max_length=32)  # 算法名称
    algorithm_channel_number = serializers.IntegerField(label="算法通道数")  # 算法通道数
    remark = serializers.CharField(label="备注", max_length=32)  # 备注
    algorithm_file = serializers.FileField(label="算法文件")  # 算法文件
    # cutterPosition = serializers.IntegerField(label="刀位号")  # 刀位号
    # is_used = serializers.BooleanField(label="是否使用")  # 是否使用


class ComponentConfigDisplaySerializer(serializers.Serializer):
    machine_number = serializers.CharField(label="机床编号", max_length=32)
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
    component_name = serializers.CharField(label="部件名称", max_length=32)  # 部件名称
    algorithm_name = serializers.CharField(label="算法名称", max_length=32)  # 算法名称
    input_channel = serializers.IntegerField(label="算法输入通道")  # 算法输入通道
    remark = serializers.CharField(label="备注", max_length=32)  # 备注
    algorithm_id = serializers.CharField(label="算法id", max_length=32)  # 算法id
    sensor_id = serializers.CharField(label="传感器id", max_length=32)  # 传感器id
    channel_id = serializers.CharField(label="通道id", max_length=32)  # 通道id
