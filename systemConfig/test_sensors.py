# -*- coding: utf-8 -*-
"""
File Name: test_sensors

Author: swjtu
Date: 2024/08/31
"""
import subprocess
import struct
import os
import sys

import django
import requests
from influxdb import InfluxDBClient
import socket
import threading
import time


# 添加项目路径到 sys.path
project_path = r'D:\machine-monitor-api'
sys.path.append(project_path)

# 设置 Django 环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MachineMonitorApi.settings')  # 请将 'your_project_name' 替换为你的项目名
django.setup()

lock = threading.Lock()

import systemConfig
from systemConfig import models

def thread_flag_clean():
    sensors = systemConfig.models.sensorConfig.objects.all()
    for m in sensors:
        m.thread_flag = 0
        m.save()


def sensor_detect(client, sensor_list):
    sensor_id = sensor_list['sensor_id']
    error_time = 0
    max_retries = 10
    response_temp = b''
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(sensor_list['time_out'])
            client_socket.connect((machine_ip, sensor_list['sensor_port']))
            print(f"成功连接到 {machine_ip}:{sensor_list['sensor_port']}")
            break
        except socket.error as e:
            error_time = error_time + 1
            print(f"第{error_time}次错误：无法连接到 {machine_ip}:{sensor_list['sensor_port']}，错误信息：{e}")
            if error_time > max_retries:
                sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
                sensor.sensor_status = 0
                sensor.save()
                return
            time.sleep(0.5)  # 重试前等待一段时间

    while True:
        try:
            sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
            # 如果传感器字段：thread_flag为0，结束该检测线程
            if sensor.thread_flag == 0:
                client_socket.close()
                return
            client_socket.sendall(sensor_list['command_code'])
            time.sleep(0.15)
            response = client_socket.recv(sensor_list['receive_number'])
            # 如果此次数据和上次一致，忽略此次
            if response == response_temp:
                continue
            response_temp = response
            # print('response', response.hex())
            # 从响应中提取数据部分 (跳过前面3个字节: 从站地址、功能码、字节数;) # -2是为了去掉最后的CRC校验
            data_section = response[3:-2]
            # 根据传感器字敦：ruler，将data_section划分成对应数量的数值
            registers = struct.unpack(sensor_list['ruler'], data_section)  # '>'表示大端，'9H'表示9个无符号短整型数
            # 将寄存器的值存储在一个列表中
            registers_list = list(registers)
            scaled_registers_list = [value / 100 for value in registers_list]
            # 打印除以10后的寄存器列表
            print("第", sensor_id, '个传感器', scaled_registers_list)
            field_dict = {}
            for field, value in zip(sensor_list['field_list'], scaled_registers_list):
                field_dict[field] = value
            point = [
                {
                    'measurement': sensor_list['measurement'],
                    'fields': field_dict
                }]
            client.write_points(point)
            # 按照传感器频率延迟对应的时间
            time.sleep(1 / sensor_list['frequency'])
            error_time = 0
        # 传感器数据解析错误
        except struct.error as e:
            error_time += 1
            print(f"第{error_time}次错误：传感器 {sensor_id} 数据解析错误：{e}")
            if error_time > max_retries:
                return
            time.sleep(0.5)  # 重试前等待一段时间
        # 传感器网络错误
        except socket.error as e:
            print(f"第{error_time}次错误：传感器 {sensor_id} 网络错误：{e}")
            error_time += 1
            wait_for_influxdb()
            if error_time > max_retries:
                sensor.sensor_status = 0
                sensor.save()
                return
            time.sleep(0.5)  # 重试前等待一段时间
        # 其他错误
        except Exception as e:
            error_time = error_time + 1
            print(f"第{error_time}次错误：无法连接到 {machine_ip}:{sensor_list['sensor_port']}，错误信息：{e}")
            if error_time > max_retries:
                return
            time.sleep(0.5)  # 重试前等待一段时间


# 开启多线程，一个传感器一个线程
def start_sensor_threads(detect_list):
    threads = []
    for y in detect_list:
        sensor_id = y['sensor_id']
        sensor = models.sensorConfig.objects.get(id=sensor_id)
        sensor.thread_flag = True
        sensor.save()
        t = threading.Thread(target=sensor_detect, args=(client, y))
        t.start()
        threads.append(t)

    # 等待所有线程完成
    for t in threads:
        t.join()


# 创建数据库
def create_database(client_temp, new_database):
    client_temp.create_database(new_database)


# 连接时序数据库：database_name
def connect_database(database_name):
    # 获取所有数据库的列表
    client_temp = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin')
    database_list = client_temp.get_list_database()
    print('现有数据库列表', database_list)

    # 检查是否存在名为 'database_name' 的数据库
    if any(db['name'] == database_name for db in database_list):
        exist_flag = 1
    else:
        exist_flag = 0

    if exist_flag == 0:  # 如果没有这个数据库，则创建它
        create_database(client_temp, database_name)
    else:
        print(f'连接到时序数据库：', database_name)
    # 关闭该连接
    client_temp.close()
    return


# 等待时序数据库服务连接验证
def wait_for_influxdb():
    retry_count = 0
    max_retries = 10  # 设置最大重试次数
    flag = 1

    # 使用全局锁，确保只有一个线程可以进入
    with lock:
        while retry_count < max_retries:
            try:
                # 发送一个简单的请求到 InfluxDB 的 Ping 端点
                response = requests.get('http://localhost:8086/ping')
                if response.status_code == 204:
                    return flag
                else:
                    print("InfluxDB is not responding correctly.")
            except requests.exceptions.ConnectionError as e:
                print(f"Connection Error: {e}")
                # 如果连接错误，尝试启动 InfluxDB
                print("Trying to start InfluxDB...")
                start_influxdb()
                retry_count += 1
                time.sleep(0.5)  # 等待一段时间后重试
            except Exception as e:
                print(f"An error occurred: {e}")
                retry_count += 1
                time.sleep(0.5)  # 等待一段时间后重试
        flag = 0
    return flag


def start_influxdb():
    try:
        # 尝试启动 InfluxDB
        subprocess.run(
            ["cmd", "/c", "start", "/min", "cmd", "/c",
             "D:\\influx\\influxdb\\influxdb-1.8.10-1\\influxd -config "
             "D:\\influx\\influxdb\\influxdb-1.8.10-1\\influxdb.conf"],
            check=True
        )
        print("InfluxDB is starting...")
        # 增加等待时间
        time.sleep(5)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start InfluxDB: {e}")


# 查找时序数据库名称和串口服务器ip
def get_influxdb_name():
    retry_count = 0
    max_retries = 10  # 设置最大重试次数
    flag = 1
    while retry_count < max_retries:
        try:
            machines = systemConfig.models.systemConfig.objects.filter(is_apply=1)
            if not machines.exists():
                print("没有正在应用的机床")
                continue
            name = machines.first().database_name
            ip = machines.first().machine_ip
            return flag, name, ip
        except Exception as e:
            print(f"获取机床信息时发生错误：{e}")
            retry_count += 1
            time.sleep(0.5)  # 等待一段时间后重试
    flag = 0
    return flag, retry_count, max_retries  # 后两个没用


# 定义传感器检测的列表信息
def define_sensor_list():
    retry_count = 0
    max_retries = 10  # 设置最大重试次数
    while retry_count < max_retries:
        try:
            sensors = systemConfig.models.sensorConfig.objects.filter(sensor_status=1).order_by('id')

            if not sensors.exists():
                print('请检查传感器状态或是否配置')
                retry_count += 1
                time.sleep(0.5)  # 等待一段时间后重试
                continue

            detect_list = []
            for sensor in sensors:
                sensor_id = sensor.id
                field_list = []

                channels = systemConfig.models.channelConfig.objects.filter(channel_id=sensor_id).order_by('id')
                if not channels.exists():
                    print(f"传感器 {sensor_id} 没有配置通道")
                    retry_count += 1
                    time.sleep(0.5)  # 等待一段时间后重试
                    continue
                for H in channels:
                    field_list.append(H.channel_field)  # 将 field 拼接到 field_list 中
                sensor_list = {
                    'sensor_id': sensor.id,
                    'sensor_port': sensor.sensor_port,  # 假设传感器的Modbus端口
                    'frequency': sensor.frequency,
                    'command_code': bytearray.fromhex(sensor.command_code),  # 这是一个示例的Modbus指令
                    'ruler': sensor.ruler,
                    'time_out': sensor.time_out,  # 5秒超时
                    'receive_number': sensor.receive_number,  # 预期接收46个字节
                    'measurement': sensor.measurement,
                    'field_list': field_list}
                detect_list.append(sensor_list)
            return 1, detect_list
        except Exception as e:
            print(f"定义传感器列表时发生错误：{e}")
            retry_count += 1
            time.sleep(0.5)  # 等待一段时间后重试
    return 0, []  # 后两个没用


if __name__ == '__main__':
    thread_flag_clean()
    # 检测时序数据库的服务是否打开，如果没有打开就在内部循环
    flag_a = wait_for_influxdb()
    if flag_a == 1:
        # 获取时序数据库名称和机床ip
        flag_b, influxdb_name, machine_ip = get_influxdb_name()
        if flag_b == 1:
            # 连接该时序数据库，如果没有这个数据库，则创建它
            connect_database(influxdb_name)
            # 定义传感器信息
            flag_c, detect_list = define_sensor_list()
            if flag_c == 1:
                client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin',
                                        database=influxdb_name)
                # 开启多线程检测
                start_sensor_threads(detect_list)

    thread_flag_clean()
    os._exit(0)
