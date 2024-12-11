import numpy as np
import systemConfig
import methodConfig


def TY_remaining_life(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):
    global value_d

    def JSQ_normal(x):
        a = 100.780881969348
        b = -0.188048300024243
        c = 0.000541998641975223
        d = -1.27535769883709e-06
        e = 2.0657883837544e-09
        f = -2.01619795653154e-12
        g = 1.04176234604196e-15
        h = -2.19222477293504e-19
        if 0 <= x <= 4:
            return 100
        if 4 < x <= 1498:
            return round(a + b * x + c * x ** 2 + d * x ** 3 + e * x ** 4 + f * x ** 5 + g * x ** 6 + h * x ** 7)
        if 1498 < x <= 1500:
            return 0

    def function1(a):
        aa = 0.5
        bb = np.log(4) / 100
        return aa * np.exp(bb * (100 - a))

    def function2(b):
        return 5 ** ((100 - b) / 100)

    def find_closest_index(lst, start_index, target_value):
        # 创建一个新列表，包含从start_index + 1开始的元素及其索引
        filtered_lst_with_index = [(i, val) for i, val in enumerate(lst[start_index + 1:], start=start_index + 1)]
        # 找到与目标值最接近的元素及其索引
        closest_item = min(filtered_lst_with_index, key=lambda x: (abs(x[1] - target_value), x[0]))
        # 返回最接近元素的索引
        return closest_item[0]

    x_axis_1 = list(range(0, 1501))
    y_axis_1 = []
    for i in x_axis_1:
        y_axis_1.append(JSQ_normal(i))

    sensor_id = systemConfig.models.channelConfig.objects.get(id=c1_id).sensor_id
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
        print(x1, x2)
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
