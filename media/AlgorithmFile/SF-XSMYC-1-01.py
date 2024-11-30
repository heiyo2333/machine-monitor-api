from datetime import datetime
import numpy as np
import systemConfig
import methodConfig


def XM_remaining_life(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):
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

    def find_closest_index(lst, start_index, target_value):
        filtered_lst = lst[start_index + 1:]
        relative_closest_index = min(range(len(filtered_lst)), key=lambda i: abs(filtered_lst[i] - target_value))
        target_index = start_index + 1 + relative_closest_index
        return target_index

    sensor_id = systemConfig.models.channelConfig.objects.get(id=c1_id).sensor_id
    component_id = methodConfig.models.componentSensor.objects.get(sensor_id=sensor_id).component_id
    current_life = methodConfig.models.componentConfig.objects.get(id=component_id).current_life
    record1 = methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,
                                                                          algorithm_type=1).order_by('-id').first()
    record2 = methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,

                                                                    algorithm_type=0).order_by('-id').first()
    t_index = find_closest_index(lst=y_axis, start_index=-1, target_value=current_life)
    if record1 and record1.value4 == current_life:
        date1 = datetime.strptime(record1.date, "%Y-%m-%d").date()
        d_gap = datetime.now().date() - date1
        date_gap = int(d_gap.days)
        used_day = record1.value5 + date_gap
    else:
        used_day = x_axis[t_index] + 1

    if record2 is None:
        status = 0
    else:
        status = int(record2.value2)

    value_1 = y_axis[round(used_day // 15)]

    if status == 0:
        value_d = value_1
    elif status == 1:
        value_d = value_1 - function1(current_life)
    elif status == 2:
        value_d = value_1 - function2(current_life)

    middle = find_closest_index(lst=y_axis, start_index=t_index, target_value=value_d)

    y_pre_axis = []
    y_last_axis = []

    for index, value in enumerate(y_axis):
        if index < middle + 1:
            y_pre_axis.append([index, value])
        if index >= middle:
            y_last_axis.append([index, value])

    life = y_axis[middle]

    return x_axis, y_pre_axis, y_last_axis, life, used_day
