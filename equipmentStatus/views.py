import ast
import importlib
import os
import sys
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

import equipmentStatus.models
import methodConfig
import systemConfig
from methodConfig.models import algorithmConfig
from methodConfig.views import get_local_ip
from systemConfig.models import sensorConfig
from . import models, serializer
from .models import thermalDiagram
import threading


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


class EquipmentStatusViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = serializer.algorithmStatusListSerializer  # 添加这一行

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
        responses={200: openapi.Response('successful', serializer.algorithmStatusListSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def algorithmStatusList(self, request):
        # config_id = self.request.query_params.get('config_id')
        config_id = systemConfig.models.systemConfig.objects.get(is_apply=1).id
        algorithms = methodConfig.models.algorithmConfig.objects.filter(config_id=config_id)
        total = algorithms.count()
        result_list = []
        for algorithm in algorithms:
            result_list.append(
                {
                    'id': algorithm.id,
                    'algorithm_name': algorithm.algorithm_name,
                    'algorithm_code': algorithm.algorithm_code,
                    'algorithm_type': algorithm.algorithm_type,
                    'function_name': algorithm.function_name,
                    'algorithm_monitor_status': algorithm.algorithm_monitor_status,
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
            openapi.Parameter('id', openapi.IN_QUERY, description='算法id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def monitorOn(self, request):
        algorithm_id = self.request.query_params.get('id')
        algorithm_status = methodConfig.models.algorithmConfig.objects.get(id=algorithm_id)
        algorithm_status.algorithm_monitor_status = True
        algorithm_status.save()
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
            openapi.Parameter('id', openapi.IN_QUERY, description='算法id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def monitorOff(self, request):
        algorithm_id = self.request.query_params.get('id')
        algorithm_status = methodConfig.models.algorithmConfig.objects.get(id=algorithm_id)
        algorithm_status.algorithm_monitor_status = False
        algorithm_status.save()
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

        methodConfig.models.algorithmConfig.objects.filter(config_id=config_id).update(algorithm_monitor_status=True)

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

        methodConfig.models.algorithmConfig.objects.filter(config_id=config_id).update(algorithm_monitor_status=False)

        response = {
            'status': 200,
            'message': '全部结束监控成功'
        }
        return JsonResponse(response)

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

    # 机床部件状态
    @swagger_auto_schema(
        operation_summary='机床部件状态',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.componentStatusSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def componentStatus(self, request):
        config_id = self.request.query_params.get('config_id')
        print(config_id)
        components = methodConfig.models.componentConfig.objects.filter(config_id=config_id)
        count = 1
        result_list = []
        for component in components:
            status = methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component.id,
                                                                                 algorithm_type=0).order_by(
                '-id').first()
            if status is None:
                continue
            count += 1
            result_list.append({
                'id': status.id,
                'component_name': status.component_name,
                'sensor_name': status.sensor_name,
                'overrun_times': status.value1,
                'status': status.value2,
            })
        response_list = {
            'list': result_list,
            'total': count
        }
        response = {
            'data': response_list,
            'status': 200,
            'message': '机床部件状态获取成功！',
        }
        return JsonResponse(response)

    # 报警记录
    @swagger_auto_schema(
        operation_summary='报警记录',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.faultInformationSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def faultInformationList(self, request):
        # config_id = self.request.query_params.get('config_id')
        config_id = systemConfig.models.systemConfig.objects.get(is_apply=1).id
        faults = models.faultInformation.objects.filter(config_id=config_id).order_by('-id')
        total = faults.count()
        result_list = []
        for x in faults:
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
                    'fault_status': x.fault_status
                }
            )
        response_list = {
            'list': result_list,
            'total': total,
        }
        response = {
            'data': response_list,
            'status': 200,
            'message': '报警记录获取成功！',
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
                    # 'machine_t': machine_parameter.machine_t,
                    'machine_p': machine_parameter.machine_p,
                    'machine_a': machine_parameter.machine_a,
                    # 'machine_t_unit': machine_parameter.machine_t_unit,
                    'machine_p_unit': machine_parameter.machine_p_unit,
                    'machine_a_unit': machine_parameter.machine_a_unit,
                    # 'machine_t_max': machine_parameter.machine_t_max,
                    'machine_p_max': machine_parameter.machine_p_max,
                    'machine_a_max': machine_parameter.machine_a_max,
                }
            else:
                parameter = {
                    # 'machine_t': 0,
                    'machine_p': 0,
                    'machine_a': 0,
                    # 'machine_t_unit': '',
                    'machine_p_unit': '',
                    'machine_a_unit': '',
                    # 'machine_t_max': 0,
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
        if methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,
                                                                       algorithm_type=1).order_by('-id').exists():
            life = methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component_id,
                                                                               algorithm_type=1).order_by('-id').first()
            data = {
                'id': life.id,
                'x_axis': ast.literal_eval(life.value1),
                'y_pre_axis': ast.literal_eval(life.value2),
                'y_last_axis': ast.literal_eval(life.value3),
                'middle_value': c.middle_value,
                'last_value': c.last_value,
            }
            response = {
                "status": 200,
                "message": "剩余寿命曲线获取成功！",
                "data": data
            }
        else:
            response = {
                'status': 200,
                'message': '暂无剩余寿命曲线数据！',
                "data": []
            }
        return JsonResponse(response)

    # 算法监控接口
    @swagger_auto_schema(
        operation_summary='算法监控',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def algorithmMonitor(self, request):
        config_id = self.request.query_params.get('config_id')
        algorithms = methodConfig.models.algorithmConfig.objects.filter(config_id=config_id,
                                                                        algorithm_monitor_status=True)

        for algorithm in algorithms:

            name = algorithm.function_name
            algorithm_path = algorithm.algorithm_file.path
            # 已知模块地址和函数名
            module_path = algorithm_path  # 模块文件的路径
            function_name = name  # 函数名

            # 获取模块文件名（不包括.py扩展名）
            module_name = module_path.split('/')[-1].split('.')[0]

            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            if spec is None:
                raise ImportError(f"Could not find module at {module_path}")

            module = importlib.util.module_from_spec(spec)
            if module is None:
                raise ImportError(f"Could not create module from spec for {module_path}")

            sys.modules[module_name] = module  # 将模块添加到sys.modules中
            spec.loader.exec_module(module)  # 执行模块

            # 调用函数
            try:
                algorithm_function = getattr(module, function_name)
            except AttributeError:
                raise AttributeError(f"The function {function_name} does not exist in the module {module_name}")

            channels = methodConfig.models.algorithmChannel.objects.filter(algorithm_id=algorithm.id)
            args1 = ()
            for channel in channels:
                args1 += (channel.channel_id,)
            sensors = systemConfig.models.channelConfig.objects.filter(id__in=args1)
            s1 = None
            s2 = None
            for i in sensors:
                s = i.sensor_id
                if "电流" in systemConfig.models.sensorConfig.objects.get(id=s).sensor_name:
                    s1 = s
                elif "三相加速度" in systemConfig.models.sensorConfig.objects.get(id=s).sensor_name:
                    s2 = s
            if s2:
                c = methodConfig.models.componentSensor.objects.get(sensor_id=s2)
            else:
                c = methodConfig.models.componentSensor.objects.get(sensor_id=s1)

            component = methodConfig.models.componentConfig.objects.get(id=c.component_id)
            sensor_name = systemConfig.models.sensorConfig.objects.get(id=c.sensor_id).sensor_name
            config_id = component.config_id
            machine = systemConfig.models.systemConfig.objects.get(id=config_id)

            if algorithm.algorithm_type == 0:
                overrun_times, operational_status = algorithm_function(*args1)
                if operational_status == 2:
                    count = 0
                    a = methodConfig.models.componentAlgorithmRecord.objects.filter(component_id=component.id,
                                                                                    algorithm_type=0).order_by('-id')[
                        :15]
                    for i in a:
                        if i.value2 == 2:
                            count += 1
                    if count >= 10:
                        operational_status = 3

                methodConfig.models.componentAlgorithmRecord.objects.create(component_id=component.id,
                                                                            component_name=component.component_name,
                                                                            algorithm_type=algorithm.algorithm_type,
                                                                            date=datetime.now().date(),
                                                                            sensor_name=sensor_name,
                                                                            value1=overrun_times,
                                                                            value2=operational_status)

                if operational_status == 2:
                    equipmentStatus.models.faultInformation.objects.create(config_id=config_id,
                                                                           machine_code=machine.machine_code,
                                                                           machine_name=machine.machine_name,
                                                                           warning_time=datetime.now().date(),
                                                                           component_id=component.id,
                                                                           component_name=component.component_name,
                                                                           fault_type='0', fault_status='异常')

                elif operational_status == 3:
                    equipmentStatus.models.faultInformation.objects.create(config_id=config_id,
                                                                           machine_code=machine.machine_code,
                                                                           machine_name=machine.machine_name,
                                                                           warning_time=datetime.now().date(),
                                                                           component_id=component.id,
                                                                           component_name=component.component_name,
                                                                           fault_type='0', fault_status='损坏')

            else:
                x_axis, y_pre_axis, y_last_axis, current_life, used_day = algorithm_function(*args1)
                methodConfig.models.componentAlgorithmRecord.objects.create(component_id=component.id,
                                                                            component_name=component.component_name,
                                                                            algorithm_type=algorithm.algorithm_type,
                                                                            date=datetime.now().date(),
                                                                            sensor_name=sensor_name, value1=x_axis,
                                                                            value2=y_pre_axis, value3=y_last_axis,
                                                                            value4=current_life,
                                                                            value5=used_day)
                methodConfig.models.componentConfig.objects.filter(id=component.id).update(current_life=current_life)

                if component.middle_value >= current_life > component.last_value:
                    equipmentStatus.models.faultInformation.objects.create(config_id=config_id,
                                                                           machine_code=machine.machine_code,
                                                                           machine_name=machine.machine_name,
                                                                           warning_time=datetime.now().date(),
                                                                           component_id=component.id,
                                                                           component_name=component.component_name,
                                                                           fault_type='1', fault_status='中期')

                elif current_life <= component.last_value:
                    equipmentStatus.models.faultInformation.objects.create(config_id=config_id,
                                                                           machine_code=machine.machine_code,
                                                                           machine_name=machine.machine_name,
                                                                           warning_time=datetime.now().date(),
                                                                           component_id=component.id,
                                                                           component_name=component.component_name,
                                                                           fault_type='1', fault_status='末期')

        response = {
            'status': 200,
            'message': '算法监控成功！'
        }
        return JsonResponse(response)
