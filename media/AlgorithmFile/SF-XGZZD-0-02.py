import os
from datetime import datetime, timedelta
import pandas as pd
import systemConfig


def XG_threshold_detection(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):
    # date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    date = "2024-10-21"
    sensors = systemConfig.models.channelConfig.objects.filter(id__in=[c1_id, c2_id, c3_id, c4_id, c5_id, c6_id])
    s1 = None
    s2 = None
    for i in sensors:
        s = i.sensor_id
        if "电流" in systemConfig.models.sensorConfig.objects.get(id=s).sensor_name:
            s1 = s
        elif "三相加速度" in systemConfig.models.sensorConfig.objects.get(id=s).sensor_name:
            s2 = s
    cur = systemConfig.models.sensorConfig.objects.get(id=s1).measurement
    vib = systemConfig.models.sensorConfig.objects.get(id=s2).measurement

    c1 = 7
    c2 = 10
    p = 1.75

    csv_1_path = f'media/Sensor/SensorData/{cur}_{date}.csv'
    csv_2_path = f'media/Sensor/SensorData/{vib}_{date}.csv'

    # 检查文件是否存在
    file_exists_1 = os.path.exists(csv_1_path)
    file_exists_2 = os.path.exists(csv_2_path)

    if file_exists_2 == 0:
        return 0, 0
    else:
        if file_exists_1 == 0:

            csv_2 = pd.read_csv(csv_2_path)

        else:
            csv_1 = pd.read_csv(csv_1_path)
            csv_2 = pd.read_csv(csv_2_path)

            data1 = csv_1.iloc[:, 0]
            data2 = csv_1.iloc[:, 1:4].sum(axis=1)
            data3 = csv_2.iloc[:, 0]

            # 初始化列表
            list_a = []
            list_b = []

            # 初始化首尾序号和时间
            start_index = None
            start_time = None

            for index, (time, signal) in enumerate(zip(data1, data2)):
                # 将时间字符串转换为datetime对象
                time = pd.to_datetime(time)

                # 检测信号数值大于0.5的
                if signal > 0.5:
                    if start_index is None:
                        # 记录首序号和时间
                        start_index = index
                        start_time = time
                else:
                    if start_index is not None:
                        # 记录尾序号
                        end_index = index - 1
                        # 计算时间差
                        time_diff = (time - start_time).total_seconds()
                        # 判断时间是否超过10秒
                        if time_diff > 30:
                            list_a.append(data1[start_index])
                            list_b.append(data1[end_index])
                        # 重置首序号和时间
                        start_index = None
                        start_time = None

            # 如果最后一个信号数值大于0.5，需要单独处理
            if start_index is not None:
                end_index = len(data1) - 1
                end_time = pd.to_datetime(data1[end_index])
                time_diff = (end_time - start_time).total_seconds()
                if time_diff > 30:
                    list_a.append(data1[start_index])
                    list_b.append(data1[end_index])

            # 将字符串时间转换为datetime对象
            data3_time = [datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ") for time in data3]
            a_time = [datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ") for time in list_a]
            b_time = [datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ") for time in list_b]

            # 创建一个空列表来保存符合条件的data1中的时间
            filtered_data1 = []

            # 循环遍历列表a和b
            for start, end in zip(a_time, b_time):
                # 循环遍历data1
                for index, time in enumerate(data3_time):
                    # 如果时间在信号段内，则添加到filtered_data1
                    if start <= time <= end:
                        filtered_data1.append(index)

            # 只保留列表a中的索引
            csv_2 = csv_2.loc[filtered_data1]
            # 重新设置DataFrame的索引，使其从0开始
            csv_2.reset_index(drop=True, inplace=True)

        data = csv_2.iloc[:, c1:c2].mean(axis=1)
        threshold2 = (1 + p) * (data.mean())
        overrun_times = 0
        for j in data:
            if j >= threshold2:
                overrun_times += 1

        if 0 <= overrun_times < 30:
            operational_status = 0
        elif 30 <= overrun_times < 100:
            operational_status = 1
        else:
            operational_status = 2

        return overrun_times, operational_status
