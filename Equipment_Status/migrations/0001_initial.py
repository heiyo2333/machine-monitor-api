# Generated by Django 3.2 on 2024-06-04 11:58

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='faultCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config_id', models.IntegerField(null=True)),
                ('machine_code', models.CharField(max_length=32, null=True)),
                ('machine_name', models.CharField(max_length=32, null=True)),
                ('warning_time', models.CharField(max_length=32)),
                ('component_id', models.IntegerField(null=True)),
                ('component_name', models.CharField(max_length=32, null=True)),
                ('fault_type', models.CharField(max_length=32)),
                ('fault_code', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='thermalDiagram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config_id', models.IntegerField(null=True)),
                ('machine_code', models.CharField(max_length=32, null=True)),
                ('machine_name', models.CharField(max_length=32, null=True)),
                ('machine_process_date', models.DateField(default=timezone.now)),
                ('machine_running_time', models.CharField(max_length=32)),
            ],
        ),
    ]
