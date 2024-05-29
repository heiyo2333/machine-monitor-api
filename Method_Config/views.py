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


class MethodConfigViewSet(viewsets.GenericViewSet):
    authentication_classes = (BasicAuthentication,)

    # 返回数据库所有对象.
    def get_queryset(self):
        return models.methodConfig.objects.all()

    # 算法配置查询
    @swagger_auto_schema(
        operation_summary='监测信号展示 > 算法配置查询',
        # 获取参数
        manual_parameters=[
            # openapi.Parameter('id', openapi.IN_QUERY, description='算法编号', type=openapi.TYPE_STRING,
            #                   required=False),
            # openapi.Parameter('algorithm_name', openapi.IN_QUERY, description='算法名称', type=openapi.TYPE_STRING,
            #                   required=False),
            # openapi.Parameter('algorithm_channel_number', openapi.IN_QUERY, description='算法通道数',
            #                   type=openapi.TYPE_INTEGER, required=False),
            # openapi.Parameter('remark', openapi.IN_QUERY, description='备注', type=openapi.TYPE_STRING,
            #                   required=True),
            openapi.Parameter('pageSize', openapi.IN_QUERY, description='一页多少条', type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('current', openapi.IN_QUERY, description='当前页面号', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.MethodConfigDisplaySerializer)},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['get'])
    def methodConfigList(self, request):
        # cutter_type = self.request.query_params.get('cutterType')
        # cutter_material = self.request.query_params.get('cutterMaterial')
        # cutter_brand = self.request.query_params.get('cutterBrand')
        # cutter_status = self.request.query_params.get('cutterStatus')
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))
        first = (current - 1) * pageSize
        last = current * pageSize
        method = self.get_queryset()
        # if cutter_type or cutter_material or cutter_brand or cutter_status:
        #     # 创建五个查询Q对象,默认条件全为非空,按照要求更新指定条件
        #     condition1 = Q(cutter_type__isnull=False)
        #     condition2 = Q(cutter_material__isnull=False)
        #     condition3 = Q(cutter_brand__isnull=False)
        #     condition4 = Q(cutter_status__isnull=False)
        #     if cutter_type:
        #         cutter_type = models.context.objects.get(id=cutter_type).name
        #         condition1 = Q(cutter_type=cutter_type)
        #     if cutter_material:
        #         cutter_material = models.context.objects.get(id=cutter_material).name
        #         condition2 = Q(cutter_material=cutter_material)
        #     if cutter_brand:
        #         condition3 = Q(cutter_brand=cutter_brand)
        #     if cutter_status:
        #         cutter_status = models.context.objects.get(id=cutter_status).name
        #         condition4 = Q(cutter_status=cutter_status)
        #     combined_condition = (condition1 & condition2 & condition3 & condition4)
        #     tool_magazine_all = tool.filter(combined_condition)[first:last]
        #     total = tool.filter(combined_condition).count()
        # else:
        #     # 如果查询条件全部默认,直接返回全部的数据.
        #     tool_magazine_all = tool.all()[first:last]
        #     total = tool.all().count()
        method_config_all = method[first:last]
        total = method.count()
        result_list = []
        for x in method_config_all:
            result_list.append(
                {
                    'id': x.id,
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

    # 部件配置查询
    @swagger_auto_schema(
        operation_summary='监测信号展示 > 部件配置查询',
        # 获取参数
        manual_parameters=[
            openapi.Parameter('machine_number', openapi.IN_QUERY, description='机床编号', type=openapi.TYPE_STRING,
                              required=True),
            openapi.Parameter('pageSize', openapi.IN_QUERY, description='一页多少条', type=openapi.TYPE_INTEGER,
                              required=True),
            openapi.Parameter('current', openapi.IN_QUERY, description='当前页面号', type=openapi.TYPE_INTEGER,
                              required=True),
        ],
        responses={200: openapi.Response('successful', serializer.ComponentConfigDisplaySerializer)},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['get'])
    def componentConfigList(self, request):
        machine_number = self.request.query_params.get('machine_number')
        pageSize = int(self.request.query_params.get('pageSize'))
        current = int(self.request.query_params.get('current'))

        first = (current - 1) * pageSize
        last = current * pageSize

        component = models.componentConfig.objects.filter(machine_number=machine_number)[first:last]
        total = models.componentConfig.objects.filter(machine_number=machine_number).count()
        result_list = []
        for x in component:
            result_list.append(
                {
                    'machine_number': x.machine_number,
                    'machine_name': x.machine_name,
                    'component_name': x.component_name,
                    'algorithm_name': x.algorithm_name,
                    'input_channel': x.input_channel,
                    'remark': x.remark,
                    'algorithm_id': x.algorithm_id,
                    'sensor_id': x.sensor_id,
                    'channel_id': x.channel_id,
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

    # 新增算法配置
    @swagger_auto_schema(
        operation_summary='新增算法配置',
        request_body=serializer.MethodConfigDisplaySerializer,
        responses={200: '新增算法配置成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def addMethodConfig(self, request):
        algorithm_name = self.request.data.get('algorithm_name')
        remark = self.request.data.get('remark')
        algorithm_channel_number = self.request.data.get('algorithm_channel_number')
        algorithm_file = self.request.data.get('algorithm_file')
        new_method_configuration = models.methodConfig.objects.create(algorithm_name=algorithm_name,
                                                                      algorithm_channel_number=algorithm_channel_number,
                                                                      algorithm_file=algorithm_file,
                                                                      remark=remark)
        response = {
            'data': {'id': new_method_configuration.id},
            'status': 200,
            'message': '新增算法配置成功'
        }
        return JsonResponse(response)

    # 删除算法配置
    @swagger_auto_schema(
        operation_summary='删除算法配置',
        request_body=serializer.MethodConfigDisplaySerializer,
        responses={200: '删除算法配置成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def deleteMethodConfig(self, request):
        g = serializer.MethodConfigDisplaySerializer(data=request.data)
        g.is_valid()
        algorithm_id = g.validated_data.get('id')
        print(algorithm_id)
        models.methodConfig.objects.filter(id=id).delete()

        response = {
            'status': 200,
            'message': '删除算法配置成功'
        }
        return JsonResponse(response)

    # 修改算法配置
    @swagger_auto_schema(
        operation_summary='修改算法配置',
        request_body=serializer.MethodConfigDisplaySerializer,
        responses={200: '算法配置修改成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def methodConfigUpdate(self, request):
        id = self.request.data.get('id')
        remark = self.request.data.get('remark')
        algorithm_channel_number = self.request.data.get('algorithm_channel_number')
        algorithm_file = self.request.data.get('algorithm_file')
        configuration = models.methodConfig.objects.get(id=id)
        configuration.update(id=id,
                             algorithm_channel_number=algorithm_channel_number,
                             algorithm_file=algorithm_file,
                             remark=remark)
        response = {
            'status': 200,
            'message': '修改算法配置成功'
        }
        return JsonResponse(response)

    # 新增部件配置
    @swagger_auto_schema(
        operation_summary='新增部件配置',
        request_body=serializer.ComponentConfigDisplaySerializer,
        responses={200: '新增部件配置成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def addComponentConfig(self, request):
        machine_name = self.request.data.get('machine_name')
        component_name = self.request.data.get('component_name')
        algorithm_name = self.request.data.get('algorithm_name')
        remark = self.request.data.get('remark')
        algorithm_id = self.request.data.get('algorithm_id')
        sensor_id = self.request.data.get('sensor_id')
        channel_id = self.request.data.get('channel_id')
        new_Component_config = models.methodConfig.objects.create(machine_name=machine_name,
                                                                  component_name=component_name,
                                                                  algorithm_name=algorithm_name,
                                                                  remark=remark,
                                                                  algorithm_id=algorithm_id,
                                                                  sensor_id=sensor_id,
                                                                  channel_id=channel_id)
        response = {
            'data': {'id': new_Component_config.id},
            'status': 200,
            'message': '新增部件配置成功'
        }
        return JsonResponse(response)

    # 删除部件配置
    @swagger_auto_schema(
        operation_summary='删除部件配置',
        request_body=serializer.ComponentConfigDisplaySerializer,
        responses={200: '删除部件配置成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def deleteComponentConfig(self, request):
        g = serializer.ComponentConfigDisplaySerializer(data=request.data)
        g.is_valid()
        machine_number = g.validated_data.get('machine_number')
        print(machine_number)
        models.componentConfig.objects.filter(machine_number=machine_number).delete()

        response = {
            'status': 200,
            'message': '删除部件配置成功'
        }
        return JsonResponse(response)

    # 修改部件配置
    @swagger_auto_schema(
        operation_summary='修改部件配置',
        request_body=serializer.ComponentConfigDisplaySerializer,
        responses={200: '部件配置修改成功'},
        tags=["MethodConfig"],
    )
    @action(detail=False, methods=['post'])
    def componentConfigUpdate(self, request):
        machine_name = self.request.data.get('machine_name')
        component_name = self.request.data.get('component_name')
        algorithm_name = self.request.data.get('algorithm_name')
        remark = self.request.data.get('remark')
        algorithm_id = self.request.data.get('algorithm_id')
        sensor_id = self.request.data.get('sensor_id')
        channel_id = self.request.data.get('channel_id')
        configuration = models.componentConfig.objects.get(machine_name=machine_name)
        configuration.update(machine_name=machine_name,
                             component_name=component_name,
                             algorithm_name=algorithm_name,
                             remark=remark,
                             algorithm_id=algorithm_id,
                             sensor_id=sensor_id,
                             channel_id=channel_id)
        response = {
            'status': 200,
            'message': '修改部件配置成功'
        }
        return JsonResponse(response)
