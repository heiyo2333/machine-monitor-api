import time

from django.db.models import Q, Max
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from rest_framework.decorators import action
from datetime import datetime
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication

from . import models, serializer


class EquipmentStatusViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)
    parser_classes = (MultiPartParser, FormParser)

    # 返回数据库所有对象.
    def get_queryset(self):
        return models.machineStatus.objects.all()

    # 设备运行状况 > 查询机床运行状况
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 机床运行状况',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('machine_code', openapi.IN_QUERY, description='机床编号', type=openapi.TYPE_STRING,
                              required=True),
            openapi.Parameter('pageSize', openapi.IN_QUERY, description='一页多少条', type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('current', openapi.IN_QUERY, description='当前页面号', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.EquipmentStatusSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def machineStatusList(self, request):
        machine_code = self.request.query_params.get('machine_code')
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        first = (current - 1) * pageSize
        last = current * pageSize
        machine_all = models.machineStatus.objects.filter(machine_code=machine_code)[first:last]
        total = models.machineStatus.objects.filter(machine_code=machine_code).count()
        result_list = []
        for x in machine_all:
            result_list.append(
                {
                    'machine_code': x.machine_code,
                    'machine_name': x.machine_name,
                    'component_number': x.component_number,
                    'component_name': x.component_name,
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

    # 设备运行状况 > 查询机床运行物理量
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 机床运行物理量',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('value_name', openapi.IN_QUERY, description='物理量名称', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.MonitorValueSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def monitorValueList(self, request):
        value_name = self.request.query_params.get('value_name')
        value_information = models.monitorValue.objects.filter(value_name=value_name)
        total = models.monitorValue.objects.filter(value_name=value_name).count()
        result_list = []
        for x in value_information:
            result_list.append(
                {
                    'value_name': x.value_name,
                    'value_unit': x.value_unit,
                    'value': x.value,
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

    # 设备运行状况 > 查询传感器运行状况
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 传感器运行状况',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('sensor_code', openapi.IN_QUERY, description='传感器编码', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.SensorStatusSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def sensorStatusList(self, request):
        sensor_code = self.request.query_params.get('sensor_code')
        sensor_information = models.sensorStatus.objects.filter(sensor_code=sensor_code)
        total = models.sensorStatus.objects.filter(sensor_code=sensor_code).count()
        result_list = []
        for x in sensor_information:
            result_list.append(
                {
                    'sensor_code': x.sensor_code,
                    'sensor_name': x.sensor_name,
                    'sensor_status': x.sensor_status,
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

    # 设备运行状况 > 查询警告及故障代码
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 警告及故障代码',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('machine_code', openapi.IN_QUERY, description='机床编号', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.FaultCodeSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def faultCodeList(self, request):
        machine_code = self.request.query_params.get('machine_code')
        machine_information = models.faultCode.objects.filter(machine_code=machine_code)
        total = models.faultCode.objects.filter(machine_code=machine_code).count()
        result_list = []
        for x in machine_information:
            result_list.append(
                {
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
            'message': 'successful',
        }
        return JsonResponse(response)

    # 设备运行状况 > 查询机床加工时间热力图
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 机床加工时间热力图',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('machine_code', openapi.IN_QUERY, description='机床编号', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.ThermalDiagramSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def thermalDiagramList(self, request):
        machine_code = self.request.query_params.get('machine_code')
        machine_information = models.thermalDiagram.objects.filter(machine_code=machine_code)
        total = models.thermalDiagram.objects.filter(machine_code=machine_code).count()
        result_list = []
        for x in machine_information:
            result_list.append(
                {
                    'machine_code': x.machine_code,
                    'machine_name': x.machine_name,
                    'machine_running_time': x.machine_running_time,
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
