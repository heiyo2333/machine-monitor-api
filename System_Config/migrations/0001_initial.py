# Generated by Django 3.2 on 2024-05-30 10:29

from django.db import migrations, models
import django.db.models.deletion


def create_initial_data(apps, schema_editor):
    Model1 = apps.get_model('System_Config', 'systemConfig')
    Model2 = apps.get_model('System_Config', 'sensorConfig')
    Model3 = apps.get_model('System_Config', 'channelConfig')
    # 初始化系统配置1
    Model1.objects.create(id=1, machine_code='vmc850', machine_name='大恒机床VMC850', machine_type='五轴加工中心',
                          machine_description='大恒机床-五轴-VMC850', manager='张三', machine_ip='192.168.110.23',
                          machine_port=7798, tool_number=30, database_name='ComponentMonitor',
                          alarm_data_delay_positive=30, alarm_data_delay_negative=10, is_apply=1)
    # 初始化加速度传感器
    Model2.objects.create(pk=1, sensor_code="Principal-DH5501R-Px", sensor_name='主轴-三相加速度传感器', frequency=100,
                          channel_number=3, sensor_status=1)
    Model3.objects.create(id=1, sensor_name="主轴-三相加速度传感器", channel_name='加速度-X', overrun_times=3,
                          channel_field='AcceleratedSpeed_X', is_monitor=1, channel_id=1)
    Model3.objects.create(id=2, sensor_name="主轴-三相加速度传感器", channel_name='加速度-Y', overrun_times=3,
                          channel_field='AcceleratedSpeed_Y', is_monitor=1, channel_id=1)
    Model3.objects.create(id=3, sensor_name="主轴-三相加速度传感器", channel_name='加速度-Z', overrun_times=3,
                          channel_field='AcceleratedSpeed_Z', is_monitor=1, channel_id=1)
    # 初始化电流传感器
    Model2.objects.create(pk=2, sensor_code="Principal-KXT237I-VD", sensor_name='主轴-三相交流电流传感器', frequency=100,
                          channel_number=3,
                          sensor_status=1)
    Model3.objects.create(id=4, sensor_name="主轴-三相交流电流传感器", channel_name='电流-U', overrun_times=3,
                          channel_field='Current_X', is_monitor=1, channel_id=2)
    Model3.objects.create(id=5, sensor_name="主轴-三相交流电流传感器", channel_name='电流-V', overrun_times=3,
                          channel_field='Current_Y', is_monitor=1, channel_id=2)
    Model3.objects.create(id=6, sensor_name="主轴-三相交流电流传感器", channel_name='电流-W', overrun_times=3,
                          channel_field='Current_Z', is_monitor=1, channel_id=2)

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='sensorConfig',
            fields=[
                ('sensor_code', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('sensor_name', models.CharField(max_length=32, null=True)),
                ('frequency', models.IntegerField(null=True)),
                ('channel_number', models.IntegerField(null=True)),
                ('remark', models.CharField(max_length=32, null=True)),
                ('sensor_status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='systemConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_code', models.CharField(max_length=32, null=True)),
                ('machine_name', models.CharField(max_length=32, null=True)),
                ('machine_type', models.CharField(max_length=32, null=True)),
                ('machine_description', models.CharField(max_length=32, null=True)),
                ('manager', models.CharField(max_length=32, null=True)),
                ('machine_ip', models.CharField(max_length=32, null=True)),
                ('machine_port', models.IntegerField(null=True)),
                ('tool_number', models.IntegerField(null=True)),
                ('database_name', models.CharField(max_length=32, null=True)),
                ('alarm_data_delay_positive', models.IntegerField(null=True)),
                ('alarm_data_delay_negative', models.IntegerField(null=True)),
                ('is_apply', models.BooleanField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='channelConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=32, null=True)),
                ('channel_name', models.CharField(max_length=32, null=True)),
                ('overrun_times', models.IntegerField(null=True)),
                ('channel_field', models.CharField(max_length=32, null=True)),
                ('is_monitor', models.BooleanField(default=False)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='System_Config.sensorconfig')),
            ],
        ),
        migrations.RunPython(create_initial_data),
    ]
