import json
import random
import time
import struct
import numpy as np
from django.db.models import Q, Max
from django.http import JsonResponse
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from influxdb import InfluxDBClient
from rest_framework.decorators import action
from datetime import datetime, timedelta
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
import socket
import methodConfig
import systemConfig
from methodConfig.views import get_local_ip
from . import models, serializer
from .models import thermalDiagram
import threading

# class DatabaseManager:
#     def __init__(self):
#         influxdb_ip = 'localhost'  # 时序数据库ip：默认用本地
#         influxdb_port = 8086  # InfluxDB 服务器的端口，默认是 8086
#         username = 'admin'  # 可选，如果设置了用户名和密码
#         password = 'admin'  # 可选，如果设置了用户名和密码
#         client = InfluxDBClient(host=influxdb_ip, port=influxdb_port, username=username, password=password)
#         self.client = client
#
#     def createDatabase(self, new_database):
#         self.client.create_database(new_database)
#
#     def connect_database(self, database_name):
#         # 获取所有数据库的列表
#         database_list = self.client.get_list_database()
#         print('现有数据库列表:', database_list)
#
#         # 检查是否存在名为 'database_name' 的数据库
#         if any(db['name'] == database_name for db in database_list):
#             print(f"数据库 '{database_name}' 已存在。")
#         else:
#             print(f"数据库 '{database_name}' 不存在，正在创建数据库。")
#             self.createDatabase(database_name)
#
#     def detect_sensor(self, ip, sensor_id, sensor_port, command_vibrate, time_out, receive_number, measurement, field_list):
#         response_temp = b''
#         while True:
#             sensor = systemConfig.models.sensorConfig.objects.filter(id=sensor_id)
#             if sensor.exists():
#                 thread_flag = sensor.first().thread_flag
#                 if thread_flag == 0:
#                     break
#             else:
#                 return
#             try:
#                 client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#                 client_socket.settimeout(time_out)
#                 client_socket.connect((ip, sensor_port))
#                 print(f"成功连接到 {ip}:{sensor_port}")
#                 while True:
#                     try:
#                         client_socket.sendall(command_vibrate)
#                         time.sleep(0.15)
#                         response = client_socket.recv(receive_number)
#                         if response == response_temp:
#                             continue
#                         response_temp = response
#                         # 从响应中提取数据部分 (跳过前面3个字节: 从站地址、功能码、字节数;) # -2是为了去掉最后的CRC校验
#                         data_section = response[3:-2]
#                         # 每两个字节表示一个寄存器的值
#                         if receive_number == 46:
#                             registers = struct.unpack('>9H', data_section)  # '>'表示大端，'9H'表示9个无符号短整型数
#                             # 将寄存器的值存储在一个列表中
#                             registers_list = list(registers)
#                             scaled_registers_list = [value / 100 for value in registers_list]
#                         else:
#                             registers = struct.unpack('>3I', data_section)  # '>'表示大端，'3I'表示3个无符号短整型数
#                             # 将寄存器的值存储在一个列表中
#                             registers_list = list(registers)
#                             scaled_registers_list = [value / 100 for value in registers_list]
#
#                         field_dict = {}
#                         for field, value in zip(field_list, scaled_registers_list):
#                             field_dict[field] = value
#                         point = [
#                             {
#                                 'measurement': measurement,
#                                 'fields': field_dict
#                             }]
#                         self.client.write_points(point)
#                     except Exception as e:
#                         print(f"发生错误: {e}")
#                         continue
#             except socket.error as e:
#                 print(f"无法连接到 {ip}:{sensor_port}，错误信息：{e}")
#                 time.sleep(0.5)  # 重试前等待一段时间
#
#             finally:
#                 client_socket.close()
#
#     def start_sensor_threads(self, sensors, ip):
#         threads = []
#         for sensor in sensors:
#             t = threading.Thread(target=self.detect_sensor,
#                                  args=(ip,
#                                        sensor['sensor_id'],
#                                        sensor['sensor_port'],
#                                        sensor['command_code'],
#                                        sensor['time_out'],
#                                        sensor['receive_number'],
#                                        sensor['measurement'],
#                                        sensor['field_list'])
#                                  )
#             t.start()
#             threads.append(t)
def detect_sensor(client, ip, sensor_id, sensor_port, command_code, time_out, receive_number, measurement, field_list):
    response_temp = b''
    while True:
        sensor = systemConfig.models.sensorConfig.objects.filter(id=sensor_id)
        if sensor.exists():
            thread_flag = sensor.first().thread_flag
            if thread_flag == 0:
                break
        else:
            return
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(time_out)
            client_socket.connect((ip, sensor_port))
            print(f"成功连接到 {ip}:{sensor_port}")
            while True:
                try:
                    client_socket.sendall(command_code)
                    time.sleep(0.15)
                    response = client_socket.recv(receive_number)
                    if response == response_temp:
                        continue
                    response_temp = response
                    # 从响应中提取数据部分 (跳过前面3个字节: 从站地址、功能码、字节数;) # -2是为了去掉最后的CRC校验
                    data_section = response[3:-2]
                    # 每两个字节表示一个寄存器的值
                    if receive_number == 46:
                        registers = struct.unpack('>9H', data_section)  # '>'表示大端，'9H'表示9个无符号短整型数
                        # 将寄存器的值存储在一个列表中
                        registers_list = list(registers)
                        scaled_registers_list = [value / 100 for value in registers_list]
                    else:
                        registers = struct.unpack('>3I', data_section)  # '>'表示大端，'3I'表示3个无符号短整型数
                        # 将寄存器的值存储在一个列表中
                        registers_list = list(registers)
                        scaled_registers_list = [value / 100 for value in registers_list]
                        print('scaled_registers_list', scaled_registers_list)

                    field_dict = {}
                    for field, value in zip(field_list, scaled_registers_list):
                        field_dict[field] = value
                    point = [
                        {
                            'measurement': measurement,
                            'fields': field_dict
                        }]
                    client.write_points(point)
                except Exception as e:
                    print(f"发生错误: {e}")
                    continue
        except socket.error as e:
            print(f"无法连接到 {ip}:{sensor_port}，错误信息：{e}")
            time.sleep(0.5)  # 重试前等待一段时间

        finally:
            client_socket.close()


def createDatabase(client, new_database):
    client.create_database(new_database)
    return


def connect_database(database_name):
    influxdb_ip = 'localhost'  # 时序数据库ip：默认用本地
    influxdb_port = 8086  # InfluxDB 服务器的端口，默认是 8086
    username = 'admin'  # 可选，如果设置了用户名和密码
    password = 'admin'  # 可选，如果设置了用户名和密码
    client_temp = InfluxDBClient(host=influxdb_ip, port=influxdb_port, username=username, password=password)
    # 获取所有数据库的列表
    database_list = client_temp.get_list_database()
    print('现有数据库列表:', database_list)

    # 检查是否存在名为 'database_name' 的数据库
    if any(db['name'] == database_name for db in database_list):
        print(f"数据库 '{database_name}' 已存在。")
    else:
        print(f"数据库 '{database_name}' 不存在，正在创建数据库。")
        createDatabase(client_temp, database_name)
    client_temp.close()
    return

    # def detect_sensor(self, ip, sensor_id, sensor_port, command_code, time_out, receive_number, measurement, field_list):
    #     response_temp = b''
    #     while True:
    #         sensor = systemConfig.models.sensorConfig.objects.filter(id=sensor_id)
    #         if sensor.exists():
    #             thread_flag = sensor.first().thread_flag
    #             if thread_flag == 0:
    #                 break
    #         else:
    #             return
    #         try:
    #             client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #             client_socket.settimeout(time_out)
    #             client_socket.connect((ip, sensor_port))
    #             print(f"成功连接到 {ip}:{sensor_port}")
    #             while True:
    #                 try:
    #                     client_socket.sendall(command_code)
    #                     time.sleep(0.15)
    #                     response = client_socket.recv(receive_number)
    #                     if response == response_temp:
    #                         continue
    #                     response_temp = response
    #                     # 从响应中提取数据部分 (跳过前面3个字节: 从站地址、功能码、字节数;) # -2是为了去掉最后的CRC校验
    #                     data_section = response[3:-2]
    #                     # 每两个字节表示一个寄存器的值
    #                     if receive_number == 46:
    #                         registers = struct.unpack('>9H', data_section)  # '>'表示大端，'9H'表示9个无符号短整型数
    #                         # 将寄存器的值存储在一个列表中
    #                         registers_list = list(registers)
    #                         scaled_registers_list = [value / 100 for value in registers_list]
    #                     else:
    #                         registers = struct.unpack('>3I', data_section)  # '>'表示大端，'3I'表示3个无符号短整型数
    #                         # 将寄存器的值存储在一个列表中
    #                         registers_list = list(registers)
    #                         scaled_registers_list = [value / 100 for value in registers_list]
    #                         print('scaled_registers_list', scaled_registers_list)
    #
    #                     field_dict = {}
    #                     for field, value in zip(field_list, scaled_registers_list):
    #                         field_dict[field] = value
    #                     point = [
    #                         {
    #                             'measurement': measurement,
    #                             'fields': field_dict
    #                         }]
    #                     self.client.write_points(point)
    #                 except Exception as e:
    #                     print(f"发生错误: {e}")
    #                     continue
    #         except socket.error as e:
    #             print(f"无法连接到 {ip}:{sensor_port}，错误信息：{e}")
    #             time.sleep(0.5)  # 重试前等待一段时间
    #
    #         finally:
    #             client_socket.close()

    # def start_sensor_threads(self, sensors, ip):
    #     threads = []
    #     print(sensors)
    #     for sensor in sensors:
    #         t = threading.Thread(target=self.detect_sensor,
    #                              args=(ip,
    #                                    sensor['sensor_id'],
    #                                    sensor['sensor_port'],
    #                                    sensor['command_code'],
    #                                    sensor['time_out'],
    #                                    sensor['receive_number'],
    #                                    sensor['measurement'],
    #                                    sensor['field_list'])
    #                              )
    #         t.start()
    #         threads.append(t)


class EquipmentStatusViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = serializer.equipmentStatusSerializer  # 添加这一行

    # 返回数据库所有对象.
    def get_queryset(self):
        return models.machineStatus.objects.all()

    # 设备运行状况-查询
    @swagger_auto_schema(
        operation_summary='设备运行状况-查询',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.equipmentStatusSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def equipmentStatusList(self, request):
        config_id = self.request.query_params.get('config_id')
        machine_all = methodConfig.models.componentConfig.objects.filter(config_id=config_id)
        total = machine_all.count()
        result_list = []
        for x in machine_all:
            result_list.append(
                {
                    'id': x.id,
                    'component_name': x.component_name,
                    'component_code': x.component_code,
                    'component_status': x.component_status,
                    'monitor_status': x.monitor_status,
                }
            )
        response_list = {
            'list': result_list,
            'total': total,
        }
        response = {
            'data': response_list,
            'status': 200,
            'message': 'successful',
        }
        return JsonResponse(response)

    # 开始监控
    @swagger_auto_schema(
        operation_summary='开始监控',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='部件id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def monitorOn(self, request):
        id = self.request.query_params.get('id')
        machineStatus = methodConfig.models.componentConfig.objects.get(id=id)
        machines = systemConfig.models.systemConfig.objects.filter(is_apply=1)
        if not machines.exists():
            response = {
                'status': 500,
                'message': '机床未应用'
            }
            return JsonResponse(response)

        influxdb_name = machines.first().database_name
        machine_ip = machines.first().machine_ip

        connect_database(influxdb_name)
        client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin',
                                database=influxdb_name)
        sensor_id = machineStatus.sensor_id
        sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
        channels = systemConfig.models.channelConfig.objects.filter(channel_id=sensor_id).order_by('id')
        field_list = []

        # 遍历所有符合条件的 channelConfig 对象，将其 field 字段加入 field_list
        for H in channels:
            field_list.append(H.channel_field)  # 将 field 拼接到 field_list 中

        # detected_sensors = [
        #     {
        #         'sensor_id': sensor_id,
        #         'sensor_port': sensor.sensor_port,  # 假设传感器的Modbus端口
        #         'command_code': sensor.command_code,  # 这是一个示例的Modbus指令
        #         'time_out': sensor.time_out,  # 5秒超时
        #         'receive_number': sensor.receive_number,  # 预期接收46个字节
        #         'measurement': sensor.measurement,
        #         'field_list': field_list,
        #         # 对应的字段
        #     }
        # ]
        t = threading.Thread(target=detect_sensor, args=(client, machine_ip,
                                                     sensor_id,
                                                     sensor.sensor_port,
                                                     sensor.command_code,
                                                     sensor.time_out,
                                                     sensor.receive_number,
                                                     sensor.measurement,
                                                     field_list)).start()
        # 执行监控算法

        machineStatus.monitor_status = True
        machineStatus.ident =t.ident
        machineStatus.save()
        response = {
            'status': 200,
            'message': '开始监控成功'
        }
        return JsonResponse(response)

    # 结束监控
    @swagger_auto_schema(
        operation_summary='结束监控',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='部件id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def monitorOff(self, request):
        id = self.request.query_params.get('id')
        machineStatus = methodConfig.models.componentConfig.objects.get(id=id)
        machines = systemConfig.models.systemConfig.objects.filter(is_apply=1)
        if not machines.exists():
            response = {
                'status': 500,
                'message': '机床未应用'
            }
            return JsonResponse(response)
        sensor_id = machineStatus.sensor_id
        sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
        # 结束监控算法
        sensor.thread_flag = 0
        sensor.save()
        machineStatus.monitor_status = False
        machineStatus.save()
        response = {
            'status': 200,
            'message': '结束监控成功'
        }
        return JsonResponse(response)

    # 全部开始监控
    @swagger_auto_schema(
        operation_summary='开始监控',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def monitorOnAll(self, request):
        config_id = self.request.query_params.get('config_id')

        # 执行监控算法

        methodConfig.models.componentConfig.objects.filter(config_id=config_id).update(monitor_status=True)

        response = {
            'status': 200,
            'message': '全部开始监控成功'
        }
        return JsonResponse(response)

    # 全部结束监控
    @swagger_auto_schema(
        operation_summary='结束监控',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def monitorOffAll(self, request):
        config_id = self.request.query_params.get('config_id')

        # 结束监控算法

        methodConfig.models.componentConfig.objects.filter(config_id=config_id).update(monitor_status=False,
                                                                                       thread_flag=False)

        response = {
            'status': 200,
            'message': '全部结束监控成功'
        }
        return JsonResponse(response)

    # # 设备数据
    # @swagger_auto_schema(
    #     operation_summary='设备数据',
    #     # 获取参数
    #     manual_parameters=[
    #         openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
    #                           required=True), ],
    #     responses={200: openapi.Response('successful', serializer.equipmentDataSerializer)},
    #     tags=["equipment"],
    # )
    # @action(detail=False, methods=['get'])
    # def equipmentData(self, request):
    #     config_id = self.request.query_params.get('config_id')
    #
    #     # 读取当前机床温度，功率，主轴加速度
    #     a = methodConfig.models.systemConfig.objects.get(config_id=config_id)
    #
    #     result_list = [{
    #         'config_id': a.config_id,
    #         'temp': a.temp,
    #         'temp_min': a.temp_min,
    #         'temp_max': a.temp_max,
    #         'power': a.power,
    #         'power_min': a.power_min,
    #         'power_max': a.power_max,
    #         'acceleration': a.acceleration,
    #         'acceleration_min': a.acceleration_min,
    #         'acceleration_max': a.acceleration_max,
    #     }]
    #     response = {
    #         'data': result_list,
    #         'status': 200,
    #         'message': '设备运行数据查询成功！',
    #     }
    #     return JsonResponse(response)

    # 部件-传感器下拉框
    @swagger_auto_schema(
        operation_summary='部件-传感器下拉框',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def sensorsList(self, request):
        config_id = self.request.query_params.get('config_id')
        conponents = methodConfig.models.componentConfig.objects.filter(config_id=config_id)
        result_list = []
        for conponent in conponents:
            result_list.append({
                'id': conponent.id,
                'component_name': conponent.component_name,
            })
        response_list = {
            'list': result_list,
            'total': conponents.count()
        }
        response = {
            'data': response_list,
            'status': 200,
            'message': '部件下拉框获取成功！',
        }
        return JsonResponse(response)

    # 传感器通道信息
    @swagger_auto_schema(
        operation_summary='部件传感器信息',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='部件id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.sensorDataSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def sensorData(self, request):
        id = self.request.query_params.get('id')
        channels = methodConfig.models.algorithmChannel.objects.filter(algorithm_channel_id=id)
        result_list = []
        for i in channels:
            channel_id = i.channel_id
            sensor_id = i.sensor_id
            channel = systemConfig.models.channelConfig.objects.get(id=channel_id)
            sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
            channel_name = channel.channel_name
            sensor_name = sensor.sensor_name
            result_list.append({
                'id': channel_id,
                'sensor_id': sensor_id,
                'sensor_name': sensor_name,
                'channel_id': channel_id,
                'channel_name': channel_name,
                'status': sensor.sensor_status,
            })
        response_list = {
            'list': result_list,
            'total': channels.count()
        }
        response = {
            'data': response_list,
            'status': 200,
            'message': '传感器通道信息获取成功！',
        }
        return JsonResponse(response)

    # 查询警告及故障代码
    @swagger_auto_schema(
        operation_summary='警告及故障代码查询',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.faultCodeSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def faultCodeList(self, request):
        config_id = self.request.query_params.get('config_id')
        machineConfig = models.faultCode.objects.filter(config_id=config_id)
        total = machineConfig.count()
        result_list = []
        for x in machineConfig:
            result_list.append(
                {
                    "id": x.id,
                    'config_id': x.config_id,
                    'machine_code': x.machine_code,
                    'machine_name': x.machine_name,
                    'warning_time': x.warning_time,
                    'component_id': x.component_id,
                    'component_name': x.component_name,
                    'fault_type': x.fault_type,
                    'fault_code': x.fault_code
                }
            )
        response_list = {
            'list': result_list,
            'total': total,
        }
        response = {
            'data': response_list,
            'status': 200,
            'message': '警告及故障代码获取成功！',
        }
        return JsonResponse(response)

    # 加工时间热力图
    @swagger_auto_schema(
        operation_summary='加工时间热力图',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.thermalDiagramSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def thermalDiagramList(self, request):

        config_id = request.query_params.get('config_id')
        # 查询所有相关数据
        data = thermalDiagram.objects.filter(config_id=config_id)

        # 初始化热力图数据结构
        heatmap_data = {}
        weeks = set()
        days_of_week = set()

        # 遍历数据，填充weeks, days_of_week和heatmap_data
        for entry in data:
            week = entry.machine_process_date.isocalendar()[1]  # 获取ISO周数
            day_of_week = entry.machine_process_date.weekday()  # 获取星期（0=周一，6=周日）
            weeks.add(week)
            days_of_week.add(day_of_week)
            key = (week, day_of_week)
            if key not in heatmap_data:
                heatmap_data[key] = 0
            heatmap_data[key] += entry.machine_running_time

        # 获取当前日期和12周前的日期
        current_date = datetime.now()
        start_date = current_date - timedelta(weeks=12)

        # 构建热力图数据
        final_data = []
        current_week = current_date.isocalendar()[1]
        for i in range(12):
            week_data = []
            for j in range(7):
                day_of_week = (j + 6) % 7  # 将0-6调整为周日（6）到周六（5）
                key = (current_week - i, day_of_week)
                week_day_data = heatmap_data.get(key, 0)
                week_data.append([11 - i, 6 - j, week_day_data])
            final_data.extend(week_data)

        result = {
            'config_id': config_id,
            'data': final_data,
        }
        # 构建响应数据
        response = {
            'data': result,
            'status': 200,
            'message': '加工热力图数据获取成功！',
        }

        return JsonResponse(response)

    # 部件树
    @swagger_auto_schema(
        operation_summary='部件树',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.componentTreeSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def componentTreeList(self, request):
        config_id = self.request.query_params.get('config_id')
        machine_information = methodConfig.models.componentConfig.objects.filter(config_id=config_id)
        components = []
        for x in machine_information:
            components.append(x.component_name)

        # 创建部件树数据结构
        machine_name = machine_information.first().machine_name if machine_information.exists() else '未知机床'
        response_list = {
            'name': machine_name,
            'value': '1',
            'children': []
        }

        for component in components:
            child_component = {
                'name': component,
                'value': f'1.{len(response_list["children"]) + 1}'
            }
            response_list['children'].append(child_component)

        response = {
            'data': response_list,
            'status': 200,
            'message': '部件树获取成功！',
        }
        return JsonResponse(response)

    # 机床信息
    @swagger_auto_schema(
        operation_summary='机床信息',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.machineInformationSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def machineInformation(self, request):
        config_id = self.request.query_params.get('config_id')
        machine = systemConfig.models.systemConfig.objects.get(id=config_id)

        result = {
            'id': machine.id,
            'machine_code': machine.machine_code,
            'machine_name': machine.machine_name,
            'machine_image': f"http://{get_local_ip()}:8000" + machine.machine_image.url,
        }

        response = {
            'data': result,
            'status': 200,
            'message': '机床信息获取成功！',
        }
        return JsonResponse(response)

    # 警告及故障代码填写
    @swagger_auto_schema(
        operation_summary='警告及故障代码填写',
        request_body=serializer.addFaultCodeSerializer,
        responses={200: '警告及故障代码填写成功'},
        tags=["equipment"],
    )
    @action(detail=False, methods=['post'])
    def addFaultCode(self, request):
        component_id = self.request.data.get('component_id')
        component = methodConfig.models.componentConfig.objects.get(id=component_id)
        warning_time = self.request.data.get('warning_time')  # 警告时间
        fault_type = self.request.data.get('fault_type')  # 报警类型
        fault_code = self.request.data.get('fault_code')  # 报警代码

        new_faultCode = models.faultCode.objects.create(config_id=component.config_id,
                                                        machine_code=component.machine_code,
                                                        machine_name=component.machine_name,
                                                        warning_time=warning_time,
                                                        component_id=component_id,
                                                        component_name=component.component_name,
                                                        fault_type=fault_type,
                                                        fault_code=fault_code, )
        response = {
            'id': new_faultCode.id,
            'status': 200,
            'message': '警告及故障代码填写成功'
        }
        return JsonResponse(response)

    # 机床加工时间填写
    @swagger_auto_schema(
        operation_summary='机床加工时间填写',
        request_body=serializer.addThermalDiagramSerializer,
        responses={200: '机床加工时间填写成功'},
        tags=["equipment"],
    )
    @action(detail=False, methods=['post'])
    def addThermalDiagram(self, request):
        config_id = self.request.data.get('config_id')  # 机床系统配置的id
        machine_process_date = self.request.data.get('machine_process_date')  # 机床工作日期
        machine_running_time = self.request.data.get('machine_running_time')  # 机床加工时间

        machine = systemConfig.models.systemConfig.objects.get(id=config_id)

        new_thermalDiagram = models.thermalDiagram.objects.create(config_id=config_id,
                                                                  machine_code=machine.machine_code,
                                                                  machine_name=machine.machine_name,
                                                                  machine_process_date=machine_process_date,
                                                                  machine_running_time=machine_running_time, )
        response = {
            'id': new_thermalDiagram.id,
            'status': 200,
            'message': '机床加工时间填写成功'
        }
        return JsonResponse(response)

    # 机床参数查询
    @swagger_auto_schema(
        operation_summary='机床参数查询',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: '机床参数查询成功'},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def findParameter(self, request):
        config_id = self.request.query_params.get('config_id')
        if systemConfig.models.systemConfig.objects.filter(id=config_id).exists():
            machine_parameters = models.machineParameter.objects.filter(config_id=config_id)
            if machine_parameters.count() > 0:
                machine_parameter = machine_parameters.last()
                Parameter = {
                    'machine_t': machine_parameter.machine_t,
                    'machine_p': machine_parameter.machine_p,
                    'machine_a': machine_parameter.machine_a,
                    'machine_t_unit': machine_parameter.machine_t_unit,
                    'machine_p_unit': machine_parameter.machine_p_unit,
                    'machine_a_unit': machine_parameter.machine_a_unit,
                    'machine_t_max': machine_parameter.machine_t_max,
                    'machine_p_max': machine_parameter.machine_p_max,
                    'machine_a_max': machine_parameter.machine_a_max,
                }
            else:
                Parameter = {
                    'machine_t': 0,
                    'machine_p': 0,
                    'machine_a': 0,
                    'machine_t_unit': '',
                    'machine_p_unit': '',
                    'machine_a_unit': '',
                    'machine_t_max': 0,
                    'machine_p_max': 0,
                    'machine_a_max': 0,
                }
            response = {
                'data': Parameter,
                'status': 200,
                'message': '机床参数查询成功'
            }
            return JsonResponse(response)
        else:
            response = {
                'status': 500,
                'message': '未找到该机床信息'
            }
            return JsonResponse(response)

    # 剩余寿命曲线
    @swagger_auto_schema(
        operation_summary='剩余寿命曲线',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: '剩余寿命曲线获取成功'},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def remainingLife(self, request):
        config_id = self.request.query_params.get('config_id')
        num_points = 100
        xData = np.arange(0, 10.1, 0.1).round(1).tolist()
        if systemConfig.models.systemConfig.objects.filter(id=config_id).exists():
            response = {
                "status": 200,
                "message": "Successful",
                "data": {
                    "x_axis": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7,
                               1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4,
                               2.5,
                               2.6,
                               2.7,
                               2.8,
                               2.9,
                               3.0,
                               3.1,
                               3.2,
                               3.3,
                               3.4,
                               3.5,
                               3.6,
                               3.7,
                               3.8,
                               3.9,
                               4.0,
                               4.1,
                               4.2,
                               4.3,
                               4.4,
                               4.5,
                               4.6,
                               4.7,
                               4.8,
                               4.9,
                               5.0,
                               5.1,
                               5.2,
                               5.3,
                               5.4,
                               5.5,
                               5.6,
                               5.7,
                               5.8,
                               5.9,
                               6.0,
                               6.1,
                               6.2,
                               6.3,
                               6.4,
                               6.5,
                               6.6,
                               6.7,
                               6.8,
                               6.9,
                               7.0,
                               7.1,
                               7.2,
                               7.3,
                               7.4,
                               7.5,
                               7.6,
                               7.7,
                               7.8,
                               7.9,
                               8.0,
                               8.1,
                               8.2,
                               8.3,
                               8.4,
                               8.5,
                               8.6,
                               8.7,
                               8.8,
                               8.9,
                               9.0,
                               9.1,
                               9.2,
                               9.3,
                               9.4,
                               9.5,
                               9.6,
                               9.7,
                               9.8,
                               9.9,
                               10.0
                               ],
                    "y_pre_axis": [
                        [0, 100],
                        [1, 97],
                        [2, 96
                         ],
                        [
                            3,
                            94
                        ],
                        [
                            4,
                            92
                        ]
                    ],
                    "y_last_axis": [
                        [
                            4,
                            92
                        ],
                        [
                            5,
                            90
                        ],
                        [
                            6,
                            88
                        ],
                        [
                            7,
                            86
                        ],
                        [
                            8,
                            84
                        ],
                        [
                            9,
                            83
                        ],
                        [
                            10,
                            82
                        ],
                        [
                            11,
                            80
                        ],
                        [
                            12,
                            79
                        ],
                        [
                            13,
                            77
                        ],
                        [
                            14,
                            76
                        ],
                        [
                            15,
                            75
                        ],
                        [
                            16,
                            74
                        ],
                        [
                            17,
                            73
                        ],
                        [
                            18,
                            72
                        ],
                        [
                            19,
                            72
                        ],
                        [
                            20,
                            71
                        ],
                        [
                            21,
                            70
                        ],
                        [
                            22,
                            70
                        ],
                        [
                            23,
                            69
                        ],
                        [
                            24,
                            69
                        ],
                        [
                            25,
                            68
                        ],
                        [
                            26,
                            67
                        ],
                        [
                            27,
                            67
                        ],
                        [
                            28,
                            66
                        ],
                        [
                            29,
                            66
                        ],
                        [
                            30,
                            66
                        ],
                        [
                            31,
                            65
                        ],
                        [
                            32,
                            65
                        ],
                        [
                            33,
                            64
                        ],
                        [
                            34,
                            64
                        ],
                        [
                            35,
                            63
                        ],
                        [
                            36,
                            63
                        ],
                        [
                            37,
                            62
                        ],
                        [
                            38,
                            62
                        ],
                        [
                            39,
                            61
                        ],
                        [
                            40,
                            61
                        ],
                        [
                            41,
                            60
                        ],
                        [
                            42,
                            60
                        ],
                        [
                            43,
                            60
                        ],
                        [
                            44,
                            59
                        ],
                        [
                            45,
                            59
                        ],
                        [
                            46,
                            59
                        ],
                        [
                            47,
                            59
                        ],
                        [
                            48,
                            58
                        ],
                        [
                            49,
                            58
                        ],
                        [
                            50,
                            58
                        ],
                        [
                            51,
                            57
                        ],
                        [
                            52,
                            57
                        ],
                        [
                            53,
                            57
                        ],
                        [
                            54,
                            56
                        ],
                        [
                            55,
                            56
                        ],
                        [
                            56,
                            56
                        ],
                        [
                            57,
                            55
                        ],
                        [
                            58,
                            55
                        ],
                        [
                            59,
                            55
                        ],
                        [
                            60,
                            54
                        ],
                        [
                            61,
                            54
                        ],
                        [
                            62,
                            54
                        ],
                        [
                            63,
                            54
                        ],
                        [
                            64,
                            53
                        ],
                        [
                            65,
                            53
                        ],
                        [
                            66,
                            52
                        ],
                        [
                            67,
                            52
                        ],
                        [
                            68,
                            51
                        ],
                        [
                            69,
                            51
                        ],
                        [
                            70,
                            50
                        ],
                        [
                            71,
                            49
                        ],
                        [
                            72,
                            49
                        ],
                        [
                            73,
                            48
                        ],
                        [
                            74,
                            48
                        ],
                        [
                            75,
                            47
                        ],
                        [
                            76,
                            46
                        ],
                        [
                            77,
                            46
                        ],
                        [
                            78,
                            45
                        ],
                        [
                            79,
                            44
                        ],
                        [
                            80,
                            44
                        ],
                        [
                            81,
                            43
                        ],
                        [
                            82,
                            42
                        ],
                        [
                            83,
                            41
                        ],
                        [
                            84,
                            40
                        ],
                        [
                            85,
                            39
                        ],
                        [
                            86,
                            37
                        ],
                        [
                            87,
                            36
                        ],
                        [
                            88,
                            35
                        ],
                        [
                            89,
                            34
                        ],
                        [
                            90,
                            32
                        ],
                        [
                            91,
                            30
                        ],
                        [
                            92,
                            29
                        ],
                        [
                            93,
                            27
                        ],
                        [
                            94,
                            24
                        ],
                        [
                            95,
                            22
                        ],
                        [
                            96,
                            19
                        ],
                        [
                            97,
                            16
                        ],
                        [
                            98,
                            12
                        ],
                        [
                            99,
                            7
                        ],
                        [
                            100,
                            0
                        ]
                    ],
                    "middle_value": 30,
                    "last_value": 60,
                }
            }
        else:
            response = response = {
                'status': 500,
                'message': '未找到该机床信息'
            }
        return JsonResponse(response)
