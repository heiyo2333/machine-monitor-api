import os
from datetime import datetime, timedelta
import pandas as pd
import systemConfig
from dateutil import parser


# 定义故障诊断算法函数--函数名需要在新增算法时“算法函数名称”对应--根据自己的需求进行修改参考文件函数名称
# 函数传入的参数个数要和新增算法时设置的“通道数量”对应
# 函数传入的参数是算法各输入通道的“通道id”

def xxx_threshold_detection(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):  # 默认6个通道，前3个通道为振动传感器，后3个通道为电流传感器。

    # 阈值设置
    p = 3.2
    # 超限次数---部件状态码判定参数
    a = 30
    b = 100

    # 昨天的日期
    date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 查询每个通道在数据文件中字段名称（channel_field）
    channels_field = []
    for i in [c1_id, c2_id, c3_id, c4_id, c5_id, c6_id]:  # 函数传入的参数数量进行修改
        channel = systemConfig.models.channelConfig.objects.get(id=i).channel_field
        channels_field.append(channel)

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
    cur = systemConfig.models.sensorConfig.objects.get(id=s1).measurement
    vib = systemConfig.models.sensorConfig.objects.get(id=s2).measurement

    csv_1_path = f'media/Sensor/SensorData/{vib}_{date}.csv'
    csv_2_path = f'media/Sensor/SensorData/{cur}_{date}.csv'

    # 检查文件是否存在
    file_exists_1 = os.path.exists(csv_1_path)
    file_exists_2 = os.path.exists(csv_2_path)

    if file_exists_1 == 0:

        return 0, 0
    else:
        if file_exists_2 == 0:
            data1 = pd.read_csv(csv_1_path)[[channels_field[0]]]
            data2 = pd.read_csv(csv_1_path)[[channels_field[1]]]
            data3 = pd.read_csv(csv_1_path)[[channels_field[2]]]
            vib_signal = (data1.iloc[:, 0] + data2.iloc[:, 0] + data3.iloc[:, 0]) / 3


        else:
            data1 = pd.read_csv(csv_1_path)[[channels_field[0]]]
            data2 = pd.read_csv(csv_1_path)[[channels_field[1]]]
            data3 = pd.read_csv(csv_1_path)[[channels_field[2]]]
            data4 = pd.read_csv(csv_2_path)[[channels_field[3]]]
            data5 = pd.read_csv(csv_2_path)[[channels_field[4]]]
            data6 = pd.read_csv(csv_2_path)[[channels_field[5]]]

            cur_time = pd.read_csv(csv_2_path).iloc[:, 0]
            vib_time = pd.read_csv(csv_1_path).iloc[:, 0]
            cur_signal = data4.iloc[:, 0] + data5.iloc[:, 0] + data6.iloc[:, 0]
            vib_signal = (data1.iloc[:, 0] + data2.iloc[:, 0] + data3.iloc[:, 0]) / 3

            ###数据清洗##########
            # 初始化列表
            list_a = []
            list_b = []

            # 初始化首尾序号和时间
            start_index = None
            start_time = None

            for index, (time, signal) in enumerate(zip(cur_time, cur_signal)):
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
                        # 判断时间是否超过30秒
                        if time_diff > 30:
                            list_a.append(cur_time[start_index])
                            list_b.append(cur_time[end_index])
                        # 重置首序号和时间
                        start_index = None
                        start_time = None

            # 如果最后一个信号数值大于0.5，需要单独处理
            if start_index is not None:
                end_index = len(cur_time) - 1
                end_time = pd.to_datetime(cur_time[end_index])
                time_diff = (end_time - start_time).total_seconds()
                if time_diff > 30:
                    list_a.append(cur_time[start_index])
                    list_b.append(cur_time[end_index])

            # 将字符串时间转换为datetime对象
            vib_time_1 = [parser.parse(time) for time in vib_time]
            a_time = [parser.parse(time) for time in list_a]
            b_time = [parser.parse(time) for time in list_b]

            # 创建一个空列表来保存符合条件的data1中的时间
            filtered_data1 = []

            # 循环遍历列表a和b
            for start, end in zip(a_time, b_time):
                # 循环遍历data1
                for index, time in enumerate(vib_time_1):
                    # 如果时间在信号段内，则添加到filtered_data1
                    if start <= time <= end:
                        filtered_data1.append(index)

            # 只保留列表a中的索引
            vib_signal = vib_signal.loc[filtered_data1]
            # 重新设置DataFrame的索引，使其从0开始
            vib_signal.reset_index(drop=True, inplace=True)
            ###数据清洗##########

    # 阈值设置
    threshold2 = p * (vib_signal.mean())

    overrun_times = 0
    for j in vib_signal:
        if j >= threshold2:
            overrun_times += 1

    if 0 <= overrun_times < a:  # 可以定义不同类型的判定条件
        operational_status = 0  # 正常
    elif a <= overrun_times < b:
        operational_status = 1  # 预警
    else:
        operational_status = 2  # 异常

    # 需要返回超限次数（overrun_times），和部件状态码（operational_status）
    return overrun_times, operational_status
