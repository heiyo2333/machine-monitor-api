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


class SystemConfigViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)
    parser_classes = (MultiPartParser, FormParser)

    # 返回数据库所有对象
    def get_queryset(self):
        return models.SystemConfiguration.objects.all()

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
