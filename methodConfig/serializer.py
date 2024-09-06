import os

from rest_framework import serializers

from MachineMonitorApi import settings


# 算法配置-显示
class algorithmListSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="算法id")
    algorithm_code = serializers.CharField(help_text="算法编号", max_length=32)  # 算法编号
    algorithm_name = serializers.CharField(help_text="算法名称", max_length=32)  # 算法名称
    algorithm_channel_number = serializers.IntegerField(help_text="算法通道数")  # 算法通道数
    remark = serializers.CharField(help_text="备注", max_length=32, required=False)  # 备注
    algorithm_file = serializers.FileField(help_text="算法文件")  # 算法文件


# 算法配置-新增
class algorithmSerializer(serializers.Serializer):
    algorithm_name = serializers.CharField(help_text="算法名称", max_length=32)  # 算法名称
    algorithm_channel_number = serializers.IntegerField(help_text="算法通道数")  # 算法通道数
    algorithm_file = serializers.CharField(help_text="算法文件")  # 算法文件
    remark = serializers.CharField(help_text="备注", max_length=32, required=False)  # 备注


# 算法配置-编辑
class editAlgorithmSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="算法id")
    algorithm_name = serializers.CharField(help_text="算法名称", max_length=32)  # 算法名称
    algorithm_channel_number = serializers.IntegerField(help_text="算法通道数")  # 算法通道数
    algorithm_file = serializers.CharField(help_text="算法文件")  # 算法文件
    remark = serializers.CharField(help_text="备注", max_length=32, required=False)  # 备注


# 算法配置-删除
class deleteAlgorithmSerializer(serializers.Serializer):
    id = serializers.CharField(help_text="算法id", max_length=32)  # 算法id


# 部件配置-删除
class componentDeleteSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="部件id")


# 部件配置-显示
class componentListSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="部件id")
    machine_code = serializers.CharField(help_text="机床编号", max_length=32)  # 机床编号
    machine_name = serializers.CharField(help_text="机床名称", max_length=32)  # 机床名称
    component_code = serializers.CharField(help_text="部件编号", max_length=32)  # 部件编号
    component_name = serializers.CharField(help_text="部件名称", max_length=32)  # 部件名称
    algorithm_name = serializers.CharField(help_text="算法名称", max_length=32)  # 算法名称
    algorithm_input_channel = serializers.CharField(help_text="算法输入通道", max_length=32)  # 算法输入通道
    remark = serializers.CharField(help_text="备注", max_length=32, required=False)  # 备注


# 部件配置-编辑
class editComponentSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="部件id")
    config_id = serializers.CharField(help_text="系统配置id", max_length=32)  # 系统配置id
    component_name = serializers.CharField(help_text="部件名称", max_length=32)  # 部件名称
    algorithm_id = serializers.IntegerField(help_text="算法id")  # 算法id
    remark = serializers.CharField(help_text="备注", max_length=32, required=False)  # 备注
    # 算法输入通道数据： [{"sensor_id":1,"channel_id":2},{"sensor_id":2,"channel_id":5},{"sensor_id":1,"channel_id":3}]
    algorithm_channel_data = serializers.CharField(help_text="算法输入通道数据")


# 部件配置-新增
class addComponentSerializer(serializers.Serializer):
    config_id = serializers.CharField(help_text="系统配置id", max_length=32)  # 系统配置id
    component_name = serializers.CharField(help_text="部件名称", max_length=32)  # 部件名称
    algorithm_id = serializers.IntegerField(help_text="算法id")  # 算法id
    remark = serializers.CharField(help_text="备注", max_length=32, required=False)  # 备注
    # 算法输入通道数据： [{"sensor_id":1,"channel_id":2},{"sensor_id":2,"channel_id":5},{"sensor_id":1,"channel_id":3}]
    algorithm_channel_data = serializers.CharField(help_text="算法输入通道数据")


# 上传文件
class uploadFileSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="上传文件")

    def save(self):
        file = self.validated_data['file']
        # 定义上传路径
        upload_path = os.path.join(settings.MEDIA_ROOT, 'UploadFile')

        # 如果目录不存在则创建
        os.makedirs(upload_path, exist_ok=True)

        # 定义完整的文件路径
        file_path = os.path.join(upload_path, file.name)

        # 保存文件到指定路径
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        # 构造返回的文件 URL，并将路径中的反斜杠替换为正斜杠
        file_url = os.path.normpath(os.path.join(settings.MEDIA_URL, 'UploadImage', file.name)).replace('\\', '/')

        return file_url
