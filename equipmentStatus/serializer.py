from rest_framework import serializers


# 算法运行状态
class algorithmStatusListSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="id")
    algorithm_code = serializers.CharField(help_text="算法编码", max_length=32)  # 算法编号
    algorithm_name = serializers.CharField(help_text="算法名称", max_length=32)  # 算法名称
    algorithm_type = serializers.IntegerField(help_text="算法类型")  # 算法类型：0--故障诊断，1--寿命预测
    function_name = serializers.CharField(help_text="算法函数名称", max_length=32)  # 算法函数名称
    algorithm_monitor_status = serializers.BooleanField(help_text="是否监测")  # 算法监测状态


# 报警记录
class faultInformationSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="id")
    config_id = serializers.IntegerField(help_text="机床配置id")
    machine_code = serializers.CharField(help_text="机床编号", max_length=32)  # 机床编号
    machine_name = serializers.CharField(help_text="机床名称", max_length=32)  # 机床名称
    warning_time = serializers.CharField(help_text="警告时间", max_length=32)  # 警告时间
    component_name = serializers.CharField(help_text="部件名称", max_length=32)  # 部件名称
    fault_type = serializers.CharField(help_text="报警类型", max_length=32)  # 报警类型
    fault_status = serializers.CharField(help_text="报警代码", max_length=32)  # 报警状态


# 机床加工热力图
class thermalDiagramSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(help_text="配置id")
    data = serializers.CharField(help_text="坐标数据", max_length=32)  # 坐标数据


# 机床加工热力图填写
class addThermalDiagramSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(help_text="配置id")
    # machine_process_date = serializers.CharField(help_text="机床工作日期", max_length=32)  # 机床工作日期
    # machine_running_time = serializers.CharField(help_text="机床加工时间", max_length=32)  # 机床加工时间


# 部件树
class componentTreeSerializer(serializers.Serializer):
    machine_name = serializers.CharField(help_text="机床名称", max_length=32)  # 机床名称
    components_name = serializers.CharField(help_text="部件名称", max_length=32)  # 部件名称


# 机床信息
class machineInformationSerializer(serializers.Serializer):
    config_id = serializers.IntegerField(help_text="id")
    machine_code = serializers.CharField(help_text="机床编号", max_length=32)
    machine_name = serializers.CharField(help_text="机床名称", max_length=32)  # 机床名称
    machine_image = serializers.CharField(help_text="机床图片", max_length=255)  # 机床图片


class componentStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="id")
    component_name = serializers.CharField(help_text="部件名称", max_length=32)
    sensor_name = serializers.CharField(help_text="传感器名称", max_length=32)
    overrun_times = serializers.IntegerField(help_text="超限次数")
    operational_status = serializers.IntegerField(help_text="传感器--部件状况 0：正常（绿色）1：预警（黄色）2：异常（红色）3：损坏（红色）")

# # 设备运行状况-数据
# class equipmentDataSerializer(serializers.Serializer):
#     config_id = serializers.IntegerField(help_text="配置id")
#     temp = serializers.FloatField(help_text="温度/℃")
#     temp_min = serializers.FloatField(help_text="最小温度/℃")
#     temp_max = serializers.FloatField(help_text="最大温度/℃")
#     power = serializers.FloatField(help_text="功率/W")
#     power_min = serializers.FloatField(help_text="最小功率/W")
#     power_max = serializers.FloatField(help_text="最大功率/W")
#     acceleration = serializers.FloatField(help_text="加速度/g")
#     acceleration_min = serializers.FloatField(help_text="最小加速度/g")
#     acceleration_max = serializers.FloatField(help_text="最大加速度/g")
