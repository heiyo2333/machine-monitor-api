import os
from datetime import datetime, timedelta
import pandas as pd
import systemConfig


# 定义故障诊断算法函数--函数名需要在新增算法时“算法函数名称”对应--根据自己的需求进行修改参考文件函数名称
# 函数传入的参数个数要和新增算法时设置的“通道数量”对应
# 函数传入的参数是算法各输入通道的“通道id”
def xxxx_threshold_detection(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):
    # 昨天的日期
    date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 查询每个通道在数据文件中字段名称（channel_field）
    channel_field = []
    for i in [c1_id, c2_id, c3_id, c4_id, c5_id, c6_id]:  # 函数传入的参数数量进行修改
        channel = systemConfig.models.channelConfig.objects.get(id=i)
        channel_field.append(channel)

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

    csv_1_path = f'media/Sensor/SensorData/{cur}_{date}.csv'
    csv_2_path = f'media/Sensor/SensorData/{vib}_{date}.csv'

    data1 = pd.read_csv(csv_1_path)[[channel_field[0]]]
    data2 = pd.read_csv(csv_1_path)[[channel_field[1]]]
    data3 = pd.read_csv(csv_1_path)[[channel_field[2]]]
    data4 = pd.read_csv(csv_2_path)[[channel_field[3]]]
    data5 = pd.read_csv(csv_2_path)[[channel_field[4]]]
    data6 = pd.read_csv(csv_2_path)[[channel_field[5]]]
    # pd.read_csv(path:根据传感器类型选择对应的path)[column_name:根据在channel_field这个列表中对应的索引进行选择]]

    # 添加自己的算法代码

    overrun_times = 0

    if 0 <= overrun_times < 30:  # 可以定义不同类型的判定条件
        operational_status = 0  # 正常
    elif 30 <= overrun_times < 100:
        operational_status = 1  # 预警
    else:
        operational_status = 2  # 异常

    # 需要返回超限次数（overrun_times），和部件状态码（operational_status）
    return overrun_times, operational_status
