import os
import sys
from datetime import datetime
import django
import numpy as np




# 添加项目路径到 sys.path
project_path = r'D:\machine-monitor-api'
sys.path.append(project_path)

# 设置 Django 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MachineMonitorApi.settings')
django.setup()

import systemConfig
import methodConfig


def TX_remaining_life(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):
    sensor_id = systemConfig.models.channelConfig.objects.get(id=c1_id).sensor_id
    component_id = methodConfig.models.componentSensor.objects.get(sensor_id=sensor_id).component_id
    current_life = methodConfig.models.componentConfig.objects.get(id=component_id).current_life
    record1 =  methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,algorithm_type = 1).order_by('-id').first()
    record2 =  methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,algorithm_type = 0).order_by('-id').first()
    date_gap = datetime.now().date()-record1.date
    status = record2.value2

    global value2

    x_axis = list(range(0, 1501, 15))
    y_axis = [100, 97, 96, 94, 92, 90, 88, 86, 84, 83, 82, 80, 79, 77, 76, 75, 74, 73, 72, 72, 71, 70, 70, 69, 69, 68,
              67, 67, 66, 66, 66, 65, 65, 64, 64, 63, 63, 62, 62, 61, 61, 60, 60, 60, 59, 59, 59, 59, 58, 58, 58, 57,
              57, 57, 56, 56, 56, 55, 55, 55, 54, 54, 54, 54, 53, 53, 52, 52, 51, 51, 50, 49, 49, 48, 48, 47, 46, 46,
              45, 44, 44, 43, 42, 41, 40, 39, 37, 36, 35, 34, 32, 30, 29, 27, 24, 22, 19, 16, 12, 7, 0]

    def function1(a):
        aa = 0.5
        bb = np.log(4) / 100
        return aa * np.exp(bb * (100 - a))

    def function2(b):
        return 5 ** ((100 - b) / 100)

    index1 = y_axis.index(current_life) + round(date_gap / 15)
    value1 = y_axis[index1]

    if status == 0:
        middle = index1
    elif status == 1:
        value2 = value1 - function1(current_life)
        min_diff = float('inf')
        min_index = -1
        for i in range(index1, len(y_axis)):
            diff = abs(y_axis[i] - value2)
            if diff < min_diff:
                min_diff = diff
                min_index = i
        middle = min_index
    elif status == 2:
        value2 = value1 - function2(current_life)
        min_diff = float('inf')
        min_index = -1
        for i in range(index1, len(y_axis)):
            diff = abs(y_axis[i] - value2)
            if diff < min_diff:
                min_diff = diff
                min_index = i
        middle = min_index

    y_pre_axis = []
    y_last_axis = []

    for index, value in enumerate(y_axis):
        if index < middle + 1:
            y_pre_axis.append([index, value])
        if index >= middle:
            y_last_axis.append([index, value])

    life = y_axis[middle]

    return x_axis, y_pre_axis, y_last_axis, life





