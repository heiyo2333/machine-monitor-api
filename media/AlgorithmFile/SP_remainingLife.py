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


def SP_remaining_life(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):
    sensor_id = systemConfig.models.channelConfig.objects.get(id=c1_id).sensor_id
    component_id = methodConfig.models.componentSensor.objects.get(sensor_id=sensor_id).component_id
    current_life = methodConfig.models.componentConfig.objects.get(id=component_id).current_life
    record1 =  methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,algorithm_type = 1).order_by('-id').first()
    record2 =  methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,algorithm_type = 0).order_by('-id').first()
    date_gap = datetime.now().date()-record1.date
    status = record2.value2

    global value2

    x_axis = list(range(0, 5001, 50))
    y_axis = [100, 100, 100, 100, 100, 100, 100, 100, 99, 99, 99, 99, 99, 98, 98, 98, 97, 97, 97, 96, 96, 96, 95, 95,
              94, 94, 93, 93, 92, 92, 91, 90, 90, 89, 88, 88, 87, 86, 86, 85, 84, 83, 82, 82, 81, 80, 79, 78, 77, 76,
              75, 74, 73, 72, 71, 70, 69, 68, 66, 65, 64, 63, 62, 60, 59, 58, 56, 55, 54, 52, 51, 50, 48, 47, 45, 44,
              42, 41, 39, 38, 36, 34, 33, 31, 29, 28, 26, 24, 23, 21, 19, 17, 15, 14, 12, 10, 8, 6, 4, 2, 0]

    def function1(a):
        aa = 0.5
        bb = np.log(4) / 100
        return aa * np.exp(bb * (100 - a))/2

    def function2(b):
        return 5 ** ((100 - b) / 100)/2

    index1 = y_axis.index(current_life) + round(date_gap / 50)
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





