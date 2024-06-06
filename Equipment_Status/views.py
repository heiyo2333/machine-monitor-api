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

import Method_Config
import System_Config
from . import models, serializer


class EquipmentStatusViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)
    parser_classes = (MultiPartParser, FormParser)

    # 返回数据库所有对象.
    def get_queryset(self):
        return models.machineStatus.objects.all()

    # 设备运行状况 > 机床选择下拉框
    @swagger_auto_schema(operation_summary='设备运行状况 > 机床选择下拉框',
                         responses={200: 'Successful'},
                         tags=["EquipmentStatus"], )
    @action(detail=False, methods=['get'])
    def machineSelect(self, request):
        query = System_Config.models.systemConfig.objects.all()
        request_list = []
        for i in query:
            request_list.append({
                'id': i.id,
                'machine_code': i.machine_code,
                'machine_name': i.machine_name,
            })
        response_list = {
            'list': request_list,
        }
        response = {
            'data': response_list,
            'message': 'Successful',
            'status': 200,
        }
        return JsonResponse(response)

    # 设备运行状况 > 查询机床运行状况
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 机床运行状况',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.EquipmentStatusSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def machineStatusList(self, request):
        id = self.request.query_params.get('id')
        machine_all = Method_Config.models.componentConfig.objects.filter(config_id=id)
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

    # 设备运行状况 > 部件选择下拉框
    @swagger_auto_schema(operation_summary='设备运行状况 > 部件选择下拉框',
                         # 获取参数
                         manual_parameters=[openapi.Parameter('id', openapi.IN_QUERY, description='机床配置表id',
                                                              type=openapi.TYPE_INTEGER, required=True), ],
                         responses={200: openapi.Response('successful', serializer.componentSerializer)},
                         tags=["EquipmentStatus"], )
    @action(detail=False, methods=['get'])
    def componentSelect(self, request):
        systemConfig_id = self.request.query_params.get('id')
        component_Config = Method_Config.models.componentConfig.objects.filter(config_id=systemConfig_id)
        request_list = []
        for i in component_Config:
            request_list.append({
                'id': i.id,
                'machine_name': i.machine_name,
                'component_name': i.component_name,
            })
        response_list = {
            'list': request_list,
        }
        response = {
            'data': response_list,
            'message': 'Successful',
            'status': 200,
        }
        return JsonResponse(response)

    # 设备运行状况 > 查询传感器运行状况
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 传感器运行状况',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.SensorStatusSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def sensorStatusList(self, request):
        component_id = self.request.query_params.get('id')
        sensor_information = System_Config.models.channelConfig.objects.filter(channel_id=component_id)
        # total = sensor_information.count()
        result_list = []
        for x in sensor_information:
            result_list.append(
                {
                    'id': x.id,
                    'sensor_name': x.sensor_name,
                    'operational_status': x.operational_status,
                }
            )
        response_list = {
            'list': result_list,
            # 'total': total,
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
            openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.FaultCodeSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def faultCodeList(self, request):
        id = self.request.query_params.get('id')
        machineConfig = models.faultCode.objects.filter(config_id=id)
        total = machineConfig.count()
        result_list = []
        for x in machineConfig:
            result_list.append(
                {
                    'id': x.id,
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
            openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.ThermalDiagramSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def thermalDiagramList(self, request):
        id = self.request.query_params.get('id')
        machine_information = models.thermalDiagram.objects.filter(config_id=id)
        result_list = []
        for x in machine_information:
            result_list.append(
                {
                    'id': x.id,
                    'machine_name': x.machine_name,
                    'machine_running_time': x.machine_running_time,
                }
            )
        response_list = {
            'list': result_list,
        }
        response = {
            'data': response_list,
            'status': 200,
            'message': 'successful',
        }
        return JsonResponse(response)

    # 设备运行状况 > 部件树
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 部件树',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.ComponentTreeSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['get'])
    def componentTreeList(self, request):
        id = self.request.query_params.get('id')
        machine_information = Method_Config.models.componentConfig.objects.filter(config_id=id)
        result_list = []
        for x in machine_information:
            result_list.append(
                {
                    'id': x.id,
                    'machine_name': x.machine_name,
                    'component_name': x.component_name,
                }
            )
        response_list = {
            'list': result_list,
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
            openapi.Parameter('id', openapi.IN_QUERY, description='部件配置表的id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.ComponentTreeSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['post'])
    def monitor_on(self, request):
        id = self.request.query_params.get('id')
        # 检查记录是否已经在监控状态
        try:
            machineStatus = Method_Config.models.componentConfig.objects.get(id=id)
            if machineStatus.monitor_status:
                response = {
                    'status': 400,
                    'message': '该部件已经在监控状态'
                }
                return JsonResponse(response)
            else:
                # 更新记录为监控状态
                machineStatus.monitor_status = True
                machineStatus.save()
                response = {
                    'status': 200,
                    'message': '开始监控成功'
                }
                return JsonResponse(response)
        except Method_Config.models.machineStatus.DoesNotExist:
            response = {
                'status': 404,
                'message': '未找到该通道'
            }
            return JsonResponse(response)

    # 结束监控
    @swagger_auto_schema(
        operation_summary='结束监控',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='部件配置表的id', type=openapi.TYPE_INTEGER,
                              required=True), ],
        responses={200: openapi.Response('successful', serializer.ComponentTreeSerializer)},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['post'])
    def monitor_off(self, request):
        id = self.request.query_params.get('id')
        try:
            machineStatus = Method_Config.models.componentConfig.objects.get(id=id)
            if not machineStatus.monitor_status:
                response = {
                    'status': 400,
                    'message': '该通道已经处于非监控状态'
                }
                return JsonResponse(response)
            else:
                # 更新记录为非监控状态
                machineStatus.monitor_status = False
                machineStatus.save()
                response = {
                    'status': 200,
                    'message': '结束监控成功'
                }
                return JsonResponse(response)
        except Method_Config.models.machineStatus.DoesNotExist:
            response = {
                'status': 404,
                'message': '未找到该通道'
            }
            return JsonResponse(response)

    # 设备运行状况 > 警告及故障代码填写
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 警告及故障代码填写',
        request_body=serializer.AddFaultCodeSerializer,
        responses={200: '警告及故障代码填写成功'},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['post'])
    def addFaultCode(self, request):
        config_id = self.request.data.get('config_id')  # 机床系统配置的id
        config_X = Method_Config.models.componentConfig.objects.get(config_id=config_id)  # 根据config_id找的"部件配置_X"的一行数据
        machine_code = config_X.machine_code  # 根据"部件配置X"查的机床编码
        machine_name = config_X.machine_name  # 根据"部件配置X"查的机床名称
        component_name = config_X.component_name  # 根据"部件配置X"查的部件名称
        warning_time = self.request.data.get('warning_time')  # 警告时间
        fault_type = self.request.data.get('fault_type')  # 报警类型
        fault_code = self.request.data.get('fault_code')  # 报警代码

        new_faultCode = models.faultCode.objects.create(config_id=config_id,
                                                        machine_code=machine_code,
                                                        machine_name=machine_name,
                                                        warning_time=warning_time,
                                                        component_name=component_name,
                                                        fault_type=fault_type,
                                                        fault_code=fault_code, )
        response = {
            'id': new_faultCode.id,
            'status': 200,
            'message': '警告及故障代码填写成功'
        }
        return JsonResponse(response)

    # 设备运行状况 > 机床加工时间填写
    @swagger_auto_schema(
        operation_summary='设备运行状况 > 机床加工时间填写',
        request_body=serializer.AddThermalDiagramSerializer,
        responses={200: '机床加工时间填写成功'},
        tags=["EquipmentStatus"],
    )
    @action(detail=False, methods=['post'])
    def addThermalDiagram(self, request):
        config_id = self.request.data.get('config_id')  # 机床系统配置的id
        config_X = System_Config.models.systemConfig.objects.get(id=config_id)  # 根据config_id找的"部件配置_X"的一行数据
        machine_code = config_X.machine_code
        machine_name = config_X.machine_name  # 根据"部件配置X"查的机床名称
        machine_time = self.request.data.get('machine_time')  # 机床工作日期
        machine_running_time = self.request.data.get('machine_running_time')  # 机床加工时间

        new_thermalDiagram = models.thermalDiagram.objects.create(config_id=config_id,
                                                                  machine_code=machine_code,
                                                                  machine_name=machine_name,
                                                                  machine_time=machine_time,
                                                                  machine_running_time=machine_running_time,)
        response = {
            'id': new_thermalDiagram.id,
            'status': 200,
            'message': '机床加工时间填写成功'
        }
        return JsonResponse(response)
