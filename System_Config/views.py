import json
import os
import socket
import serial.tools.list_ports
from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import action, api_view
from rest_framework import status
import Method_Config
from Method_Config.models import componentConfig
from . import models, serializer
from .serializer import ConfigListSerializer, ConfigInformationSerializer, channelListSerializer, \
    ConfigUpdateSerializer, sensorUpdateserializer
from .models import sensorConfig, channelConfig

def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


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
        responses={200: openapi.Response('successful', serializer.ConfigAddSerializer)},
        tags=["config"],
    )
    @action(detail=False, methods=['post'])
    def addConfig(self, request):
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
        machine_image = self.request.data.get('machine_image')
        if machine_image.name.endswith('.png'):
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
                                               alarm_data_delay_negative=alarm_data_delay_negative,
                                               machine_image=machine_image)
            response = {
                'status': 200,
                'message': '新增配置成功'
            }
            return JsonResponse(response)
        else:
            return JsonResponse({'status': 500, 'message': 'Image file must be in PNG format'})
    #修改配置
    @swagger_auto_schema(
        operation_summary='修改配置',
        request_body=serializer.ConfigUpdateSerializer,
        responses={200: '配置修改成功'},
        tags=["config"],
    )
    @action(detail=False, methods=['post'])
    def configUpdate(self, request):
        serializer = ConfigUpdateSerializer(data=request.data)
        if serializer.is_valid():
            config_id = serializer.validated_data['config_id']
            machine_code = serializer.validated_data['machine_code']
            machine_name = serializer.validated_data['machine_name']
            machine_type = serializer.validated_data['machine_type']
            machine_description = serializer.validated_data['machine_description']
            manager = serializer.validated_data['manager']
            machine_ip = serializer.validated_data['machine_ip']
            machine_port = serializer.validated_data['machine_port']
            tool_number = serializer.validated_data['tool_number']
            database_name = serializer.validated_data['database_name']
            alarm_data_delay_positive = serializer.validated_data['alarm_data_delay_positive']
            alarm_data_delay_negative = serializer.validated_data['alarm_data_delay_negative']
            machine_image = serializer.validated_data.get('machine_image')
            systemconfig = models.systemConfig.objects.get(id=config_id)
            # 更新图片文件
            if machine_image and machine_image.name.endswith('.png'):
                # 删除现有文件
                if systemconfig.machine_image and os.path.isfile(systemconfig.machine_image.path):
                    os.remove(systemconfig.machine_image.path)
                # 生成新的文件名
                _, file_extension = os.path.splitext(machine_image.name)
                new_image_name = f"{systemconfig.machine_code}-机床-{get_random_string(8)}{file_extension}"
                # 保存新的图片文件
                systemconfig.machine_image.save(new_image_name, ContentFile(machine_image.read()), save=True)
            else:
                return JsonResponse({'status': 500, 'message': 'Image file is required'})
            # 更新其他字段
            systemconfig.machine_code = machine_code
            systemconfig.machine_name = machine_name
            systemconfig.machine_type = machine_type
            systemconfig.machine_description = machine_description
            systemconfig.manager = manager
            systemconfig.machine_ip = machine_ip
            systemconfig.machine_port = machine_port
            systemconfig.tool_number = tool_number
            systemconfig.database_name = database_name
            systemconfig.alarm_data_delay_positive = alarm_data_delay_positive
            systemconfig.alarm_data_delay_negative = alarm_data_delay_negative
            systemconfig.save()
            response = {
                'status': 200,
                'message': '修改配置成功'
            }
            return JsonResponse(response)
        else:
            return JsonResponse({
                'status': 500,
                'message': '数据无效'
            })
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
        id = g.validated_data.get('id')
        sensor_configs = models.sensorConfig.objects.filter(config_id=id)
        for sensor_config in sensor_configs:
            channels=models.channelConfig.objects.filter(channel=sensor_config)
            if channels.filter(is_monitor=True).exists():
                return JsonResponse({'status': 500, 'message': '不能删除，存在正在监控的通道配置'})

            # 方法2：if models.channelConfig.objects.filter(channel=sensor_config, is_monitor=True).exists():
            #     return JsonResponse({'status': 500, 'message': '不能删除，存在正在监控的通道配置'}):
            else:
                models.sensorConfig.objects.filter(config_id=id).delete()
        models.systemConfig.objects.filter(id=id).delete()
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
        h = serializer.ConfigApplySerializer(data=request.data)
        if h.is_valid():
            config_id = h.validated_data.get('id')
            if not models.systemConfig.objects.filter(id=config_id).exists():
                return JsonResponse({'status': 500, 'message': '配置ID不存在'}, status=400)
            models.systemConfig.objects.all().update(is_apply=False)
            models.systemConfig.objects.filter(id=config_id).update(is_apply=True)
            response = {
                'status': 200,
                'message': '应用配置成功'
            }
            return JsonResponse(response)
        else:
            return JsonResponse({
                'status': 500,
                'message': '数据无效'
            })
    #拉取配置信息
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
                    'machine_name':i.machine_name,
                    'machine_code':i.machine_code
                }
            )
            count += 1
        response = {
            'data': {'list': list, 'total': b},
            'status': 200,
            'message': '配置列表获取成功',
        }
        return JsonResponse(response)
    #查询配置信息
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
        if not models.systemConfig.objects.filter(id=config_id).exists():
            return JsonResponse({'status': 500, 'message': '配置ID不存在'})
        else:
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
                'machine_image': f"http://{get_local_ip()}:8000"+configuration1.machine_image.url if configuration1.machine_image else None
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
            openapi.Parameter('config_id', openapi.IN_QUERY, description='系统配置id', type=openapi.TYPE_INTEGER,
                              required=False),
        ],
        responses={200: openapi.Response('successful', serializer.sensorQuerysserializer)},
        tags=["sensor"],
    )
    @action(detail=False, methods=['get'])
    def sensorDisplay(self, request):
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        config_id=self.request.query_params.get('config_id')
        first = (current - 1) * pageSize
        last = current * pageSize
        sensor = self.sensor_get_queryset()
        if config_id:
            sensor = sensor.filter(config_id=config_id)
        sensor_magazine_all = sensor.all()[first:last]
        total = sensor.all().count()
        result_list = []
        for x in sensor_magazine_all:
            result_list.append(
                {
                    'sensor_code':  x.sensor_code,
                    'sensor_name': x.sensor_name,
                    'frequency': x.frequency,
                    'channel_number': x.channel_number,
                    'sensor_status': x.sensor_status,
                    'remark': x.remark,
                    'machine_code': x.machine_code,
                    'machine_name': x.machine_name,
                    'config_id': x.config_id,
                    'sensor_image': f"http://{get_local_ip()}:8000"+x.sensor_image.url if x.sensor_image else None
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
        request_body=serializer.sensorUpdateserializer,
        responses={200: openapi.Response('successful', serializer.sensorUpdateserializer)},
        tags=["sensor"],
    )
    @action(detail=False, methods=['post'])
    def addSensor(self, request):
        sensor_code = self.request.data.get('sensor_code')
        sensor_name = self.request.data.get('sensor_name')
        frequency = self.request.data.get('frequency')
        channel_number = self.request.data.get('channel_number')
        remark = self.request.data.get('remark')
        # channel_name = self.request.data.get('channel_name')
        # overrun_times = self.request.data.get('overrun_times')
        # channel_field = self.request.data.get('channel_field')
        sensor_image = self.request.data.get('sensor_image')
        machine_name=self.request.data.get('machine_name')
        machien_code=self.request.data.get('machien_code')
        config_id = self.request.data.get('config_id')
        if sensor_image.name.endswith('.png'):
            sensor_instance = models.sensorConfig.objects.create(sensor_code=sensor_code,
                                                                 sensor_name=sensor_name,
                                                                 frequency=frequency,
                                                                 channel_number=channel_number,
                                                                 remark=remark,
                                                                 sensor_image=sensor_image,
                                                                 machine_name=machine_name,
                                                                 machine_code=machien_code,
                                                                 config_id=config_id
                                                                 )
            for m in range(1, int(channel_number) + 1):
                models.channelConfig.objects.create(
                    channel_id=sensor_instance.id
                )
            response = {
                'status': 200,
                'message': '传感器新增成功'
            }
            return JsonResponse(response)
        else:
            return JsonResponse({'status': 500, 'message': 'Image file must be in PNG format'})
    #传感器编辑
    @swagger_auto_schema(
        operation_summary='传感器-编辑',
        request_body=serializer.sensorUpdateserializer,
        responses={200: 'successful'},
        tags=["sensor"],
    )
    @action(detail=False, methods=['post'])
    def sensorUpdate(self, request):
        serializer = sensorUpdateserializer(data=request.data)
        if serializer.is_valid():
            sensor_code = serializer.validated_data['sensor_code']
            sensor_name = serializer.validated_data['sensor_name']
            frequency = serializer.validated_data['frequency']
            channel_number = serializer.validated_data['channel_number']
            remark = serializer.validated_data.get('ramark')
            sensor_image = serializer.validated_data['sensor_image']
            machine_name = serializer.validated_data['machine_name']
            machine_code=serializer.validated_data['machine_code']
            config_id = serializer.validated_data['config_id']
            sensor = models.sensorConfig.objects.get(sensor_code=sensor_code)
            if sensor_image and sensor_image.name.endswith('.png'):
                # 删除现有文件
                if sensor.sensor_image and os.path.isfile(sensor.sensor_image.path):
                    os.remove(sensor.sensor_image.path)
                # 生成新的文件名
                _, file_extension = os.path.splitext(sensor_image.name)
                new_image_name = f"{sensor.sensor_code}-传感器-"
                # 保存新的图片文件
                sensor.sensor_image.save(new_image_name, ContentFile(sensor_image.read()), save=True)
            else:
                return JsonResponse({'status': 500, 'message': 'Image file is required'})
            # 更新其他字段
            sensor.sensor_code = sensor_code
            sensor.sensor_name = sensor_name
            sensor.frequency = frequency
            sensor.channel_number = channel_number
            sensor.remark=remark
            sensor.machine_code = machine_code
            sensor.machine_name = machine_name
            sensor.config_id = config_id
            sensor.save()
            response = {
                'status': 200,
                'message': '修改成功'
            }
            return JsonResponse(response)

        else:
            return JsonResponse({
                'status': 500,
                'message': '数据无效'
            })

    #传感器删除
    @swagger_auto_schema(
        operation_summary='传感器-删除',
        request_body=serializer.sensorDeleteserializer,
        responses={200: '删除成功'},
        tags=["sensor"],
    )
    @action(detail=False, methods=['post'])
    def sensorDelete(self, request):
        g = serializer.sensorDeleteserializer(data=request.data)
        g.is_valid()
        id = g.validated_data.get('id')
        channels = models.channelConfig.objects.filter(channel=id)
        if channels.filter(is_monitor=True).exists():
            return JsonResponse({'status': 500, 'message': '不能删除，存在正在监控的通道配置'},)

        else:
            models.sensorConfig.objects.filter(id=id).delete()
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
        h = serializer.monitor_onSerializer(data=request.data)
        h.is_valid()
        id = h.validated_data.get('id')
        # 检查记录是否已经在监控状态
        channel = models.channelConfig.objects.get(id=id)
        if channel.is_monitor:
            response = {
                'status': 400,
                'message': '该通道已经在监控状态'
            }
            return JsonResponse(response)
        else:
            # 更新记录为监控状态
            channel.is_monitor = True
            channel.save()
            sensorconfig = channel.channel  # 主表实例
            sensorconfig.sensor_status = 1
            sensorconfig.save()
            response = {
                'status': 200,
                'message': '开始监控成功'
            }
            return JsonResponse(response)

    #结束监控
    @swagger_auto_schema(
        operation_summary='结束监控',
        request_body=serializer.monitor_offSerializer,
        responses={200: '结束监控'},
        tags=["channel"],
    )
    @action(detail=False, methods=['post'])
    def monitor_off(self, request):
        h = serializer.monitor_offSerializer(data=request.data)
        h.is_valid()
        id = h.validated_data.get('id')
        channel = models.channelConfig.objects.get(id=id)

        if not channel.is_monitor:
            response = {
                'status': 500,
                'message': '该通道已经处于非监控状态'
            }
            return JsonResponse(response)
        else:
            # 更新记录为非监控状态
            channel.is_monitor = False
            channel.save()
            sensorconfig = channel.channel  #主表实例
            sensorconfig.sensor_status = 0
            sensorconfig.save()
            response = {
                'status': 200,
                'message': '结束监控成功'
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
    #通道配置显示
    @swagger_auto_schema(
        operation_summary='通道配置-显示',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('sensor_code', openapi.IN_QUERY, description='传感器编号',
                              type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: openapi.Response('传感器通道配置信息', channelListSerializer)},
        tags=["channel"],
    )
    @action(detail=False, methods=['get'])
    def channelDisplay(self, request):
        sensor_code = self.request.query_params.get("sensor_code")
        configuration = models.sensorConfig.objects.get(sensor_code=sensor_code)
        channel_info = configuration.channelconfig_set.all()
        list = []
        for channel in channel_info:
            print(channel.channel_name)
            list.append({
                'sensor_name': channel.sensor_name,
                'channel_name': channel.channel_name,
                'overrun_times': channel.overrun_times,
                'channel_field': channel.channel_field,
                'is_monitor': channel.is_monitor,
            })
        response = {
            'list': list,
            'status': 200,
            'message': '通道配置信息',
        }
        return JsonResponse(response)
