import json
import os
import socket
from datetime import datetime, timedelta

from django.db.models import Max
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
import System_Config


def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip


def get_initials(chinese_str):
    # 将中文转换为拼音列表
    pinyin_list = lazy_pinyin(chinese_str, style=Style.INITIALS)
    # 提取每个拼音的首字母并转换为大写
    initials = ''.join([item[0].upper() for item in pinyin_list])
    return initials


def algorithm_code_rule(algorithm_name):
    prefix = f'SF-{algorithm_name}-'
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
        method = self.get_queryset()
        method_config_all = method[first:last]
        total = method.count()
        result_list = []
        ip_address = f"http://{get_local_ip()}:8000"
        for x in method_config_all:
            result_list.append(
                {
                    'id': x.id,
                    'algorithm_code': x.algorithm_code,
                    'algorithm_name': x.algorithm_name,
                    'algorithm_channel_number': x.algorithm_channel_number,
                    'remark': x.remark,
                    'algorithm_file': ip_address + x.algorithm_file.url,
                    # 'algorithm_file': os.path.basename(x.algorithm_file.name),
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
        algorithm_file = self.request.data.get('algorithm_file')
        remark = self.request.data.get('remark')
        if algorithm_file.name.endswith('.py'):
            algorithm_code = algorithm_code_rule(algorithm_name)
            m = models.algorithmConfig.objects.create(algorithm_code=algorithm_code,
                                                      algorithm_name=algorithm_name,
                                                      algorithm_channel_number=algorithm_channel_number,
                                                      remark=remark)
            # 生成新的文件名
            new_filename = f"{algorithm_code}.py"

            # 将新文件保存到本地文件系统和数据库中
            m.algorithm_file.save(new_filename, algorithm_file, save=True)
            m.save()

            response = {
                'status': 200,
                'message': '新增算法配置成功'
            }
        else:
            response = {
                'status': 500,
                'message': '请选择.py文件！'
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
        algorithmId = m.validated_data.get('id', None)
        n = models.algorithmConfig.objects.get(id=algorithmId)
        if n.algorithm_file:
            os.remove(n.algorithm_file.path)
        n.delete()
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
        algorithm_file = self.request.data.get('algorithm_file')
        if algorithm_file.name.endswith('.py'):
            algorithm_code = algorithm_code_rule(algorithm_name)
            models.algorithmConfig.objects.filter(id=algorithm_id).update(algorithm_code=algorithm_code,
                                                                          algorithm_name=algorithm_name,
                                                                          algorithm_channel_number=algorithm_channel_number,
                                                                          remark=remark)
            n = models.algorithmConfig.objects.get(id=algorithm_id)
            if n.algorithm_file:
                os.remove(n.algorithm_file.path)
            # 生成新的文件名
            new_filename = f"{algorithm_code}.py"
            # 将新文件保存到本地文件系统和数据库中
            n.algorithm_file.save(new_filename, algorithm_file, save=True)
            n.save()
            response = {
                'status': 200,
                'message': '编辑算法配置成功'
            }
        else:
            response = {
                'status': 500,
                'message': '请选择.py文件！'
            }
        return JsonResponse(response)

    # 算法配置-算法模板文件下载
    @swagger_auto_schema(
        operation_summary='算法配置-算法模板文件下载',
        responses={200: '算法模板文件下载成功！'},
        tags=['algorithm']
    )
    @action(detail=False, methods=['get'])
    def downloadTemplate(self, request):
        file_path = 'media/AlgorithmTemplateFile/SF-Template.py'
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
        query = System_Config.models.systemConfig.objects.all()
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

    # 部件配置-算法输入通道
    @swagger_auto_schema(
        operation_summary='部件配置-算法输入通道',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='系统配置id', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful')},
        tags=["component"]
    )
    @action(detail=False, methods=['get'])
    def channelSelect(self, request):
        config_id = self.request.query_params.get("id")
        sensors = System_Config.models.sensorConfig.objects.filter(config_id=config_id, sensor_status=True)
        request_list = []
        for i in sensors:
            sensor_data = {
                'sensor_id': i.id,
                'sensor_name': i.sensor_name,
                'channels': []
            }
            channels = System_Config.models.channelConfig.objects.filter(channel_id=i.id)
            for j in channels:
                sensor_data['channels'].append(
                    {
                        'channel_id': j.channel_id,
                        'channel_name': j.channel_name,
                    }
                )
            request_list.append(sensor_data)
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
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        first = (current - 1) * pageSize
        last = current * pageSize
        if config_id is None:
            component = models.componentConfig.objects.all()[first:last]
        else:
            component = models.componentConfig.objects.filter(config_id=config_id)[first:last]
        total = component.count()
        result_list = []
        for x in component:
            algorithm_channel = []
            c = models.algorithmChannel.objects.filter(algorithm_channel_id=x.id)
            for i in c:
                algorithm_channel.append({
                    'id': i.id,
                    'channel_name': i.channel_name,
                })
            result_list.append(
                {
                    'id': x.id,
                    'machine_code': x.machine_code,
                    'machine_name': x.machine_name,
                    'component_name': x.component_name,
                    'component_code': x.component_code,
                    'algorithm_name': x.algorithm_name,
                    'algorithm_channel': algorithm_channel,
                    'remark': x.remark,
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
        algorithm_id = self.request.data.get('algorithm_id')
        remark = self.request.data.get('remark')
        algorithm_channel_data = self.request.data.get('algorithm_channel_data')

        system = System_Config.models.systemConfig.objects.get(id=config_id)
        algorithm = models.algorithmConfig.objects.get(id=algorithm_id)

        component_code = component_code_rule(component_name)
        new_component = models.componentConfig.objects.create(config_id=config_id,
                                                              machine_code=system.machine_code,
                                                              machine_name=system.machine_name,
                                                              component_name=component_name,
                                                              component_code=component_code,
                                                              algorithm_id=algorithm_id,
                                                              algorithm_name=algorithm.algorithm_name,
                                                              remark=remark)
        algorithm_channel_data = json.loads(algorithm_channel_data)
        for i in range(len(algorithm_channel_data)):
            sensor_id = algorithm_channel_data[i]["sensor_id"]
            channel_id = algorithm_channel_data[i]["channel_id"]
            sensor = System_Config.models.sensorConfig.objects.get(id=sensor_id)
            channel = System_Config.models.channelConfig.objects.get(id=channel_id)
            models.algorithmChannel.objects.create(sensor_id=sensor.id,
                                                   sensor_name=sensor.sensor_name,
                                                   channel_id=channel.id,
                                                   channel_name=channel.channel_name,
                                                   algorithm_channel_id=new_component.id, )
        response = {
            'status': 200,
            'message': '新增部件配置成功'
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
    def ComponentUpdate(self, request):
        id = self.request.data.get('id')
        config_id = self.request.data.get('config_id')
        component_name = self.request.data.get('component_name')
        algorithm_id = self.request.data.get('algorithm_id')
        remark = self.request.data.get('remark')
        algorithm_channel_data = self.request.data.get('algorithm_channel_data')

        system = System_Config.models.systemConfig.objects.get(id=config_id)
        algorithm = models.algorithmConfig.objects.get(id=algorithm_id)

        models.algorithmChannel.objects.filter(algorithm_channel_id=id).delete()

        component = models.componentConfig.objects.filter(id=id)

        if component_name == component.first().component_name:
            component_code = component.first().component_code
        else:
            component_code = component_code_rule(component_name)

        component.update(config_id=config_id,
                         machine_code=system.machine_code,
                         machine_name=system.machine_name,
                         component_name=component_name,
                         component_code=component_code,
                         algorithm_id=algorithm_id,
                         algorithm_name=algorithm.algorithm_name,
                         remark=remark)
        algorithm_channel_data = json.loads(algorithm_channel_data)
        for i in range(len(algorithm_channel_data)):
            sensor_id = algorithm_channel_data[i]["sensor_id"]
            channel_id = algorithm_channel_data[i]["channel_id"]
            sensor = System_Config.models.sensorConfig.objects.get(id=sensor_id)
            channel = System_Config.models.channelConfig.objects.get(id=channel_id)
            models.algorithmChannel.objects.create(sensor_id=sensor.id,
                                                   sensor_name=sensor.sensor_name,
                                                   channel_id=channel.id,
                                                   channel_name=channel.channel_name,
                                                   algorithm_channel_id=id, )
        response = {
            'status': 200,
            'message': '编辑部件配置成功'
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
        id = self.request.data.get('id')
        component = models.componentConfig.objects.filter(id=id)
        if component.first().monitor_status:
            response = {
                'status': 500,
                'message': '部件正在监控，暂时无法删除！'
            }
        else:
            models.algorithmChannel.objects.filter(algorithm_channel_id=id).delete()
            models.componentConfig.objects.filter(id=id).delete()
            response = {
                'status': 200,
                'message': '删除部件配置成功！'
            }
        return JsonResponse(response)

    # 部件配置-算法选择下拉框
    @swagger_auto_schema(
        operation_summary='部件配置-算法选择下拉框',
        responses={200: 'Successful'},
        tags=["component"], )
    @action(detail=False, methods=['get'])
    def algorithmSelect(self, request):
        query = models.algorithmConfig.objects.all()
        request_list = []
        for i in query:
            request_list.append({
                'id': i.id,
                'algorithm_name': i.algorithm_name,
                'algorithm_channel_number': i.algorithm_channel_number,
            })
        response_list = {
            'list': request_list,
            'total': query.count(),
        }
        response = {
            'data': response_list,
            'message': 'Successful',
            'status': 200,
        }
        return JsonResponse(response)

    # 信号展示-多重下拉框
    @swagger_auto_schema(
        operation_summary='信号展示-多重下拉框',
        responses={200: 'Successful'},
        tags=["signal"], )
    @action(detail=False, methods=['get'])
    def signalSelect(self, request):
        system = System_Config.models.systemConfig.objects.all()
        request_list = []
        for i in system:
            machine_data = {
                'machine_name': i.machine_name,
                'components': []
            }
            components = models.componentConfig.objects.filter(config_id=i.id)
            for j in components:
                component_data = {
                    'component_name': j.component_name,
                    'sensors': []
                }
                sensors = models.algorithmChannel.objects.filter(algorithm_channel_id=j.id)
                for k in sensors:
                    sensor_data = {
                        'sensor_name': k.sensor_name,
                        'sensor_id': k.sensor_id,
                        'channels': []
                    }
                    channels = models.algorithmChannel.objects.filter(sensor_id=k.sensor_id)
                    for l in channels:
                        sensor_data['channels'].append(
                            {
                                'channel_name': l.channel_name,
                                'channel_id': l.channel_id,
                            }
                        )
                    component_data['sensors'].append(sensor_data)
                machine_data['components'].append(component_data)
            request_list.append(machine_data)

        response_list = {
            'list': request_list,
            'total': system.count(),
        }
        response = {
            'data': response_list,
            'message': 'Successful',
            'status': 200,
        }
        return JsonResponse(response)

    # 信号展示-信号列表
    @swagger_auto_schema(
        operation_summary='信号展示-信号列表',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('sensor_id', openapi.IN_QUERY, description='传感器id',
                              type=openapi.TYPE_STRING,
                              required=True),
            openapi.Parameter('channel_id', openapi.IN_QUERY, description='通道id',
                              type=openapi.TYPE_STRING,
                              required=True),
        ],
        responses={200: '功率信号列表获取成功'},
        tags=['signal']
    )
    @action(detail=False, methods=['get'])
    def signalDisplay(self, request):
        sensor_id = self.request.data.get('sensor_id')
        channel_id = self.request.data.get('channel_id')

        sensor = System_Config.models.sensorConfig.objects.get(id=sensor_id)
        channel = System_Config.models.channelConfig.objects.get(id=channel_id)
        if sensor.sensor_status and channel.is_monitor:
            database_name = System_Config.models.sensorConfig.objects.get(is_apply=True).database_name
            client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin',
                                    database=database_name)
            display_number = 2000
            table = sensor.table_name
            unit = sensor.unit
            query = f'SELECT * FROM "{table}" ORDER BY time DESC LIMIT {display_number}'
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
                field_value = point.get('fields1_power')
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

    # 信号展示-最新信号
    @swagger_auto_schema(
        operation_summary='信号展示-最新信号',
        responses={200: '最新信号获取成功'},
        tags=['signal']
    )
    @action(detail=False, methods=['get'])
    def newestSignal(self, request):
        sensor_id = self.request.data.get('sensor_id')
        channel_id = self.request.data.get('channel_id')

        sensor = System_Config.models.sensorConfig.objects.get(id=sensor_id)
        channel = System_Config.models.channelConfig.objects.get(id=channel_id)
        database_name = System_Config.models.sensorConfig.objects.get(is_apply=True).database_name
        table = sensor.table_name
        unit = sensor.unit
        if sensor.sensor_status and channel.is_monitor:
            client = InfluxDBClient(host='localhost', port=8086, username='admin', password='admin',
                                    database=database_name)
            query = f'SELECT * FROM "{table}" ORDER BY time DESC LIMIT 1'
            result = client.query(query)
            client.close()
            points = list(result.get_points())
            point = points[0]
            # 解析时间字符串
            field_time = str(
                (datetime.strptime(point.get('time'), '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(hours=8)).strftime(
                    '%Y-%m-%d %H:%M:%S.%f')[:-5])
            field_value = point.get('fields1_power')

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
