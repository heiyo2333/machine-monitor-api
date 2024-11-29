import ast
import json
import os
import socket
import threading
from datetime import datetime, timedelta
import re
from io import BytesIO

import pandas as pd
import requests
from dateutil import parser
from django.core.files.base import ContentFile
from django.db.models import Max, Q
from django.http import JsonResponse, HttpResponse
from django.utils.http import urlquote
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from influxdb import InfluxDBClient
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from pypinyin import lazy_pinyin, Style

from . import models, serializer
import systemConfig
from .models import algorithmConfig
from .serializer import addComponentSerializer


def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip



def get_initials(name):
    # 将算法名称转换为拼音
    pinyin_list = lazy_pinyin(name)

    # 过滤掉空字符串，并获取每个拼音的首字母
    initials = ''.join([item[0].upper() for item in pinyin_list if item])

    return initials


def algorithm_code_rule(algorithm_name,algorithm_type):
    prefix = f'SF-{get_initials(algorithm_name)}-{algorithm_type}'
    # 获取已存在的最大编码值
    max_existing_number = models.algorithmConfig.objects.filter(algorithm_code__startswith=prefix).aggregate(
        Max('algorithm_code'))
    max_number = max_existing_number['algorithm_code__max']

    # 如果存在已有编码，则在其基础上递增，否则从001开始
    if max_number:
        new_number = str(int(max_number[-2:]) + 1).zfill(2)
    else:
        new_number = '01'
    # 构建最终编码
    algorithm_code = f'{prefix}{new_number}'

    return algorithm_code


def component_code_rule(component_name):
    prefix = f'BJ-{get_initials(component_name)}-'
    # 获取已存在的最大编码值
    max_existing_number = models.componentConfig.objects.filter(component_code__startswith=prefix).aggregate(
        Max('component_code'))
    max_number = max_existing_number['component_code__max']

    # 如果存在已有编码，则在其基础上递增，否则从001开始
    if max_number:
        new_number = str(int(max_number[-2:]) + 1).zfill(2)
    else:
        new_number = '01'
    # 构建最终编码
    component_code = f'{prefix}{new_number}'

    return component_code


class MethodConfigViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)
    parser_classes = (MultiPartParser, FormParser)

    # 返回数据库所有对象.
    def get_queryset(self):
        return models.algorithmConfig.objects.all()

    # 文件上传
    @swagger_auto_schema(
        operation_summary='上传文件',
        request_body=serializer.uploadFileSerializer,
        responses={200: openapi.Response('successful')},
        tags=["algorithm"],
    )
    @action(detail=False, methods=['post'])
    def uploadFile(self, request):
        file = serializer.uploadFileSerializer(data=request.data)
        if file.is_valid():
            file_url = f"http://{get_local_ip()}:8000" + file.save()

        response = {
            'data': file_url,
            'status': 200,
            'message': '文件上传成功!'
        }
        return JsonResponse(response)

    # 部件配置-算法输入通道
    @swagger_auto_schema(
        operation_summary='算法配置-算法输入通道多级下拉',
        responses={200: openapi.Response('successful')},
        tags=["algorithm"]
    )
    @action(detail=False, methods=['get'])
    def algorithmChannelSelect(self, request):
        config_id = systemConfig.models.systemConfig.objects.get(is_apply=1).id
        components = models.componentConfig.objects.filter(component_status=True, config_id=config_id)
        request_list = []
        for component in components:
            component_list = {
                'value': component.id,
                'label': component.component_name,
                'children': []
            }
            component_sensors = models.componentSensor.objects.filter(component_id=component.id)
            for component_sensor in component_sensors:
                sensor_id = component_sensor.sensor_id
                sensor_name = systemConfig.models.sensorConfig.objects.get(id=sensor_id).sensor_name
                child_sensor = {
                    'value': sensor_id,
                    'label': sensor_name,
                    'children': []
                }
                component_list['children'].append(child_sensor)
                channels = systemConfig.models.channelConfig.objects.filter(sensor=sensor_id)
                for channel in channels:
                    child_channel = {
                        'value': channel.id,
                        'label': channel.channel_name,
                    }
                    child_sensor['children'].append(child_channel)
            request_list.append(component_list)

        response_list = {
            'list': request_list,
            'total': components.count(),
        }
        response = {
            'data': response_list,
            'message': 'Successful',
            'status': 200,
        }
        return JsonResponse(response)

    # 算法配置-显示
    @swagger_auto_schema(
        operation_summary='算法配置-显示',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('pageSize', openapi.IN_QUERY, description='一页多少条', type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('current', openapi.IN_QUERY, description='当前页面号', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.algorithmListSerializer)},
        tags=["algorithm"],
    )
    @action(detail=False, methods=['get'])
    def algorithmDisplay(self, request):
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        first = (current - 1) * pageSize
        last = current * pageSize
        config_id = systemConfig.models.systemConfig.objects.get(is_apply=1).id
        algorithms = models.algorithmConfig.objects.filter(config_id=config_id)[first:last]
        total = algorithms.count()

        ip_address = f"http://{get_local_ip()}:8000"


        # 通道信息列表：algorithm_channels_list

        result_list = []
        for algorithm in algorithms:
            algorithm_channels_list = []
            algorithm_channels = models.algorithmChannel.objects.filter(algorithm_id=algorithm.id)
            for algorithm_channel in algorithm_channels:
                channel = systemConfig.models.channelConfig.objects.get(id=algorithm_channel.channel_id)
                sensor = systemConfig.models.sensorConfig.objects.get(id=channel.sensor_id)
                component_sensor = models.componentSensor.objects.get(sensor=sensor.id)
                component_list = {
                    'value': component_sensor.component.id,
                    'label': component_sensor.component.component_name,
                    'children': []
                }
                sensor_list = {
                    'value': sensor.id,
                    'label': sensor.sensor_name,
                    'children': []
                }
                channel_list = {
                    'value': channel.id,
                    'label': channel.channel_name,
                }
                sensor_list['children'].append(channel_list)
                component_list['children'].append(sensor_list)
                # algorithm_list['children'].append(component_list)
                algorithm_channels_list.append(component_list)

            result_list.append(
                {
                    'id': algorithm.id,
                    'algorithm_code': algorithm.algorithm_code,
                    'algorithm_name': algorithm.algorithm_name,
                    'algorithm_channel_number': algorithm.algorithm_channel_number,
                    'algorithm_channels_list': algorithm_channels_list,
                    'remark': algorithm.remark,
                    'algorithm_file': ip_address + algorithm.algorithm_file.url,
                    # 'algorithm_file': os.path.basename(x.algorithm_file.name),
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

    # 算法配置-新增
    @swagger_auto_schema(
        operation_summary='算法配置-新增',
        request_body=serializer.algorithmSerializer,
        responses={200: openapi.Response('successful', serializer.algorithmSerializer), 500: '该id已存在'},
        tags=["algorithm"],
    )
    @action(detail=False, methods=['post'])
    def addAlgorithm(self, request):
        algorithm_name = self.request.data.get('algorithm_name')
        algorithm_channel_number = self.request.data.get('algorithm_channel_number')
        algorithm_file_path = self.request.data.get('algorithm_file')
        algorithm_channel_str = self.request.data.get('algorithm_channel_matrix')
        remark = self.request.data.get('remark')
        algorithm_type = self.request.data.get('algorithm_type')
        function_name = self.request.data.get('function_name')

        algorithm_channel_matrix = ast.literal_eval(algorithm_channel_str)
        config_id = systemConfig.models.systemConfig.objects.get(is_apply=1).id
        algorithm_code = algorithm_code_rule(algorithm_name,algorithm_type)
        new_algorithm = models.algorithmConfig.objects.create(algorithm_code=algorithm_code,
                                                              algorithm_name=algorithm_name,
                                                              algorithm_channel_number=algorithm_channel_number,
                                                              remark=remark,
                                                              algorithm_type=algorithm_type,
                                                              function_name = function_name,
                                                              config_id=config_id,)
        # 将对应的通道信息放入附表
        for channael_id in algorithm_channel_matrix:
            models.algorithmChannel.objects.create(algorithm=new_algorithm, channel_id=channael_id)
        # 从URL下载文件内容
        response = requests.get(algorithm_file_path)
        file_content = response.content
        # 将内容转换为ContentFile对象
        file_obj = ContentFile(file_content, name=f'{algorithm_code}.py')

        algorithm = algorithmConfig.objects.get(algorithm_code=algorithm_code)
        # 更新algorithm_file字段
        algorithm.algorithm_file.save(f'{algorithm_code}.py', file_obj, save=True)



        response = {
            'status': 200,
            'message': '新增算法配置成功'
        }

        return JsonResponse(response)

    # 算法配置-删除
    @swagger_auto_schema(
        operation_summary='算法配置-删除',
        request_body=serializer.deleteAlgorithmSerializer,
        responses={200: '删除算法配置成功'},
        tags=["algorithm"],
    )
    @action(detail=False, methods=['post'])
    def algorithmDelete(self, request):
        m = serializer.deleteAlgorithmSerializer(data=request.data)
        m.is_valid()
        algorithm_id = m.validated_data.get('id', None)
        algorithm = models.algorithmConfig.objects.get(id=algorithm_id)
        if algorithm.algorithm_file:
            os.remove(algorithm.algorithm_file.path)
        algorithm.delete()
        response = {
            'status': 200,
            'message': '删除算法配置成功'
        }
        return JsonResponse(response)

    # 算法配置-编辑
    @swagger_auto_schema(
        operation_summary='算法配置-编辑',
        request_body=serializer.editAlgorithmSerializer,
        responses={200: '算法配置修改成功'},
        tags=["algorithm"],
    )
    @action(detail=False, methods=['post'])
    def algorithmUpdate(self, request):
        algorithm_id = self.request.data.get('id')
        algorithm_name = self.request.data.get('algorithm_name')
        algorithm_channel_number = self.request.data.get('algorithm_channel_number')
        remark = self.request.data.get('remark')
        algorithm_file_path = self.request.data.get('algorithm_file')
        algorithm_channel_str = self.request.data.get('algorithm_channel_matrix')
        algorithm_type = self.request.data.get('algorithm_type')
        function_name = self.request.data.get('function_name')

        algorithm = models.algorithmConfig.objects.get(id=algorithm_id)
        algorithm_code = algorithm.algorithm_code
        if algorithm.algorithm_name != algorithm_name:
            if models.algorithmConfig.objects.filter(algorithm_name=algorithm_name).exists():
                response = {
                    'status': 500,
                    'message': f'算法名称<{algorithm_name}>已存在，请重新输入'
                }
                return JsonResponse(response)
            else:
                algorithm_code = algorithm_code_rule(algorithm_name,algorithm_type)

        algorithm.algorithm_name = algorithm_name
        algorithm.algorithm_code = algorithm_code
        algorithm.algorithm_channel_number = algorithm_channel_number
        algorithm.remark = remark
        algorithm.algorithm_type = algorithm_type
        algorithm.function_name = function_name
        algorithm.save()

        algorithm_channels = models.algorithmChannel.objects.filter(algorithm_id=algorithm_id)
        algorithm_channel_matrix_new = ast.literal_eval(algorithm_channel_str)
        algorithm_channel_matrix_old = []
        for algorithm_channel in algorithm_channels:
            algorithm_channel_matrix_old.append(algorithm_channel.channel_id)
        channel_to_add, channel_to_delete = matrix_diff(algorithm_channel_matrix_old, algorithm_channel_matrix_new)

        for channel_id in channel_to_add:
            models.algorithmChannel.objects.create(channel_id=channel_id, algorithm_id=algorithm.id)
        for channel_id in channel_to_delete:
            query = Q(channel_id=channel_id) & Q(algorithm_id=algorithm.id)
            models.algorithmChannel.objects.filter(query).delete()

        file_path = algorithm.algorithm_file.path
        if os.path.exists(file_path):
            os.remove(file_path)

        # 从URL下载文件内容
        response = requests.get(algorithm_file_path)
        file_content = response.content
        # 将内容转换为ContentFile对象
        file_obj = ContentFile(file_content, name=f'{algorithm_code}.py')

        # algorithm = algorithmConfig.objects.get(algorithm_code=algorithm_code)
        # 更新algorithm_file字段
        algorithm.algorithm_file.save(f'{algorithm_code}.py', file_obj, save=True)

        response = {
            'status': 200,
            'message': '编辑算法配置成功'
        }

        return JsonResponse(response)

    # 算法配置-故障算法模板文件下载
    @swagger_auto_schema(
        operation_summary='算法配置-故障算法模板文件下载',
        responses={200: '故障算法模板文件下载成功！'},
        tags=['algorithm']
    )
    @action(detail=False, methods=['get'])
    def downloadTemplateGz(self, request):
        file_path = 'media/AlgorithmTemplateFile/SF-GZ-Template.py'
        file_name = os.path.basename(file_path)

        # 设置响应头
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename={}'.format(urlquote(file_name))

        with open(file_path, 'rb') as file:
            response.write(file.read())

        return response

    # 算法配置-寿命算法模板文件下载
    @swagger_auto_schema(
        operation_summary='算法配置-寿命算法模板文件下载',
        responses={200: '寿命算法模板文件下载成功！'},
        tags=['algorithm']
    )
    @action(detail=False, methods=['get'])
    def downloadTemplateSm(self, request):
        file_path = 'media/AlgorithmTemplateFile/SF-SM-Template.py'
        file_name = os.path.basename(file_path)

        # 设置响应头
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename={}'.format(urlquote(file_name))

        with open(file_path, 'rb') as file:
            response.write(file.read())

        return response

    # 算法配置-算法文件下载
    @swagger_auto_schema(
        operation_summary='算法配置-算法文件下载',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='算法id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: '算法文件下载成功'},
        tags=['algorithm']
    )
    @action(detail=False, methods=['get'])
    def downloadAlgorithmFile(self, request):
        Algorithm_id = self.request.query_params.get("id")
        d = models.algorithmConfig.objects.get(id=Algorithm_id)

        file_path = d.algorithm_file.path
        file_name = os.path.basename(file_path)

        # 设置响应头
        response = HttpResponse(content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename={}'.format(urlquote(file_name))

        with open(file_path, 'rb') as file:
            response.write(file.read())

        return response

    # 部件配置-机床选择下拉框
    @swagger_auto_schema(
        operation_summary='部件配置-机床选择下拉框',
        responses={200: 'Successful'},
        tags=["component"], )
    @action(detail=False, methods=['get'])
    def machineSelect(self, request):
        query = systemConfig.models.systemConfig.objects.all()
        request_list = []
        for i in query:
            request_list.append({
                'id': i.id,
                'machine_name': i.machine_name,
            })
        response_list = {
            'list': request_list,
            'total': query.count()
        }
        response = {
            'data': response_list,
            'message': 'Successful',
            'status': 200,
        }
        return JsonResponse(response)

    # 部件配置-显示
    @swagger_auto_schema(
        operation_summary='部件配置-显示',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='配置id', type=openapi.TYPE_INTEGER,
                              required=False),
            openapi.Parameter('pageSize', openapi.IN_QUERY, description='一页多少条', type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('current', openapi.IN_QUERY, description='当前页面号', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.componentListSerializer)},
        tags=["component"],
    )
    @action(detail=False, methods=['get'])
    def componentDisplay(self, request):
        config_id = self.request.query_params.get('id')
        machine = systemConfig.models.systemConfig.objects.get(id=config_id)
        pageSize = self.request.query_params.get('pageSize')
        current = self.request.query_params.get('current')
        if pageSize is not None and current is not None:
            first = (int(current) - 1) * int(pageSize)
            last = int(current) * int(pageSize)
            if config_id is None:
                components = models.componentConfig.objects.all()[first:last]
                total = models.componentConfig.objects.all().count()
            else:
                components = models.componentConfig.objects.filter(config_id=config_id)[first:last]
                total = models.componentConfig.objects.filter(config_id=config_id).count()
        else:
            components = models.componentConfig.objects.filter(config_id=config_id)
            total = components.count()
        print('total',total)
        result_list = []

        for component in components:
            sensor_id_list = []
            sensor_names_list = []
            sensors = models.componentSensor.objects.filter(component_id=component.id)
            # print("sensor_id", sensors.first().id)
            for sensor in sensors:
                sensor_id = sensor.sensor_id
                sensor_name = systemConfig.models.sensorConfig.objects.get(id=sensor.sensor_id).sensor_name
                sensor_id_list.append(sensor_id)

                sensor_names_list.append(sensor_name)
                # sensor_names = f"{sensor_names} {sensor_name}"
            # sensor_id_list = str(sensor_id_list).replace(" ", "")
            # sensor_names_list = str(sensor_names_list).replace(" ", "")
            sensor_list = {
                            "sensor_id": sensor_id_list,
                            "sensor_names": sensor_names_list,}
            result_list.append(
                {
                    'id': component.id,
                    'config_id': component.config_id,
                    'machine_code': machine.machine_code,
                    'machine_name': machine.machine_name,
                    'component_name': component.component_name,
                    'component_code': component.component_code,
                    'sensor_list': sensor_list,
                    'current_life': component.current_life,
                    'middle_value': component.middle_value,
                    "last_value": component.last_value,
                    'sensor_name': sensor_names,
                    'remark': component.remark,
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

    # 部件配置-新增
    @swagger_auto_schema(
        operation_summary='部件配置-新增',
        request_body=serializer.addComponentSerializer,
        responses={200: '新增部件配置成功'},
        tags=["component"],
    )
    @action(detail=False, methods=['post'])
    def addComponent(self, request):
        config_id = self.request.data.get('config_id')
        component_name = self.request.data.get('component_name')
        remark = self.request.data.get('remark')
        current_life = self.request.data.get('current_life')
        middle_value = self.request.data.get('middle_value')
        last_value = self.request.data.get('last_value')
        sensor_id_str = self.request.data.get('sensor_id')
        sensor_id_matrix = ast.literal_eval(sensor_id_str)

        # 等会儿还原回来
        # 判断传感器是否已经绑定了别的部件；判断传感器状态是否正常
        flag, response = check_sensor(sensor_id_matrix)
        if not flag:
            return JsonResponse(response)

        component_code = component_code_rule(component_name)
        # 创建该部件
        component = models.componentConfig.objects.create(config_id=config_id,
                                                          component_name=component_name,
                                                          component_code=component_code,
                                                          current_life=current_life,
                                                          middle_value=middle_value,
                                                          last_value=last_value,
                                                          remark=remark)
        # 创建该部件对应的传感器id附表
        for sensor_id in sensor_id_matrix:
            models.componentSensor.objects.create(sensor_id=sensor_id, component_id=component.id)

        response = {
            'status': 200,
            'message': f'部件<{component_name}>新增成功'
        }
        return JsonResponse(response)

    # 部件配置-编辑
    @swagger_auto_schema(
        operation_summary='部件配置-编辑',
        request_body=serializer.editComponentSerializer,
        responses={200: '编辑部件配置成功'},
        tags=["component"],
    )
    @action(detail=False, methods=['post'])
    def componentUpdate(self, request):
        component_id = self.request.data.get('id')
        config_id = self.request.data.get('config_id')
        component_name = self.request.data.get('component_name')
        remark = self.request.data.get('remark')
        sensor_id_str = self.request.data.get('sensor_id')
        current_life= self.request.data.get('current_life')
        middle_value= self.request.data.get('middle_value')
        last_value= self.request.data.get('last_value')

        machine = systemConfig.models.systemConfig.objects.get(id=config_id)
        component = models.componentConfig.objects.get(id=component_id)
        # # 等会儿还原回来
        # if component.monitor_status == 1:
        #     response = {
        #         'status': 500,
        #         'message': f'部件<{component.component_name}>正在监控，请关闭监控后重新操作做'
        #     }
        #     return JsonResponse(response)
        component_code = component.component_code
        component_sensors = models.componentSensor.objects.filter(component_id=component_id)

        if component.component_name != component_name:
            if models.componentConfig.objects.filter(component_name=component_name).exists():
                response = {
                    'status': 500,
                    'message': f'部件名称<{component_name}>已存在，请重新输入'
                }
                return JsonResponse(response)
            else:
                component_code = component_code_rule(component_name)

        sensor_id_matrix_new = ast.literal_eval(sensor_id_str)
        sensor_id_matrix_old = []
        for component_sensor in component_sensors:
            sensor_id_matrix_old.append(component_sensor.sensor_id)
        # 等会儿还原回来
        # 判断传感器是否已经绑定了别的部件；判断传感器状态是否正常
        flag, response = check_sensor(sensor_id_matrix_new)
        if not flag:
            return JsonResponse(response)

        sensor_to_add, sensor_to_delete = matrix_diff(sensor_id_matrix_old, sensor_id_matrix_new)

        component.component_code = component_code
        component.component_name = component_name
        component.current_life =current_life
        component.middle_value =middle_value
        component.last_value =last_value
        component.remark = remark
        component.save()

        for sensor_id in sensor_to_add:
            models.componentSensor.objects.create(sensor_id=sensor_id, component_id=component.id)
        for sensor_id in sensor_to_delete:
            query = Q(sensor_id=sensor_id) & Q(component_id=component.id)
            models.componentSensor.objects.filter(query).delete()

        response = {
            'status': 200,
            'message': f'部件<{component_name}>编辑成功'
        }
        return JsonResponse(response)

    # 部件配置-删除
    @swagger_auto_schema(
        operation_summary='部件配置-删除',
        request_body=serializer.componentDeleteSerializer,
        responses={200: '删除部件配置成功'},
        tags=["component"],
    )
    @action(detail=False, methods=['post'])
    def componentDelete(self, request):
        component_id = self.request.data.get('id')
        # component = models.componentConfig.objects.filter(id=component_id)
        # 等会儿还原回来
        # if component.first().monitor_status:
        #     response = {
        #         'status': 500,
        #         'message': '部件正在监控，暂时无法删除！'
        #     }
        # else:
        #     models.componentConfig.objects.filter(id=id).delete()
        models.componentConfig.objects.filter(id=component_id).delete()

        response = {
            'status': 200,
            'message': '部件删除成功！'
        }
        return JsonResponse(response)

    # 部件配置-传感器选择下拉框
    @swagger_auto_schema(
        operation_summary='部件配置-传感器选择下拉框',
        responses={200: 'Successful'},
        tags=["component"], )
    @action(detail=False, methods=['get'])
    def sensorSelect(self, request):
        sensors = systemConfig.models.sensorConfig.objects.all()
        request_list = []
        for sensor in sensors:
            request_list.append({
                'id': sensor.id,
                'sensor_name': sensor.sensor_name,
            })
        response_list = {
            'list': request_list,
            'total': sensors.count(),
        }
        response = {
            'data': response_list,
            'message': 'Successful',
            'status': 200,
        }
        return JsonResponse(response)

    # # 部件配置-通道下拉框
    # @swagger_auto_schema(
    #     operation_summary='部件配置-通道下拉框',
    #     manual_parameters=[
    #         openapi.Parameter('sensor_id', openapi.IN_QUERY, description='传感器id', type=openapi.TYPE_INTEGER,
    #                           required=True), ],
    #     responses={200: 'Successful'},
    #     tags=["component"], )
    # @action(detail=False, methods=['get'])
    # def channelSelect(self, request):
    #     sensor_id = self.request.query_params.get('sensor_id')
    #     channels = systemConfig.models.channelConfig.objects.filter(sensor=sensor_id)
    #     if channels.count() == 0:
    #         response = {
    #             'message': '该传感器下没有通道',
    #             'status': 500
    #         }
    #         return JsonResponse(response)
    #     request_list = []
    #     for i in channels:
    #         request_list.append({
    #             'id': i.id,
    #             'channel_name': i.channel_name,
    #         })
    #
    #     response = {
    #         'list': request_list,
    #         'total': channels.count(),
    #     }
    #     response = {
    #         'data': response,
    #         'message': 'Successful',
    #         'status': 200,
    #     }
    #     return JsonResponse(response)

    # # 部件配置-算法选择下拉框
    # @swagger_auto_schema(
    #     operation_summary='部件配置-算法选择下拉框',
    #     responses={200: 'Successful'},
    #     tags=["component"], )
    # @action(detail=False, methods=['get'])
    # def algorithmSelect(self, request):
    #     query = models.algorithmConfig.objects.all()
    #     request_list = []
    #     for i in query:
    #         request_list.append({
    #             'id': i.id,
    #             'algorithm_name': i.algorithm_name,
    #             'algorithm_channel_number': i.algorithm_channel_number,
    #         })
    #     response_list = {
    #         'list': request_list,
    #         'total': query.count(),
    #     }
    #     response = {
    #         'data': response_list,
    #         'message': 'Successful',
    #         'status': 200,
    #     }
    #     return JsonResponse(response)

    # 信号展示-多重下拉框
    @swagger_auto_schema(
        operation_summary='信号展示-多重下拉框',
        responses={200: 'Successful'},
        tags=["signal"], )
    @action(detail=False, methods=['get'])
    def signalSelect(self, request):
        machines = systemConfig.models.systemConfig.objects.all()
        request = []

        for machine in machines:
            request_list = {
                'value': machine.id,
                'label': machine.machine_name + "_" + machine.manager,
                'children': [],
            }
            components = models.componentConfig.objects.filter(config_id=machine.id)
            # print(components)
            for component in components:
                child_component = {
                    'value': component.id,
                    'label': component.component_name,
                    'children': []
                }
                request_list['children'].append(child_component)
                # sensor_id = j.sensor_id
                component_sensors = models.componentSensor.objects.filter(component_id=component.id)
                for component_sensor in component_sensors:
                    sensors = systemConfig.models.sensorConfig.objects.filter(id=component_sensor.sensor_id)
                    for sensor in sensors:
                        child_sensor = {
                            'value': sensor.id,
                            'label': sensor.sensor_name,
                            'children': []
                        }
                        child_component['children'].append(child_sensor)
                        channels = systemConfig.models.channelConfig.objects.filter(sensor=sensor.id)
                        for h in channels:
                            child_channel = {
                                'value': h.id,
                                'label': h.channel_name,
                            }
                            child_sensor['children'].append(child_channel)
            request.append(request_list)

        response = {
            'list': request,
            'total': machines.count(),
        }
        response = {
            'data': response,
            'message': 'Successful',
            'status': 200,
        }
        return JsonResponse(response)

    # 折线图-信号列表
    @swagger_auto_schema(
        operation_summary='折线图-信号列表',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('component_id', openapi.IN_QUERY, description='部件id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('sensor_id', openapi.IN_QUERY, description='传感器id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('channel_id', openapi.IN_QUERY, description='通道id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: '信号列表获取成功'},
        tags=['signal']
    )
    @action(detail=False, methods=['get'])
    def signalDisplay(self, request):
        config_id = self.request.query_params.get('config_id')
        component_id = self.request.query_params.get('component_id')
        sensor_id = self.request.query_params.get('sensor_id')
        channel_id = self.request.query_params.get('channel_id')

        system = systemConfig.models.systemConfig.objects.get(id=config_id)
        sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
        channel = systemConfig.models.channelConfig.objects.get(id=channel_id)
        component = models.componentConfig.objects.get(id=component_id)

        # if sensor.sensor_status and channel.is_monitor:
        if sensor.sensor_status:
            database_name = system.database_name
            client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin',
                                    database=database_name)
            display_number = 10000
            measurement = sensor.measurement
            unit = channel.unit
            query = f'SELECT * FROM "{measurement}" ORDER BY time DESC LIMIT {display_number}'
            result = client.query(query)
            client.close()
            result_1 = list(result.get_points())
            result_2 = reversed(result_1)

            xData = []
            yData = []
            # 处理查询结果
            for point in result_2:
                field_time = str(
                    (datetime.strptime(point.get('time'), '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(hours=8)).strftime(
                        '%Y-%m-%d %H:%M:%S.%f')[:-5])
                filed = channel.channel_field
                field_value = point.get(filed)
                if (field_time is not None) or (field_value is not None):
                    xData.append(field_time)
                    yData.append(field_value)
            data = {
                'xAxisName': '时间',
                'xData': xData[0: display_number - 1],  # 横坐标
                'yAxisName': unit,
                'yData': yData[0: display_number - 1],  # 纵坐标
            }
            status = 200
            message = '信号列表获取成功'
        else:
            data = {}
            status = 500
            message = '该传感器未开启或该通道未监控，无法获取信号！'
        response = {
            'data': data,
            'status': status,
            'message': message,
        }
        return JsonResponse(response)

    # 折线图-最新信号
    @swagger_auto_schema(
        operation_summary='折线图-最新信号',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('config_id', openapi.IN_QUERY, description='配置id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('component_id', openapi.IN_QUERY, description='部件id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('sensor_id', openapi.IN_QUERY, description='传感器id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('channel_id', openapi.IN_QUERY, description='通道id',
                              type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: '最新信号获取成功'},
        tags=['signal']
    )
    @action(detail=False, methods=['get'])
    def newestSignal(self, request):
        config_id = self.request.query_params.get('config_id')
        component_id = self.request.query_params.get('component_id')
        sensor_id = self.request.query_params.get('sensor_id')
        channel_id = self.request.query_params.get('channel_id')

        system = systemConfig.models.systemConfig.objects.get(id=config_id)
        sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
        channel = systemConfig.models.channelConfig.objects.get(id=channel_id)
        component = models.componentConfig.objects.get(id=component_id)

        database_name = system.database_name
        client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin',
                                database=database_name)
        today = datetime.utcnow().date()
        today_str = today.strftime('%Y-%m-%d')
        if system.influx_clean_date is None:
            influx_clean_flag = 1
        else:
            if system.influx_clean_date < today_str:
                influx_clean_flag = 1
            else:
                influx_clean_flag = 0
        if influx_clean_flag == 1:
            system.influx_clean_date = today_str
            system.save()
            threading.Thread(target=influxDataToCsv, args=(client, today_str)).start()
            # influxDataToCsv(client)
        measurement = sensor.measurement
        unit = channel.unit

        # if sensor.sensor_status and channel.is_monitor:
        if sensor.sensor_status:
            query = f'SELECT * FROM "{measurement}" ORDER BY time DESC LIMIT 1'
            result = client.query(query)
            client.close()
            points = list(result.get_points())
            # 检查points是否为空
            if not points:
                data = {
                    'xAxisName': '时间',
                    'xData': "",  # 横坐标
                    'yAxisName': unit,
                    'yData': "",  # 纵坐标
                }
                response = {
                    'data': data,
                    'status': 200,
                    'message': '最新信号获取成功！',
                }
                return JsonResponse(response)
            point = points[0]
            # 解析时间字符串
            field_time = str(
                (datetime.strptime(point.get('time'), '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(hours=8)).strftime(
                    '%Y-%m-%d %H:%M:%S.%f')[:-5])
            filed = channel.channel_field
            field_value = point.get(filed)
            print('field_value', field_value)

            data = {
                'xAxisName': '时间',
                'xData': field_time,  # 横坐标
                'yAxisName': unit,
                'yData': field_value,  # 纵坐标
            }
        else:
            data = {
                'xAxisName': '时间',
                'xData': "",  # 横坐标
                'yAxisName': unit,
                'yData': "",  # 纵坐标
            }
        response = {
            'data': data,
            'status': 200,
            'message': '最新信号获取成功！',
        }
        return JsonResponse(response)


def influxDataToCsv(client, today_str):
    sensors = systemConfig.models.sensorConfig.objects.filter(sensor_status=True)
    # 当前日期
    today = datetime.utcnow().date()
    today_str = today.strftime('%Y-%m-%d')
    for sensor in sensors:
        measurement = sensor.measurement
        print('measurement', measurement)
        query = f'SELECT * FROM "{measurement}"'
        result = client.query(query)
        points = list(result.get_points())

        # max_date_str_result = systemConfig.models.influxDataConfig.objects.filter(sensor_id=sensor.id).aggregate(Max('date'))
        # max_date_str = max_date_str_result['date__max']
        #
        # # 判断是否已经删除过前日的数据
        # if max_date_str is not None and max_date_str == today_str:
        #     continue

        # 存储要删除的数据
        data_to_delete = {}

        # 创建CSV数据
        for point in points:
            timestamp = parser.parse(point.get('time'))
            # timestamp = datetime.strptime(point.get('time'), '%Y-%m-%dT%H:%M:%S.%fZ')
            if timestamp.date() < today:  # 今日之前的数据
                date_str = timestamp.date().strftime('%Y-%m-%d')
                if date_str not in data_to_delete:
                    data_to_delete[date_str] = []
                data_to_delete[date_str].append(point)

        # 将数据写入CSV文件
        for date_str, data in data_to_delete.items():
            if data:
                df = pd.DataFrame(data)
                csv_filename = f'{measurement}_{date_str}.csv'
                csv_bytes_io = BytesIO()
                df.to_csv(csv_bytes_io, index=False)
                csv_bytes_io.seek(0)  # 重置指针到文件开头

                influx_data = systemConfig.models.influxDataConfig.objects.create(date=today_str, sensor_id=sensor.id)
                influx_data.influx_file.save(csv_filename, csv_bytes_io)

                # 删除今日之前的数据
                delete_query = f'DELETE FROM "{measurement}" WHERE time < \'{today_str}T00:00:00Z\''
                print(f'Delete query: {delete_query}')

                try:
                    client.query(delete_query)
                    print(f'{measurement}Successfully deleted data before {today_str}')
                except Exception as e:
                    print(f'Error deleting data: {e}')
                # # 删除今日之前的数据
                # for point in data:
                #     delete_query = f'DELETE FROM "{measurement}" WHERE time = \'{point.get("time")}\''
                #     client.query(delete_query)

                csv_bytes_io.close()  # 关闭 BytesIO


# 判断传感器是否已经绑定了别的部件；判断传感器状态是否正常
def check_sensor(matrix):
    flag = True
    response = {}
    for sensor_id in matrix:
        component_senors = models.componentSensor.objects.filter(sensor_id=sensor_id)
        sensor = systemConfig.models.sensorConfig.objects.get(id=sensor_id)
        sensor_name = sensor.sensor_name
        if component_senors.exists():
            flag = False
            component_id = component_senors.first().component_id
            component_name = models.componentConfig.objects.get(id=component_id).component_name
            response = {
                'status': 500,
                'message': f'传感器<{sensor_name}>已被部件<{component_name}>”使用',
            }
            return flag, response
        if sensor.sensor_status is False:
            flag = False
            response = {
                'status': 500,
                'message': f'传感器<{sensor_name}>状态异常，请重启检查传感器状态',
            }
        return flag, response


# 多个下拉编辑时重新选择时的判定
def matrix_diff(matrix_old, matrix_new):
    set_A = set(matrix_old)
    set_B = set(matrix_new)

    # 找到两个集合的交集
    common_elements = set_A.intersection(set_B)
    # 将结果转换回列表
    common_elements_list = list(common_elements)

    # 找到第一个集合中存在，但第二个集合中不存在的元素
    elements_in_A_not_in_B = set_A.difference(set_B)
    # 将结果转换回列表
    matrix_to_delete = list(elements_in_A_not_in_B)

    # 找到第二个集合中存在，但第一个集合中不存在的元素
    elements_in_B_not_in_A = set_B.difference(set_A)
    # 将结果转换回列表
    matrix_to_add = list(elements_in_B_not_in_A)
    return matrix_to_add, matrix_to_delete
