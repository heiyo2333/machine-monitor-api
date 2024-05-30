import json
import serial.tools.list_ports
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action

from . import models, serializer
from .serializer import ConfigListSerializer, ConfigInformationSerializer


class SystemConfigViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)
    parser_classes = (MultiPartParser, FormParser)

    # 返回数据库所有对象
    def get_queryset(self):
        return models.systemConfig.objects.all()

    # 新增配置
    @swagger_auto_schema(
        operation_summary='新增配置',
        request_body=serializer.ConfigAddSerializer,
        responses={200: openapi.Response('successful', serializer.ConfigAddSerializer), 500: '该id已存在'},
        tags=["config"],
    )
    @action(detail=False, methods=['post'])
    def addConfig(self, request):
        id = self.request.data.get('id')
        if models.systemConfig.objects.filter(id=id).count() != 0:
            response = {
                'status': 500,
                'message': '该id已存在'
            }
            return JsonResponse(response)
        machine_code = self.request.data.get('machine_code')
        machine_name = self.request.data.get('machine_name')
        machine_type = self.request.data.get('machine_type')
        machine_description = self.request.data.get('machine_description')
        manager = self.request.data.get('manager')
        machine_ip = self.request.data.get('machine_ip')
        machine_port = self.request.data.get('machine_port')
        tool_number = self.request.data.get('tool_number')
        database_name = self.request.data.get('database_name')
        alarm_data_delay_positive = self.request.data.get('alarm_data_delay_positive')
        alarm_data_delay_negative = self.request.data.get('alarm_data_delay_negative')
        models.systemConfig.objects.create(machine_code=machine_code,
                                           machine_name=machine_name,
                                           machine_type=machine_type,
                                           machine_description=machine_description,
                                           manager=manager,
                                           machine_ip=machine_ip,
                                           machine_port=machine_port,
                                           tool_number=tool_number,
                                           database_name=database_name,
                                           alarm_data_delay_positive=alarm_data_delay_positive,
                                           alarm_data_delay_negative=alarm_data_delay_negative, )
        response = {
            'status': 200,
            'message': '新增配置成功'
        }
        return JsonResponse(response)

    #修改配置
    @swagger_auto_schema(
        operation_summary='修改配置',
        request_body=serializer.ConfigUpdateSerializer,
        responses={200: '配置修改成功'},
        tags=["config"],
    )
    @action(detail=False, methods=['post'])
    def configUpdate(self, request):
        config_id = self.request.data.get('config_id')
        machine_code = self.request.data.get('machine_code')
        machine_name = self.request.data.get('machine_name')
        machine_type = self.request.data.get('machine_type')
        machine_description = self.request.data.get('machine_description')
        manager = self.request.data.get('manager')
        machine_ip = self.request.data.get('machine_ip')
        machine_port = self.request.data.get('machine_port')
        tool_number = self.request.data.get('tool_number')
        database_name = self.request.data.get('database_name')
        alarm_data_delay_positive = self.request.data.get('alarm_data_delay_positive')
        alarm_data_delay_negative = self.request.data.get('alarm_data_delay_negative')
        configuration1 = models.systemConfig.objects.filter(id=config_id)
        configuration2 = models.systemConfig.objects.get(id=config_id)
        configuration1.update(machine_code=machine_code,
                              machine_name=machine_name,
                              machine_type=machine_type,
                              machine_description=machine_description,
                              manager=manager,
                              machine_ip=machine_ip,
                              machine_port=machine_port,
                              tool_number=tool_number,
                              database_name=database_name,
                              alarm_data_delay_positive=alarm_data_delay_positive,
                              alarm_data_delay_negative=alarm_data_delay_negative, )
        response = {
            'status': 200,
            'message': '修改配置成功'
        }
        return JsonResponse(response)

    # 删除配置
    @swagger_auto_schema(
        operation_summary='删除配置',
        request_body=serializer.ConfigDeleteSerializer,
        responses={200: '删除配置成功'},
        tags=["config"],
    )
    @action(detail=False, methods=['post'])
    def delete(self, request):
        g = serializer.ConfigDeleteSerializer(data=request.data)
        g.is_valid()
        config_id = g.validated_data.get('config_id')
        print(config_id)
        models.systemConfig.objects.filter(id=config_id).delete()
        response = {
            'status': 200,
            'message': '删除配置成功'
        }
        return JsonResponse(response)

    #应用配置
    @swagger_auto_schema(
        operation_summary='应用配置',
        request_body=serializer.ConfigApplySerializer,
        responses={200: '应用配置成功'},
        tags=["config"],
    )
    @action(detail=False, methods=['post'])
    def apply(self, request):
        h = serializer.ConfigDeleteSerializer(data=request.data)
        h.is_valid()
        config_id = h.validated_data.get('config_id')
        models.systemConfig.objects.all().update(is_apply=False)
        models.systemConfig.objects.filter(id=config_id).update(is_apply=True)

        response = {
            'status': 200,
            'message': '应用配置成功'}
        return JsonResponse(response)

    #获取数据列表
    @swagger_auto_schema(
        operation_summary='获取配置列表',
        responses={200: openapi.Response('配置列表获取成功', ConfigListSerializer)},
        tags=["config"],
    )
    @action(detail=False, methods=['get'])
    def configList(self, request):
        list = []
        a = models.systemConfig.objects.all()
        b = models.systemConfig.objects.count()
        count = 1
        for i in a:
            list.append(
                {
                    "label": f'配置{count}',
                    'key': i.id,
                    'is_apply': i.is_apply,
                }
            )
            count += 1
        response = {
            'data': {'list': list, 'total': b},
            'status': 200,
            'message': '配置列表获取成功',
        }
        return JsonResponse(response)

    #系统配置信息
    @swagger_auto_schema(
        operation_summary='配置信息',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='系统配置id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('配置信息显示成功', ConfigInformationSerializer)},
        tags=["config"],
    )
    @action(detail=False, methods=['get'])
    def configDisplay(self, request):
        config_id = self.request.query_params.get("config_id")
        configuration1 = models.systemConfig.objects.get(id=config_id)
        data = {
            'id': configuration1.id,
            'machine_code': configuration1.machine_code,
            'machine_name': configuration1.machine_name,
            'machine_type': configuration1.machine_type,
            'machine_description': configuration1.machine_description,
            'manager': configuration1.manager,
            'machine_ip': configuration1.machine_ip,
            'machine_port': configuration1.machine_port,
            'tool_number': configuration1.tool_number,
            'database_name': configuration1.database_name,
            'alarm_data_delay_positive': configuration1.alarm_data_delay_positive,
            'alarm_data_delay_negative': configuration1.alarm_data_delay_negative,
        }
        response = {
            'data': data,
            'status': 200,
            'message': '配置信息，显示成功',
        }
        return JsonResponse(response)

    def sensor_get_queryset(self):
        return models.sensorConfig.objects.all()

    #传感器查询
    @swagger_auto_schema(
        operation_summary='传感器 > 查询',
        # 获取参数
        manual_parameters=[

            openapi.Parameter('pageSize', openapi.IN_QUERY, description='一页多少条', type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('current', openapi.IN_QUERY, description='当前页面号', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.sensorSerializer)},
        tags=["sensor"],
    )
    @action(detail=False, methods=['get'])
    def sensorDisplay(self, request):

        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        first = (current - 1) * pageSize
        last = current * pageSize
        sensor = self.sensor_get_queryset()
        sensor_magazine_all = sensor.all()[first:last]
        total = sensor.all().count()
        result_list = []
        for x in sensor_magazine_all:
            result_list.append(
                {
                    'sensor_code': x.sensor_code,
                    'sensor_name': x.sensor_name,
                    'frequency': x.frequency,
                    'channel_number': x.channel_number,
                    'sensor_status': x.sensor_status,
                    'remark': x.remark
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

    #传感器新增
    @swagger_auto_schema(
        operation_summary='传感器-新增',
        request_body=serializer.sensorSerializer,
        responses={200: openapi.Response('successful', serializer.sensorSerializer), 500: '该id已存在'},
        tags=["sensor"],
    )
    @action(detail=False, methods=['post'])
    def addSensor(self, request):
        sensor_code = self.request.data.get('sensor_code')
        sensor_name = self.request.data.get('sensor_name')
        frequency = self.request.data.get('frequency')
        channel_number = self.request.data.get('channel_number')
        remark = self.request.data.get('remark')
        models.sensorConfig.objects.create(sensor_code=sensor_code,
                                           sensor_name=sensor_name,
                                           frequency=frequency,
                                           channel_number=channel_number,
                                           remark=remark
                                           )
        response = {
            'status': 200,
            'message': '传感器新增成功'
        }
        return JsonResponse(response)

    #传感器编辑
    @swagger_auto_schema(
        operation_summary='传感器-编辑',
        request_body=serializer.sensorUpdateserializer,
        responses={200: 'successful'},
        tags=["sensor"],
    )
    @action(detail=False, methods=['post'])
    def sensorUpdate(self, request):
        sensor_code = self.request.data.get('sensor_code')
        sensor_name = self.request.data.get('sensor_name')
        frequency = self.request.data.get('frequency')
        channel_number = self.request.data.get('channel_number')
        remark = self.request.data.get('remark')
        configuration1 = models.sensorConfig.objects.filter(sensor_code=sensor_code)
        configuration2 = models.sensorConfig.objects.get(sensor_code=sensor_code)
        configuration1.update(sensor_code=sensor_code,
                              sensor_name=sensor_name,
                              frequency=frequency,
                              channel_number=channel_number,
                              remark=remark
                              )
        response = {
            'status': 200,
            'message': '修改成功'
        }
        return JsonResponse(response)

    #传感器删除
    @swagger_auto_schema(
        operation_summary='传感器-删除',
        request_body=serializer.sensorDeleteserializer,
        responses={200: '删除成功'},
        tags=["sensor"],
    )
    @action(detail=False, methods=['post'])
    def delete(self, request):
        g = serializer.sensorDeleteserializer(data=request.data)
        g.is_valid()
        sensor_code = g.validated_data.get('sensor_code')
        print(sensor_code)
        models.sensorConfig.objects.filter(sensor_code=sensor_code).delete()
        response = {
            'status': 200,
            'message': '删除成功'
        }
        return JsonResponse(response)

    #开始监控
    @swagger_auto_schema(
        operation_summary='开始监控',
        request_body=serializer.monitor_onSerializer,
        responses={200: '开始监控'},
        tags=["channel"],
    )
    @action(detail=False, methods=['post'])
    def monitor_on(self, request):
        is_monitor = self.request.data.get('is_monitor')=='True'
        channel_name = self.request.data.get('channel_name')
        configuration1 = models.channelConfig.objects.filter(channel_name=channel_name)
        #configuration2 = models.channelConfig.objects.get(channel_name=channel_name)
        configuration1.update(channel_name=channel_name,
                              is_monitor=is_monitor,
                              )
        response = {
            'status': 200,
            'message': '开始监控'
        }
        return JsonResponse(response)

    #通道配置编辑
    @swagger_auto_schema(
        operation_summary='通道配置-编辑',
        request_body=serializer.channelConfigSerializer,
        responses={200: 'successful'},
        tags=["channel"],
    )
    @action(detail=False, methods=['post'])
    def channelConfigupdate(self, request):
        sensor_name = self.request.data.get('sensor_code')
        channel_name = self.request.data.get('channel_name')
        overrun_times = self.request.data.get('overrun_times')
        channel_field = self.request.data.get('channel_field')

        configuration = models.channelConfig.objects.filter(sensor_name=sensor_name)
        configuration.update(channel_name=channel_name,
                              overrun_times=overrun_times,
                              channel_field=channel_field,
                              )
        response = {
            'status': 200,
            'message': '修改成功'
        }
        return JsonResponse(response)


