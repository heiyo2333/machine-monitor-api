import os
import time
import struct
import numpy as np
import pandas as pd
from django.db.models import Q
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
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
from media.AlgorithmFile.thresholdDetection import threshold_detection
from methodConfig.views import get_local_ip
from systemConfig.models import sensorConfig
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
        algorithms = methodConfig.models.algorithmConfig.objects.filter(config_id=config_id)
        machine_all = methodConfig.models.componentConfig.objects.filter(config_id=config_id)
        total = machine_all.count()
        result_list = []
        for algorithm in algorithms:
            result_list.append(
                {
                    'id': algorithm.id,
                    'algorithm_name': algorithm.algorithm_name,
                    'algorithm_code': algorithm.algorithm_code,
                    # 'component_name': algorithm.component_name,
                    # 'component_code': x.component_code,
                    # 'component_status': x.component_status,
                    'algorithm_monitor_status': algorithm.algorithm_monitor_status,
                    # 'monitor_status': x.monitor_status,
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
        machine_id = self.request.query_params.get('id')
        machine_status = methodConfig.models.componentConfig.objects.get(id=machine_id)
        # machines = systemConfig.models.systemConfig.objects.filter(is_apply=1)
        # if not machines.exists():
        #     response = {
        #         'status': 500,
        #         'message': '机床未应用'
        #     }
        #     return JsonResponse(response)
        #
        # influxdb_name = machines.first().database_name
        # machine_ip = machines.first().machine_ip
        #
        # connect_database(influxdb_name)
        # client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin',
        #                         database=influxdb_name)
        # sensor_id = machineStatus.sensor_id
        # sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
        # channels = systemConfig.models.channelConfig.objects.filter(channel_id=sensor_id).order_by('id')
        # field_list = []
        #
        # # 遍历所有符合条件的 channelConfig 对象，将其 field 字段加入 field_list
        # for H in channels:
        #     field_list.append(H.channel_field)  # 将 field 拼接到 field_list 中
        #
        # # detected_sensors = [
        # #     {
        # #         'sensor_id': sensor_id,
        # #         'sensor_port': sensor.sensor_port,  # 假设传感器的Modbus端口
        # #         'command_code': sensor.command_code,  # 这是一个示例的Modbus指令
        # #         'time_out': sensor.time_out,  # 5秒超时
        # #         'receive_number': sensor.receive_number,  # 预期接收46个字节
        # #         'measurement': sensor.measurement,
        # #         'field_list': field_list,
        # #         # 对应的字段
        # #     }
        # # ]
        # t = threading.Thread(target=detect_sensor, args=(client, machine_ip,
        #                                              sensor_id,
        #                                              sensor.sensor_port,
        #                                              sensor.command_code,
        #                                              sensor.time_out,
        #                                              sensor.receive_number,
        #                                              sensor.measurement,
        #                                              field_list)).start()
        # 执行监控算法

        machine_status.monitor_status = True
        # machineStatus.ident =t.ident
        machine_status.save()
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
        machine_id = self.request.query_params.get('id')
        machine_status = methodConfig.models.componentConfig.objects.get(id=machine_id)
        machines = systemConfig.models.systemConfig.objects.filter(is_apply=1)
        if not machines.exists():
            response = {
                'status': 500,
                'message': '机床未应用'
            }
            return JsonResponse(response)

        machine_status.monitor_status = False
        machine_status.save()
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
        operation_summary='传感器通道信息',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.sensorDataSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def sensorData(self, request):
        config_id = self.request.query_params.get('config_id')
        components = methodConfig.models.componentConfig.objects.filter(config_id=config_id)
        result_list = []
        for component in components:
            component_sensors = methodConfig.models.componentSensor.objects.filter(component_id=component.id)
            for i in component_sensors:
                sensor = i.sensor_id
                if "三相加速度" in systemConfig.models.sensorConfig.objects.get(id=sensor).sensor_name:
                    a = systemConfig.models.sensorConfig.objects.get(id=sensor)
                    result_list.append({
                        'id': a.id,
                        'component_name': component.component_name,
                        'sensor_name': a.sensor_name,
                        'overrun_times': a.overrun_times,
                        'status': a.operational_status,
                    })
        response_list = {
            'list': result_list,
            'total': len(components)
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

    # 机床加工时间填写
    @swagger_auto_schema(
        operation_summary='机床加工时间填写',
        request_body=serializer.addThermalDiagramSerializer,
        responses={200: '机床加工时间填写成功'},
        tags=["equipment"],
    )
    @action(detail=False, methods=['post'])
    def addThermalDiagram(self, request):
        config_id = systemConfig.models.systemConfig.objects.get(is_apply=1).id  # 机床系统配置的id
        machine = systemConfig.models.systemConfig.objects.get(id=config_id)
        today_date = datetime.utcnow().date()
        sensor_query = Q(config_id=config_id) & Q(sensor_code='sp_current')
        sensor_id = systemConfig.models.sensorConfig.objects.get(sensor_query).id
        for i in range(20):
            working_hours = 0
            front_date = today_date - timedelta(days=i)
            date_str = front_date.strftime('%Y-%m-%d')
            machine_query = Q(config_id=config_id) & Q(machine_process_date__exact=date_str)
            if models.thermalDiagram.objects.filter(machine_query).exists():
                # 该日期的加工时间数据已经有了-->不做操作
                continue
            else:
                # 该日期的加工时间数据还没有-->寻找数据
                query = Q(date__exact=date_str) & Q(sensor_id=sensor_id)
                # print(query)
                if systemConfig.models.influxDataConfig.objects.filter(query).exists():
                    influx_object = systemConfig.models.influxDataConfig.objects.get(query)
                    file_path = influx_object.influx_file.path
                    if os.path.exists(file_path):
                        data = pd.read_csv(file_path)
                        # 转换 'time' 列为 datetime 格式
                        data['time'] = pd.to_datetime(data['time'])
                        # 求平方之和再开方
                        result = np.sqrt(data['Current_U'] ** 2 + data['Current_V'] ** 2 + data['Current_W'] ** 2)
                        # 如果需要将结果添加为新列
                        data['Current_Magnitude'] = result
                        # print(data['Current_Magnitude'])

                        # 标记分段（时间间隔大于3秒的作为新段）
                        time_diff = data['time'].diff()
                        gap_threshold = timedelta(seconds=3)
                        data['segment'] = (time_diff > gap_threshold).cumsum()

                        # 筛选 Current_Magnitude > 3 的数据
                        filtered_data = data[data['Current_Magnitude'] > 3].copy()

                        # # 计算每段的时间差
                        # filtered_data['time_diff'] = filtered_data['time'].diff()
                        # filtered_data.loc[
                        #     filtered_data['segment'] != filtered_data['segment'].shift(), 'time_diff'] = pd.NaT

                        # 修正代码以避免 SettingWithCopyWarning
                        filtered_data.loc[:, 'time_diff'] = filtered_data['time'].diff()
                        filtered_data.loc[
                            filtered_data['segment'] != filtered_data['segment'].shift(), 'time_diff'] = pd.NaT

                        # 计算总时长（秒数）
                        total_duration = filtered_data['time_diff'].dt.total_seconds().sum()

                        # 输出总时长
                        print(f"总有效时长为 {total_duration / 3600:.2f} H")
                        models.thermalDiagram.objects.create(config_id=config_id,
                                                             machine_code=machine.machine_code,
                                                             machine_name=machine.machine_name,
                                                             machine_process_date=date_str,
                                                             machine_running_time=round(total_duration / 3600, 2))
        response = {
            'status': 200,
            'message': '机床加工时间填写成功'
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
        week_dictionary = {0: "周一", 1: "周二", 2: "周三", 3: "周四", 4: "周五", 5: "周六", 6: "周日"}
        for entry in data:
            week = entry.machine_process_date.isocalendar()[1]  # 获取ISO周数
            day_of_week = entry.machine_process_date.weekday()  # 获取星期（0=周一，6=周日)
            # day_of_week = week_dictionary[entry.machine_process_date.weekday()]  # 获取星期（0=周一，6=周日）
            today = datetime.utcnow().date()
            today_str = today.strftime('%Y-%m-%d')
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
        machine = systemConfig.models.systemConfig.objects.filter(id=config_id)
        components = methodConfig.models.componentConfig.objects.filter(config_id=config_id)

        # 创建部件树数据结构
        machine_name = machine.first().machine_name if machine.exists() else '未知机床'
        response_list = {
            'name': machine_name,
            'value': '1',
            'children': []
        }
        sensor_number = 0
        component_number = 0
        for component in components:
            child_component = {
                'name': component.component_name,
                'value': f'1.{component_number + 1}',
                'children': []
            }
            component_number += 1
            component_sensors = methodConfig.models.componentSensor.objects.filter(component_id=component.id)
            for component_sensor in component_sensors:
                sensor = systemConfig.models.sensorConfig.objects.get(id=component_sensor.sensor_id)
                child_sensor = {
                    'name': sensor.sensor_name,
                    'value': f'2.{sensor_number + 1}',
                    'children': []
                }
                child_component['children'].append(child_sensor)
                sensor_number += 1
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
                parameter = {
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
                parameter = {
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
                'data': parameter,
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
            openapi.Parameter('component_id', openapi.IN_QUERY, description='部件id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: '剩余寿命曲线获取成功'},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def remainingLife(self, request):
        component_id = self.request.query_params.get('component_id')
        c = methodConfig.models.componentConfig.objects.get(id=component_id)
        if c.x_axis and c.y_pre_axis and c.y_last_axis:
            data = {
                'id':c.id,
                'x_axis':c.x_axis,
                'y_pre_axis':c.y_pre_axis,
                'y_last_axis':c.y_last_axis,
                'middle_value':c.middle_value,
                'last_value':c.last_value,
            }
            response = {
                "status": 200,
                "message": "剩余寿命曲线获取成功！",
                "data": data
            }
        else:
             response = {
                'status': 500,
                'message': '暂无剩余寿命曲线数据！'
            }
        return JsonResponse(response)

    # 部件监控接口
    @swagger_auto_schema(
        operation_summary='部件监控',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def equipmentMonitor(self, request):
        config_id = self.request.query_params.get('config_id')
        components = methodConfig.models.componentConfig.objects.filter(config_id=config_id, monitor_status=True)
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        for component in components:
            sensors = methodConfig.models.componentSensor.objects.filter(component_id=component.id)
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
            overrun_times = threshold_detection(cur=cur, vib=vib, date=date)
            if 0 <= overrun_times < 30:
                operational_status = 0
            elif 30 <= overrun_times < 100:
                operational_status = 1
            else:
                operational_status = 2
            systemConfig.models.sensorConfig.objects.filter(id=s2).update(overrun_times=overrun_times,
                                                                       operational_status=operational_status)

        response = {
            'status': 200,
            'message': '部件监控成功'
        }
        return JsonResponse(response)
