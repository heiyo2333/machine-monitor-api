# -*- coding: utf-8 -*-
"""
File Name: test_sensors

Author: swjtu
Date: 2024/08/31
"""
import struct
from influxdb import InfluxDBClient
import socket
import threading
import time

# 全局变量和锁
count_vibrate = 0
lock = threading.Lock()


def detect_vibrate(sensoe_number, port, command_code, measurement):
    global count_vibrate
    response_temp = b''
    client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin',
                            database=database_name)
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(time_out)
            client_socket.connect((ip, port))
            print(f"成功连接到 {ip}:{port}")
            while True:
                try:
                    client_socket.sendall(command_code)
                    time.sleep(0.15)
                    response = client_socket.recv(46)
                    if response == response_temp:
                        continue
                    response_temp = response
                    # print('response', response.hex())
                    # 从响应中提取数据部分 (跳过前面3个字节: 从站地址、功能码、字节数;) # -2是为了去掉最后的CRC校验
                    data_section = response[3:-2]
                    # 每两个字节表示一个寄存器的值
                    registers = struct.unpack('>9H', data_section)  # '>'表示大端，'9H'表示9个无符号短整型数
                    # 将寄存器的值存储在一个列表中
                    registers_list = list(registers)
                    scaled_registers_list = [value / 100 for value in registers_list]
                    # 打印除以10后的寄存器列表
                    print("第", sensoe_number, '个传感器', scaled_registers_list)
                    point = [
                        {
                            'measurement': measurement,
                            'fields': {
                                'AcceleratedSpeed_X': scaled_registers_list[0],
                                'AcceleratedSpeed_Y': scaled_registers_list[1],
                                'AcceleratedSpeed_Z': scaled_registers_list[2],
                                'StandardDeviation_X': scaled_registers_list[3],
                                'StandardDeviation_Y': scaled_registers_list[4],
                                'StandardDeviation_Z': scaled_registers_list[5],
                                'RMS_X': scaled_registers_list[6],
                                'RMS_Y': scaled_registers_list[7],
                                'RMS_Z': scaled_registers_list[8],
                            }

                        }]
                    client.write_points(point)

                except Exception as e:
                    print(f"发生错误: {e}")
                    continue

        except socket.error as e:
            print(f"无法连接到 {ip}:{port}，错误信息：{e}")
            time.sleep(0.5)  # 重试前等待一段时间

        finally:
            client_socket.close()


# def detect_current(sensoe_number, port, command_current, measurement):
#     global count_current
#     response_temp = b''
#     while True:
#         try:
#             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             client_socket.settimeout(time_out)
#             client_socket.connect((ip, port))
#             print(f"成功连接到 {ip}:{port}")
#             while True:
#                 try:
#                     client_socket.sendall(command_current)
#                     time.sleep(0.15)
#                     response = client_socket.recv(34)
#                     if response == response_temp:
#                         continue
#
#                     response_temp = response
#                     # print('response', response.hex())
#                     # 从响应中提取数据部分 (跳过前面3个字节: 从站地址、功能码、字节数;) # -2是为了去掉最后的CRC校验
#                     data_section = response[3:-2]
#                     # 每两个字节表示一个寄存器的值
#                     registers = struct.unpack('>3I', data_section)  # '>'表示大端，'9H'表示9个无符号短整型数
#                     # 将寄存器的值存储在一个列表中
#                     registers_list = list(registers)
#                     scaled_registers_list = [value / 100 for value in registers_list]
#                     # 打印除以10后的寄存器列表
#                     print("第", sensoe_number, '个传感器', scaled_registers_list)
#                     point = [
#                         {
#                             'measurement': measurement,
#                             'fields': field_dict
#                         }]
#                     client.write_points(point)
#
#                 except Exception as e:
#                     print(f"发生错误: {e}")
#                     continue
#
#         except socket.error as e:
#             print(f"无法连接到 {ip}:{port}，错误信息：{e}")
#             time.sleep(0.5)  # 重试前等待一段时间
#
#         finally:
#             client_socket.close()


def start_sensor_threads(sensors):
    threads = []
    for sensor in sensors:
        t = threading.Thread(target=detect_vibrate, args=(sensor['sensor_number'],
                                                          sensor['port'],
                                                          sensor['command_code'],
                                                          sensor['measurement']))
        t.start()
        threads.append(t)

    # 等待所有线程完成
    for t in threads:
        t.join()


# def write_influxdb(data):
#     point_vibrate = [
#         {
#             'measurement': 'signal',
#             'fields':  # 字段
#                 {
#                     'fields1_power': round(data[x], 2),  # 字段：振动烈度
#                     'fields2_vibration_x': round(data2[y], 2),  # 字段：X方向振动
#                     'fields3_vibration_y': round(data3[y], 2),  # 字段：Y方向振动
#                     'fields4_vibration_z': round(data4[y], 2),  # 字段：Z方向振动
#                 }
#         }]
#     client.write_points(point_vibrate)

# 创建数据库
def create_database(client_temp, new_database):
    client_temp.create_database(new_database)


# 连接时序数据库
def connect_database(client, database_name):
    # 获取所有数据库的列表
    database_list = client.get_list_database()
    print('现有数据库列表', database_list)

    # 检查是否存在名为 'database_name' 的数据库
    if any(db['name'] == database_name for db in database_list):
        exist_flag = 1
    else:
        print(f"数据库 '{database_name}' 不存在。")
        exist_flag = 0
    return exist_flag


if __name__ == '__main__':
    #  #### 配置时序数据库 #######

    database_name = 'testdata'  # 时序数据库名称
    client_temp = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin')
    exist_flag = connect_database(client_temp, database_name)
    if exist_flag == 0:  # 如果没有这个数据库，则创建它
        create_database(client_temp, database_name)
    else:
        print(f'连接到时序数据库：', database_name)
    client_temp.close()

    # 创建具体的数据库'database_name'对象

    ip = "192.168.1.253"
    time_out = 1  # 增加超时时间
    recv_num = 27

    # 添加其他传感器的IP和端口0
    sensors = [
        {"sensor_number": 1, "port": 1030, "command_code": bytearray.fromhex("01 03 A6 04 00 09 E6 85"),
         'measurement': 'signal1'},
        {"sensor_number": 2, "port": 1031, "command_code": bytearray.fromhex("01 03 A6 04 00 09 E6 85"),
         'measurement': 'signal2'},
        {"sensor_number": 3, "port": 1032, "command_code": bytearray.fromhex("01 03 A6 04 00 09 E6 85"),
         'measurement': 'signal3'},
        {"sensor_number": 4, "port": 1033, "command_code": bytearray.fromhex("01 03 A6 04 00 09 E6 85"),
         'measurement': 'signal4'},
        {"sensor_number": 5, "port": 1034, "command_code": bytearray.fromhex("01 03 A6 04 00 09 E6 85"),
         'measurement': 'signal5'},
        {"sensor_number": 6, "port": 1035, "command_code": bytearray.fromhex("01 03 A6 04 00 09 E6 85"),
         'measurement': 'signal6'},
        {"sensor_number": 7, "port": 1036, "command_code": bytearray.fromhex("01 03 A6 04 00 09 E6 85"),
         'measurement': 'signal7'},
        {"sensor_number": 8, "port": 1037, "command_code": bytearray.fromhex("01 03 A6 04 00 09 E6 85"),
         'measurement': 'signal8'},
        # {"sensor_number": 9, "port": 1038, "command": bytearray.fromhex("01 03 00 01 00 06 94 08")},
        # {"sensor_number": 1, "port": 1030, "command": bytearray.fromhex("AB")},# 改波特率`1
    ]

    start_sensor_threads(sensors)
