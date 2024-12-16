import os
from datetime import datetime, timedelta
import numpy as np
import methodConfig
import systemConfig


# 定义寿命预测算法函数--函数名需要在新增算法时“算法函数名称”对应--根据自己的需求进行修改参考文件函数名称
# 函数传入的参数个数要和新增算法时设置的“通道数量”对应
# 函数传入的参数是算法各输入通道的“通道id”
def xxxx_remaining_life(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):  # 默认6个通道，前3个通道为振动传感器，后3个通道为电流传感器。
    global value_d

    # 定义正常退化时间（天）
    a = 5000

    # 定义正常退化曲线
    def SP_normal(x):
        a = 100.064466697955
        b = -2.41360515263883e-05
        c = -3.99517278969472e-06
        if 0 <= x <= 5000:
            return round(a + b * x + c * x ** 2)

    # 定义故障诊断出现预警时，剩余寿命变化值
    def function1(a):
        aa = 0.5
        bb = np.log(4) / 100
        return (aa * np.exp(bb * (100 - a))) / 2

    # 定义故障诊断出现异常时，剩余寿命变化值
    def function2(b):
        return (5 ** ((100 - b) / 100)) / 2

    def find_closest_index(lst, start_index, target_value):
        # 创建一个新列表，包含从start_index + 1开始的元素及其索引
        filtered_lst_with_index = [(i, val) for i, val in enumerate(lst[start_index + 1:], start=start_index + 1)]
        # 找到与目标值最接近的元素及其索引
        closest_item = min(filtered_lst_with_index, key=lambda x: (abs(x[1] - target_value), x[0]))
        # 返回最接近元素的索引
        return closest_item[0]

    x_axis_1 = list(range(0, a + 1))
    y_axis_1 = []
    for i in x_axis_1:
        y_axis_1.append(SP_normal(i))

        # 通过通道id查询传感器--并且读取相应传感器数据（可根据自己选择通道时选择的传感器种类--电流-振动-电流和振动）
    sensors = systemConfig.models.channelConfig.objects.filter(id__in=[c1_id, c2_id, c3_id, c4_id, c5_id, c6_id])
    s1 = None
    s2 = None
    for i in sensors:
        s = i.sensor_id
        if "电流" in systemConfig.models.sensorConfig.objects.get(id=s).sensor_name:
            s1 = s
        elif "三相加速度" in systemConfig.models.sensorConfig.objects.get(id=s).sensor_name:
            s2 = s

    sensor_id = s2
    component_id = methodConfig.models.componentSensor.objects.get(sensor_id=sensor_id).component_id
    current_life = methodConfig.models.componentConfig.objects.get(id=component_id).current_life
    record1 = methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,
                                                                          algorithm_type=1).order_by('-id').first()
    record2 = methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,

                                                                          algorithm_type=0).order_by('-id').first()

    y_pre_axis = []
    y_last_axis = []

    if record1 and record1.value4 == current_life:
        # 有历史记录
        used_day = record1.value5

        if record2 is None:
            status = 0
        else:
            status = int(record2.value2)

        value_1 = record1.value4

        if status == 0:
            value_d = value_1
        elif status == 1:
            value_d = value_1 - function1(current_life)
        elif status == 2:
            value_d = value_1 - function2(current_life)
        elif status == 3:
            value_d = 5

        middle = find_closest_index(lst=y_axis_1, start_index=used_day, target_value=value_d)
        used_day = middle
        x1 = len(eval(record1.value2))
        x2 = len(y_axis_1) - middle
        x_axis = list(range(0, x1 + x2))
        y_pre_axis = eval(record1.value2)
        y_pre_axis.append([x1, y_axis_1[middle]])
        y_last_axis.append([x1, y_axis_1[middle]])
        count = x1
        for index, value in enumerate(y_axis_1):
            if index >= middle:
                y_last_axis.append([count + 1, value])
                count += 1
    else:
        # 新部件或者第一次
        t_index = find_closest_index(lst=y_axis_1, start_index=-1, target_value=current_life)
        used_day = x_axis_1[t_index] + 1
        middle = used_day
        x_axis = x_axis_1
        for index, value in enumerate(y_axis_1):
            if index < middle + 1:
                y_pre_axis.append([index, value])
            if index >= middle:
                y_last_axis.append([index, value])

    life = y_axis_1[middle]

    return x_axis, y_pre_axis, y_last_axis, life, used_day
