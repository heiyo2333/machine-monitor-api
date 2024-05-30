from rest_framework import serializers


# 算法配置：展示序列化器、新增算法序列化器、编辑序列化器
class AlgorithmSerializer(serializers.Serializer):
    algorithm_id = serializers.IntegerField(help_text="算法id")
    algorithm_code = serializers.CharField(help_text="算法编号", max_length=32)  # 算法编号
    algorithm_name = serializers.CharField(help_text="算法名称", max_length=32)  # 算法名称
    algorithm_channel_number = serializers.IntegerField(help_text="算法通道数")  # 算法通道数
    remark = serializers.CharField(help_text="备注", max_length=32, required=False)  # 备注
    algorithm_file = serializers.FileField(help_text="算法文件")  # 算法文件


# 算法配置：删除算法请求序列化器
class deleteAlgorithmSerializer(serializers.Serializer):
    algorithm_code = serializers.CharField(help_text="算法编号", max_length=32)  # 算法编号


# 部件配置：查询部件请求序列化器、删除部件请求序列化器
class deleteComponentConfigSerializer(serializers.Serializer):
    machine_code = serializers.CharField(label="机床编号", max_length=32)  # 机床编号


# 部件配置：新增部件请求序列化器、编辑部件请求序列化器
class componentConfigSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(label="系统配置id")  # (实际上是系统配置的id)
    component_name = serializers.CharField(label="部件名称", max_length=32)  # 部件名称
    algorithm_id = serializers.IntegerField(label="算法id", required=True)  # 算法id
    input_channel1 = serializers.IntegerField(label="算法输入通道1", required=False)  # 算法输入通道1对应的id
    input_channel2 = serializers.IntegerField(label="算法输入通道2", required=False)  # 算法输入通道2对应的id
    input_channel3 = serializers.IntegerField(label="算法输入通道3", required=False)  # 算法输入通道3对应的id
    input_channel4 = serializers.IntegerField(label="算法输入通道4", required=False)  # 算法输入通道4对应的id
    input_channel5 = serializers.IntegerField(label="算法输入通道5", required=False)  # 算法输入通道5对应的id
    remark = serializers.CharField(label="备注", max_length=32, required=False)  # 备注


# 部件配置：机床选择下拉框请求序列化器
class machineSelectSerializer(serializers.Serializer):
    machine_code = serializers.CharField(label="机床编号", max_length=32)  # 机床编号
    machine_name = serializers.CharField(label="机床名称", max_length=32)  # 机床名称
