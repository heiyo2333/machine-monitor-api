import json
import serial.tools.list_ports
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
        responses={200: openapi.Response('successful', serializer.ConfigAddSerializer)},
        tags=["config"],
    )
    @action(detail=False, methods=['post'])
    def add(self, request):
        id = self.request.data.get('id')
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
        models.systemConfig.objects.create(id=id,
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
        id = self.request.data.get('id')
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
        configuration1.update (id=id,
                               machine_name=machine_name,
                               machine_type=machine_type,
                               machine_description=machine_description,
                               manager=manager,
                               machine_ip=machine_ip,
                               machine_port=machine_port,
                               tool_number=tool_number,
                               database_name=database_name,
                               alarm_data_delay_positive=alarm_data_delay_positive,
                               alarm_data_delay_negative=alarm_data_delay_negative,)
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
        models.systemConfig.objects.filter(configuration_number_id=config_id).delete()
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
    def information(self, request):
        config_id = self.request.query_params.get("config_id")
        configuration1 = models.systemConfig.objects.get(id=config_id)
        data = {
                'id':configuration1.id,
                'machine_name':configuration1.machine_name,
                'machine_type':configuration1.machine_type,
                'machine_description':configuration1.machine_description,
                'manager':configuration1.manager,
                'machine_ip':configuration1.machine_ip,
                'machine_port':configuration1.machine_port,
                'tool_number':configuration1.tool_number,
                'database_name':configuration1.database_name,
                'alarm_data_delay_positive':configuration1.alarm_data_delay_positive,
                'alarm_data_delay_negative':configuration1.alarm_data_delay_negative,
                }
        response = {
            'data': data,
            'status': 200,
            'message': '配置信息，显示成功',
        }
        return JsonResponse(response)


















