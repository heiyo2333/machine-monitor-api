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
        config_id = self.request.data.get('config_id')
        machine = System_Config.models.systemConfig.objects.get(id=config_id)
        machine_code = machine.machine_code
        machine_name = machine.machine_name

        component_name = self.request.data.get('component_name')
        algorithm_id = self.request.data.get('algorithm_id')
        algorithm_name = models.methodConfig.objects.get(id=algorithm_id).algorithm_name
        remark = self.request.data.get('remark')
        channel_count = 5
        channel_name_dictionary = {1: 'null',
                                   2: 'null',
                                   3: 'null',
                                   4: 'null',
                                   5: 'null'}
        channel_id_dictionary = {1: 'null',
                                 2: 'null',
                                 3: 'null',
                                 4: 'null',
                                 5: 'null'}
        input_channel1_id = self.request.data.get('input_channel1')
        if input_channel1_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[1] = System_Config.models.channelConfig.objects.get(
                id=input_channel1_id).channel_id
            channel_name_dictionary[1] = System_Config.models.channelConfig.objects.get(
                id=input_channel1_id).channel_name
        input_channel2_id = self.request.data.get('input_channel2')
        if input_channel2_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[2] = System_Config.models.channelConfig.objects.get(
                id=input_channel2_id).channel_id
            channel_name_dictionary[2] = System_Config.models.channelConfig.objects.get(
                id=input_channel2_id).channel_name
        input_channel3_id = self.request.data.get('input_channel3')
        if input_channel3_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[3] = System_Config.models.channelConfig.objects.get(
                id=input_channel3_id).channel_id
            channel_name_dictionary[3] = System_Config.models.channelConfig.objects.get(
                id=input_channel3_id).channel_name
        input_channel4_id = self.request.data.get('input_channel4')
        if input_channel4_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[4] = System_Config.models.channelConfig.objects.get(
                id=input_channel4_id).channel_id
            channel_name_dictionary[4] = System_Config.models.channelConfig.objects.get(
                id=input_channel4_id).channel_name
        input_channel5_id = self.request.data.get('input_channel5')
        if input_channel5_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[5] = System_Config.models.channelConfig.objects.get(
                id=input_channel5_id).channel_id
            channel_name_dictionary[5] = System_Config.models.channelConfig.objects.get(
                id=input_channel5_id).channel_name
        algorithm_channel = channel_name_dictionary[1]
        for j in range(2, channel_count + 1):
            if channel_name_dictionary[j] is not 'null':
                algorithm_channel = f'{algorithm_channel}, {channel_name_dictionary[j]}'
        new_Component_config = models.componentConfig.objects.create(config_id=config_id,
                                                                     machine_code=machine_code,
                                                                     machine_name=machine_name,
                                                                     component_name=component_name,
                                                                     algorithm_id=algorithm_id,
                                                                     algorithm_name=algorithm_name,
                                                                     algorithm_channel=algorithm_channel,
                                                                     remark=remark, )

        for m in range(1, channel_count + 1):
            channel_id = channel_id_dictionary[m]
            channel = System_Config.models.channelConfig.objects.get(id=channel_id)
            models.algorithmChannel.objects.create(sensor_id=channel.channel_id,
                                                   sensor_name=channel.sensor_name,
                                                   channel_id=channel_id,
                                                   channel_name=channel.channel_name,
                                                   algorithm_channel_id=new_Component_config.id, )
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
        id = request.data.get('id')
        config_id = self.request.data.get('config_id')
        machine = System_Config.models.systemConfig.objects.get(id=config_id)
        machine_code = machine.machine_code
        machine_name = machine.machine_name

        component_name = self.request.data.get('component_name')
        algorithm_id = self.request.data.get('algorithm_id')
        algorithm_name = models.methodConfig.objects.get(id=algorithm_id).algorithm_name
        remark = self.request.data.get('remark')
        channel_count = 5
        channel_name_dictionary = {1: 'null',
                                   2: 'null',
                                   3: 'null',
                                   4: 'null',
                                   5: 'null'}
        channel_id_dictionary = {1: 'null',
                                 2: 'null',
                                 3: 'null',
                                 4: 'null',
                                 5: 'null'}
        input_channel1_id = self.request.data.get('input_channel1')
        if input_channel1_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[1] = System_Config.models.channelConfig.objects.get(
                id=input_channel1_id).channel_id
            channel_name_dictionary[1] = System_Config.models.channelConfig.objects.get(
                id=input_channel1_id).channel_name
        input_channel2_id = self.request.data.get('input_channel2')
        if input_channel2_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[2] = System_Config.models.channelConfig.objects.get(
                id=input_channel2_id).channel_id
            channel_name_dictionary[2] = System_Config.models.channelConfig.objects.get(
                id=input_channel2_id).channel_name
        input_channel3_id = self.request.data.get('input_channel3')
        if input_channel3_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[3] = System_Config.models.channelConfig.objects.get(
                id=input_channel3_id).channel_id
            channel_name_dictionary[3] = System_Config.models.channelConfig.objects.get(
                id=input_channel3_id).channel_name
        input_channel4_id = self.request.data.get('input_channel4')
        if input_channel4_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[4] = System_Config.models.channelConfig.objects.get(
                id=input_channel4_id).channel_id
            channel_name_dictionary[4] = System_Config.models.channelConfig.objects.get(
                id=input_channel4_id).channel_name
        input_channel5_id = self.request.data.get('input_channel5')
        if input_channel5_id is None:
            channel_count = channel_count - 1
        else:
            channel_id_dictionary[5] = System_Config.models.channelConfig.objects.get(
                id=input_channel5_id).channel_id
            channel_name_dictionary[5] = System_Config.models.channelConfig.objects.get(
                id=input_channel5_id).channel_name
        algorithm_channel = channel_name_dictionary[1]
        for j in range(2, channel_count + 1):
            if channel_name_dictionary[j] is not 'null':
                algorithm_channel = f'{algorithm_channel}, {channel_name_dictionary[j]}'
        change_Component_config = (models.componentConfig.objects
                                   .filter(id=id).update(id=id,
                                                         machine_code=machine_code,
                                                         machine_name=machine_name,
                                                         component_name=component_name,
                                                         algorithm_id=algorithm_id,
                                                         algorithm_name=algorithm_name,
                                                         algorithm_channel=algorithm_channel,
                                                         remark=remark, ))
        for m in range(1, channel_count + 1):
            channel_id = channel_id_dictionary[m]
            channel = System_Config.models.channelConfig.objects.get(id=channel_id)
            models.algorithmChannel.objects.create(sensor_id=channel.channel_id,
                                                   sensor_name=channel.sensor_name,
                                                   channel_id=channel_id,
                                                   channel_name=channel.channel_name,
                                                   algorithm_channel_id=change_Component_config.id, )
        response = {
            'status': 200,
            'message': '编辑部件配置成功'
        }
        return JsonResponse(response)

    # # 部件配置 > 编辑
    # @swagger_auto_schema(
    #     operation_summary='部件配置 > 编辑',
    #     request_body=serializer.componentConfigSerializer,
    #     responses={200: '部件配置修改成功'},
    #     tags=["MethodConfig"],
    # )
    # @action(detail=False, methods=['post'])
    # def componentConfigUpdate(self, request):
    #     machine_code = self.request.data.get('machine_code')
    #     machine_name = self.request.data.get('machine_name')
    #     component_name = self.request.data.get('component_name')
    #     algorithm_name = self.request.data.get('algorithm_name')
    #     remark = self.request.data.get('remark')
    #     input_channel1 = self.request.data.get('input_channel1')
    #     input_channel2 = self.request.data.get('input_channel2')
    #     input_channel3 = self.request.data.get('input_channel3')
    #     input_channel4 = self.request.data.get('input_channel4')
    #     input_channel5 = self.request.data.get('input_channel5')
    #     configuration = models.componentConfig.objects.filter(machine_code=machine_code)
    #     configuration.update(machine_code=machine_code,
    #                          machine_name=machine_name,
    #                          component_name=component_name,
    #                          algorithm_name=algorithm_name,
    #                          remark=remark,
    #                          input_channel1=input_channel1,
    #                          input_channel2=input_channel2,
    #                          input_channel3=input_channel3,
    #                          input_channel4=input_channel4,
    #                          input_channel5=input_channel5
    #                          )
    #     response = {
    #         'status': 200,
    #         'message': '编辑部件配置成功'
    #     }
    #     return JsonResponse(response)

    # # 部件配置 > 删除
    # @swagger_auto_schema(
    #     operation_summary='部件配置 > 删除',
    #     request_body=serializer.deleteComponentConfigSerializer,
    #     responses={200: '删除部件配置成功'},
    #     tags=["MethodConfig"],
    # )
    # @action(detail=False, methods=['post'])
    # def deleteComponentConfig(self, request):
    #     g = serializer.deleteComponentConfigSerializer(data=request.data)
    #     g.is_valid()
    #     machine_code = g.validated_data.get('machine_code')
    #     print(machine_code)
    #     models.componentConfig.objects.filter(machine_code=machine_code).delete()
    #     response = {
    #         'status': 200,
    #         'message': '删除部件配置成功'
    #     }
    #     return JsonResponse(response)
    #
