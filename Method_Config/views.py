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
import System_Config


class MethodConfigViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)
    parser_classes = (MultiPartParser, FormParser)

    # 返回数据库所有对象.
    def get_queryset(self):
        return models.methodConfig.objects.all()

    # 算法配置 > 查询
    @swagger_auto_schema(
        operation_summary='算法配置 > 查询',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('pageSize', openapi.IN_QUERY, description='一页多少条', type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('current', openapi.IN_QUERY, description='当前页面号', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.AlgorithmSerializer)},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['get'])
    def methodConfigList(self, request):
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        first = (current - 1) * pageSize
        last = current * pageSize
        method = self.get_queryset()
        method_config_all = method[first:last]
        total = method.count()
        result_list = []
        for x in method_config_all:
            result_list.append(
                {
                    'algorithm_code': x.algorithm_code,
                    'algorithm_name': x.algorithm_name,
                    'algorithm_channel_number': x.algorithm_channel_number,
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

    # 算法配置 > 新增算法
    @swagger_auto_schema(
        operation_summary='算法配置 > 新增算法',
        request_body=serializer.AlgorithmSerializer,
        responses={200: openapi.Response('successful', serializer.AlgorithmSerializer), 500: '该id已存在'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def addMethodConfig(self, request):
        algorithm_code = self.request.data.get('algorithm_code')
        algorithm_name = self.request.data.get('algorithm_name')
        algorithm_channel_number = self.request.data.get('algorithm_channel_number')
        algorithm_file = self.request.data.get('algorithm_file')
        remark = self.request.data.get('remark')
        new_method_configuration = models.methodConfig.objects.create(algorithm_code=algorithm_code,
                                                                      algorithm_name=algorithm_name,
                                                                      algorithm_channel_number=algorithm_channel_number,
                                                                      algorithm_file=algorithm_file,
                                                                      remark=remark)
        response = {
            'status': 200,
            'message': '新增算法配置成功'
        }
        return JsonResponse(response)

    # 算法配置 > 删除
    @swagger_auto_schema(
        operation_summary='算法配置 > 删除',
        request_body=serializer.deleteAlgorithmSerializer,
        responses={200: '删除算法配置成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def deleteMethodConfig(self, request):
        g = serializer.deleteAlgorithmSerializer(data=request.data)
        g.is_valid()
        algorithm_code = g.validated_data.get('algorithm_code')
        print(algorithm_code)
        models.methodConfig.objects.filter(algorithm_code=algorithm_code).delete()
        response = {
            'status': 200,
            'message': '删除算法配置成功'
        }
        return JsonResponse(response)

    # 算法配置 > 编辑
    @swagger_auto_schema(
        operation_summary='算法配置 > 编辑',
        request_body=serializer.AlgorithmSerializer,
        responses={200: '算法配置修改成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def methodConfigUpdate(self, request):
        algorithm_id = request.data.get('algorithm_id')
        algorithm_code = self.request.data.get('algorithm_code')
        algorithm_name = self.request.data.get('algorithm_name')
        algorithm_channel_number = self.request.data.get('algorithm_channel_number')
        remark = self.request.data.get('remark')
        algorithm_file = self.request.data.get('algorithm_file')
        models.methodConfig.objects.filter(id=algorithm_id).update(algorithm_code=algorithm_code,
                                                                   algorithm_name=algorithm_name,
                                                                   algorithm_channel_number=algorithm_channel_number,
                                                                   remark=remark,
                                                                   algorithm_file=algorithm_file,
                                                                   )
        response = {
            'status': 200,
            'message': '编辑算法配置成功'
        }
        return JsonResponse(response)

    # 部件配置 > 机床选择下拉框
    @swagger_auto_schema(operation_summary='部件配置 > 机床选择下拉框',
                         responses={200: 'Successful'},
                         tags=["MethodConfig"], )
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

    # 部件配置 > 部件选择下拉框
    @swagger_auto_schema(operation_summary='部件配置 > 部件选择下拉框',
                         # 获取参数
                         manual_parameters=[
                             openapi.Parameter('id', openapi.IN_QUERY, description='部件配置表id',
                                               type=openapi.TYPE_INTEGER, required=True),
                         ],
                         responses={200: openapi.Response('successful', serializer.componentConfigSerializer)},
                         tags=["MethodConfig"], )
    @action(detail=False, methods=['get'])
    def componentSelect(self, request):
        systemConfig_id = self.request.query_params.get('id')
        component_Config = models.componentConfig.objects.filter(config_id=systemConfig_id)
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

    # 部件配置 > 算法选择下拉框
    @swagger_auto_schema(operation_summary='部件配置 > 算法选择下拉框',
                         responses={200: 'Successful'},
                         tags=["MethodConfig"], )
    @action(detail=False, methods=['get'])
    def methodSelect(self, request):
        query = models.methodConfig.objects.all()
        request_list = []
        for i in query:
            request_list.append({
                'id': i.id,
                'algorithm_name': i.algorithm_name,
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

    # 部件配置 > 算法输入通道1、2、3 > 传感器选择下拉框
    @swagger_auto_schema(operation_summary='部件配置 > 算法输入通道1、2、3 > 传感器选择下拉框',
                         responses={200: 'Successful'},
                         tags=["MethodConfig"], )
    @action(detail=False, methods=['get'])
    def sensorSelect(self, request):
        sensor = System_Config.models.sensorConfig.objects.all()
        request_list = []
        for i in sensor:
            request_list.append({
                'id': i.id,
                'sensor_code': i.sensor_code,
                'sensor_name': i.sensor_name,
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

    # 部件配置 > 算法输入通道1、2、3 > 通道选择下拉框
    @swagger_auto_schema(operation_summary='部件配置 > 算法输入通道1、2、3 > 通道选择下拉框',
                         # 获取参数
                         manual_parameters=[
                             openapi.Parameter('id', openapi.IN_QUERY, description='传感器id',
                                               type=openapi.TYPE_INTEGER, required=True),
                         ],
                         responses={200: openapi.Response('successful', serializer.sensorChannelSerializer)},
                         tags=["MethodConfig"], )
    @action(detail=False, methods=['get'])
    def channelSelect(self, request):
        sensor_id = self.request.query_params.get('id')
        channel = System_Config.models.channelConfig.objects.filter(channel_id=sensor_id)
        request_list = []
        for i in channel:
            request_list.append({
                'id': i.id,
                'sensor_name': i.sensor_name,
                'channel_name': i.channel_name,
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

    # 部件配置 > 查询
    @swagger_auto_schema(
        operation_summary='部件配置 > 查询',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description='id', type=openapi.TYPE_INTEGER,
                              required=False),
            openapi.Parameter('pageSize', openapi.IN_QUERY, description='一页多少条', type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('current', openapi.IN_QUERY, description='当前页面号', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.componentConfigSerializer)},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['get'])
    def componentConfigList(self, request):
        config_id = self.request.query_params.get('id')
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        first = (current - 1) * pageSize
        last = current * pageSize
        if config_id is None:
            component = models.componentConfig.objects.all()[first:last]
        else:
            component = models.componentConfig.objects.filter(machine_code=config_id)[first:last]
        total = component.count()
        result_list = []
        for x in component:
            result_list.append(
                {
                    'machine_code': x.machine_code,
                    'machine_name': x.machine_name,
                    'component_name': x.component_name,
                    'algorithm_name': x.algorithm_name,
                    'algorithm_channel': x.algorithm_channel,
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

    # 部件配置 > 新增部件
    @swagger_auto_schema(
        operation_summary='部件配置 > 新增部件',
        request_body=serializer.componentConfigSerializer,
        responses={200: '新增部件配置成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def addComponentConfig(self, request):
        config_id = self.request.data.get('config_id')  # 重新选择“机床下拉框”返回的“表：系统配置”的id
        config_X = System_Config.models.systemConfig.objects.get(id=config_id)  # 根据config_id找的"系统配置_X"的一行数据
        machine_code = config_X.machine_code  # 根据"系统配置_X"查的机床编号
        machine_name = config_X.machine_name  # 根据"系统配置X"查的机床名称

        component_name = self.request.data.get('component_name')  # 修改的部件名称
        algorithm_id = self.request.data.get('algorithm_id')  # 重新选择“算法下拉框”返回的“表：算法配置”的id
        algorithm_X = models.methodConfig.objects.get(id=algorithm_id)  # 根据algorithm_id查的"算法_X"
        algorithm_name = algorithm_X.algorithm_name  # 根据"算法_X"查的算法名称
        algorithm_channel_number = algorithm_X.algorithm_channel_number  # 根据"算法_X"查的算法通道数量
        remark = self.request.data.get('remark')  # 修改的备注

        channel_id_dictionary = {1: 'input_channel1',
                                 2: 'input_channel2',
                                 3: 'input_channel3',
                                 4: 'input_channel4',
                                 5: 'input_channel5'}
        channel_name_dictionary = {1: 'input_channel1',
                                   2: 'input_channel2',
                                   3: 'input_channel3',
                                   4: 'input_channel4',
                                   5: 'input_channel5'}
        for t in range(1, algorithm_channel_number + 1):
            channel_id_dictionary[t] = self.request.data.get(channel_id_dictionary[t])
            channel_name_dictionary[t] = System_Config.models.channelConfig.objects.get(
                id=channel_id_dictionary[t]).channel_name
        # 获取字典的前algorithm_channel_number个值并拼接成字符串
        # algorithm_channel = ','.join([channel_name_dictionary[key] for key in
        #                               sorted(channel_name_dictionary.keys())[:algorithm_channel_number]])
        algorithm_channel = ','.join(channel_name_dictionary[t] for t in range(1, algorithm_channel_number + 1))
        print('运行成功', algorithm_channel)
        new_component = models.componentConfig.objects.create(config_id=config_id,
                                                              machine_code=machine_code,
                                                              machine_name=machine_name,
                                                              component_name=component_name,
                                                              algorithm_id=algorithm_id,
                                                              algorithm_name=algorithm_name,
                                                              algorithm_channel=algorithm_channel,
                                                              remark=remark)
        # 生成对应通道数量的实例
        for m in range(1, algorithm_channel_number + 1):
            channel_id = channel_id_dictionary[m]
            channel = System_Config.models.channelConfig.objects.get(id=channel_id)
            models.algorithmChannel.objects.create(sensor_id=channel.channel_id,
                                                   sensor_name=channel.sensor_name,
                                                   channel_id=channel_id,
                                                   channel_name=channel.channel_name,
                                                   algorithm_channel_id=new_component.id, )
        response = {
            'status': 200,
            'message': '新增部件配置成功'
        }
        return JsonResponse(response)

    # 部件配置 > 编辑部件
    @swagger_auto_schema(
        operation_summary='部件配置 > 编辑部件',
        request_body=serializer.changeComponentConfigSerializer,
        responses={200: '编辑部件配置成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def ComponentConfigUpdate(self, request):
        id = self.request.data.get('id')  # 要修改的那条数据的id
        config_id = self.request.data.get('config_id')  # 重新选择“机床下拉框”返回的“表：系统配置”的id
        config_X = System_Config.models.systemConfig.objects.get(id=config_id)  # 根据config_id找的"系统配置_X"
        machine_code = config_X.machine_code  # 根据"系统配置_X"查的机床编号
        machine_name = config_X.machine_name  # 根据"系统配置X"查的机床名称

        component_name = self.request.data.get('component_name')  # 修改的部件名称
        algorithm_id = self.request.data.get('algorithm_id')  # 重新选择“算法下拉框”返回的“表：算法配置”的id
        algorithm_X = models.methodConfig.objects.get(id=algorithm_id)  # 根据algorithm_id查的"算法_X"
        algorithm_name = algorithm_X.algorithm_name  # 根据"算法_X"查的算法名称
        algorithm_channel_number = algorithm_X.algorithm_channel_number  # 根据"算法_X"查的算法通道数量
        remark = self.request.data.get('remark')  # 修改的备注

        channel_id_dictionary = {1: 'input_channel1',
                                 2: 'input_channel2',
                                 3: 'input_channel3',
                                 4: 'input_channel4',
                                 5: 'input_channel5'}
        channel_name_dictionary = {1: 'input_channel1',
                                   2: 'input_channel2',
                                   3: 'input_channel3',
                                   4: 'input_channel4',
                                   5: 'input_channel5'}
        for t in range(1, algorithm_channel_number + 1):
            channel_id_dictionary[t] = self.request.data.get(channel_id_dictionary[t])
            channel_name_dictionary[t] = System_Config.models.channelConfig.objects.get(
                id=channel_id_dictionary[t]).channel_name
        # 获取字典的前三个值并拼接成字符串
        # algorithm_channel = ','.join(
        #      [channel_name_dictionary[key] for key in sorted(channel_name_dictionary.keys())[:algorithm_channel_number]])
        algorithm_channel = ','.join(channel_name_dictionary[t] for t in range(1, algorithm_channel_number + 1))
        change_Component_config = models.componentConfig.objects.filter(id=id)
        print(change_Component_config.count())
        change_Component_config.update(config_id=config_id,
                                       machine_code=machine_code,
                                       machine_name=machine_name,
                                       component_name=component_name,
                                       algorithm_id=algorithm_id,
                                       algorithm_name=algorithm_name,
                                       algorithm_channel=algorithm_channel,
                                       remark=remark)
        # 删除附表中外键为该id的实例
        # models.algorithmChannel.objects.filter(algorithm_channel_id=id).delete()
        # 重新生成对应通道数量的实例
        for m in range(1, algorithm_channel_number + 1):
            channel_id = channel_id_dictionary[m]
            channel = System_Config.models.channelConfig.objects.get(id=channel_id)
            models.algorithmChannel.objects.create(sensor_id=channel.channel_id,
                                                   sensor_name=channel.sensor_name,
                                                   channel_id=channel_id,
                                                   channel_name=channel.channel_name,
                                                   algorithm_channel_id=id, )
        response = {
            'status': 200,
            'message': '编辑部件配置成功'
        }
        return JsonResponse(response)

    # 部件配置 > 删除部件
    @swagger_auto_schema(
        operation_summary='部件配置 > 删除部件',
        request_body=serializer.deleteComponentConfigSerializer,
        responses={200: '删除部件配置成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def ComponentConfigDelete(self, request):
        id = self.request.data.get('id')  # 要删除的那条数据的id
        # 删除部件配置表对应id的实例
        models.componentConfig.objects.filter(id=id).delete()
        # 删除附表中外键为该id的实例
        models.algorithmChannel.objects.filter(algorithm_channel_id=id).delete()

        response = {
            'status': 200,
            'message': '编辑部件配置成功'
        }
        return JsonResponse(response)
