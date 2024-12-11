import os
from datetime import datetime, timedelta
import pandas as pd
import systemConfig


# 定义寿命预测算法函数--函数名需要在新增算法时“算法函数名称”对应--根据自己的需求进行修改参考文件函数名称
# 函数传入的参数个数要和新增算法时设置的“通道数量”对应
# 函数传入的参数是算法各输入通道的“通道id”
def xxxx_remaining_life(c1_id, c2_id, c3_id, c4_id, c5_id, c6_id):
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

    # 作为一个示例
    x_axis = [0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330,
              345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645,
              660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 945, 960,
              975, 990, 1005, 1020, 1035, 1050, 1065, 1080, 1095, 1110, 1125, 1140, 1155, 1170, 1185, 1200, 1215, 1230,
              1245, 1260, 1275, 1290, 1305, 1320, 1335, 1350, 1365, 1380, 1395, 1410, 1425, 1440, 1455, 1470, 1485,
              1500]
    y_pre_axis = [[0, 100], [1, 97], [2, 96], [3, 94], [4, 92], [5, 90], [6, 88], [7, 86], [8, 84], [9, 83], [10, 82],
                  [11, 80], [12, 79], [13, 77], [14, 76], [15, 76], [16, 76], [17, 75], [18, 75], [19, 75], [20, 75],
                  [21, 74], [22, 74], [23, 74], [24, 73], [25, 73], [26, 73], [27, 72], [28, 72], [29, 72], [30, 64]]
    y_last_axis = [[30, 64], [31, 64], [32, 64], [33, 63], [34, 63], [35, 63], [36, 63], [37, 62], [38, 62], [39, 61],
                   [40, 61], [41, 60], [42, 60], [43, 60], [44, 59], [45, 59], [46, 59], [47, 59], [48, 58], [49, 58],
                   [50, 58], [51, 57], [52, 57], [53, 57], [54, 56], [55, 56], [56, 56], [57, 55], [58, 55], [59, 55],
                   [60, 54], [61, 54], [62, 54], [63, 54], [64, 53], [65, 53], [66, 52], [67, 52], [68, 51], [69, 51],
                   [70, 50], [71, 49], [72, 49], [73, 48], [74, 48], [75, 47], [76, 46], [77, 46], [78, 45], [79, 44],
                   [80, 44], [81, 43], [82, 42], [83, 41], [84, 40], [85, 39], [86, 37], [87, 36], [88, 35], [89, 34],
                   [90, 32], [91, 30], [92, 29], [93, 27], [94, 24], [95, 22], [96, 19], [97, 16], [98, 12], [99, 7],
                   [100, 0]]
    life = 66
    used_day = 2000

    # 返回退化曲线X轴坐标列表（x_axis）--长度为101
    # 退化曲线中已使用寿命曲线的各点坐标（y_pre_axis）-包括当前寿命点坐标
    # 退化曲线中剩余寿命预测曲线的各点坐标（y_last_axis）-包括当前寿命点坐标
    # 当前剩余寿命值（life）
    # 部件已使用时间（used_day）
    return x_axis, y_pre_axis, y_last_axis, life, used_day
