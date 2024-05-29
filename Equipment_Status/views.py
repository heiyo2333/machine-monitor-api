import time

from django.db.models import Q, Max
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from rest_framework.decorators import action
from datetime import datetime
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication

from . import models, serializer


class EquipmentStatusViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)

    # 返回数据库所有对象.
    def get_queryset(self):
        return models.machineStatus.objects.all()

    # 设备运行状况查询
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 机床运行状况',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('machine_number', openapi.IN_QUERY, description='机床编号', type=openapi.TYPE_STRING,
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
        # cutter_type = self.request.query_params.get('cutterType')
        # cutter_material = self.request.query_params.get('cutterMaterial')
        # cutter_brand = self.request.query_params.get('cutterBrand')
        # cutter_status = self.request.query_params.get('cutterStatus')
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        first = (current - 1) * pageSize
        last = current * pageSize
        machine = self.get_queryset()
        machine_all = machine[first:last]
        total = machine.count()
        result_list = []
        for x in machine_all:
            result_list.append(
                {
                    'machine_number': x.machine_number,
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

    # 机床运行物理量查询
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 机床工作参数状况',
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
        total = models.monitorValue.objects.filter(value_name=value_name).count()
        result_list = []
        for x in total:
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

    # 传感器运行状况查询
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 传感器运行状况',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('sensor_name', openapi.IN_QUERY, description='传感器名称', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.SensorStatusSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def sensorStatusList(self, request):
        sensor_name = self.request.query_params.get('sensor_name')
        total = models.monitorValue.objects.filter(sensor_name=sensor_name).count()
        result_list = []
        for x in total:
            result_list.append(
                {
                    'sensor_number': x.sensor_number,
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

    # 警告及故障代码查询
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 警告及故障代码',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('machine_number', openapi.IN_QUERY, description='机床编号', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.FaultCodeSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def faultCodeList(self, request):
        machine_number = self.request.query_params.get('machine_number')
        total = models.monitorValue.objects.filter(machine_number=machine_number).count()
        result_list = []
        for x in total:
            result_list.append(
                {
                    'machine_number': x.machine_number,
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

    # 机床加工时间热力图查询
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 机床加工时间热力图',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('machine_number', openapi.IN_QUERY, description='机床编号', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.ThermalDiagramSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def thermalDiagramList(self, request):
        machine_number = self.request.query_params.get('machine_number')
        total = models.monitorValue.objects.filter(machine_number=machine_number).count()
        result_list = []
        for x in total:
            result_list.append(
                {
                    'machine_number': x.machine_number,
                    'machine_name': x.machine_name,
                    'machine_running_time': x.value_name,
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
