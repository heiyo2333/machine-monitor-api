import time

from django.db.models import Q, Max
from django.http import JsonResponse
from django.urls import reverse
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from rest_framework.decorators import action
from datetime import datetime, timedelta
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication

import methodConfig
import systemConfig
from methodConfig.views import get_local_ip
from . import models, serializer
from .models import thermalDiagram


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

        # 执行监控算法

        machineStatus.monitor_status = True
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

        # 结束监控算法

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

        methodConfig.models.componentConfig.objects.filter(config_id=config_id).update(monitor_status=False)

        response = {
            'status': 200,
            'message': '全部结束监控成功'
        }
        return JsonResponse(response)

    # 设备数据
    @swagger_auto_schema(
        operation_summary='设备数据',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.equipmentDataSerializer)},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def equipmentData(self, request):
        config_id = self.request.query_params.get('config_id')

        # 读取当前机床温度，功率，主轴加速度
        a = methodConfig.models.systemConfig.objects.get(config_id=config_id)

        result_list = [{
            'config_id': a.config_id,
            'temp': a.temp,
            'temp_min': a.temp_min,
            'temp_max': a.temp_max,
            'power': a.power,
            'power_min': a.power_min,
            'power_max': a.power_max,
            'acceleration': a.acceleration,
            'acceleration_min': a.acceleration_min,
            'acceleration_max': a.acceleration_max,
        }]
        response = {
            'data': result_list,
            'status': 200,
            'message': '设备运行数据查询成功！',
        }
        return JsonResponse(response)

    # 传感器下拉框
    @swagger_auto_schema(
        operation_summary='传感器下拉框',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @action(detail=False, methods=['get'])
    def sensorsData(self, request):
        config_id = self.request.query_params.get('config_id')
        sensors = systemConfig.models.sensorConfig.objects.filter(config_id=config_id)
        result_list =[]
        for sensor in sensors:
            result_list.append({
                'id': sensor.id,
                'sensor_name': sensor.sensor_name,
            })
        response_list = {
            'list': result_list,
            'total': sensors.count()
        }
        response = {
            'data': response_list,
            'status': 200,
            'message': '传感器下拉框获取成功！',
        }
        return JsonResponse(response)

    # 传感器通道信息
    @swagger_auto_schema(
        operation_summary='传感器通道信息',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='传感器id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful')},
        tags=["equipment"],
    )
    @ action(detail=False, methods=['get'])
    def sensorChannel(self, request):
        id = self.request.query_params.get('id')
        channels = methodConfig.models.channelConfig.objects.filter(channel_id=id)
        result_list = []
        for channel in channels:
            result_list.append({
                'id': channel.id,
                'channel_name': channel.channel_name,
                'is_monitor': channel.is_monitor,
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
        operation_summary='警告及故障代码',
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
                    'id': x.id,
                    'machine_code': x.machine_code,
                    'machine_name': x.machine_name,
                    'warning_time': x.warning_time,
                    'component_name': x.component_name,
                    'fault_type': x.fault_type,
                    'fault_code': x.fault_code,
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
        component = methodConfig.models.componentConfig.objects.filter(id=component_id)
        warning_time = self.request.data.get('warning_time')  # 警告时间
        fault_type = self.request.data.get('fault_type')  # 报警类型
        fault_code = self.request.data.get('fault_code')  # 报警代码

        new_faultCode = models.faultCode.objects.create(config_id=component.config_id,
                                                        machine_code=component.machine_code,
                                                        machine_name=component.machine_name,
                                                        warning_time=warning_time,
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
