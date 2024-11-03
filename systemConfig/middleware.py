import threading

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from systemConfig.models import systemConfig
import requests
import subprocess
import time


# test_sensors_lock = threading.Lock()
# test_sensors_running_flag = False


# # 先检查是否已有 test_sensors.exe 在运行
# def start_test_sensors():
#     global test_sensors_running_flag
#     with test_sensors_lock:
#         if not is_program_running("test_sensors.exe") and not test_sensors_running_flag:
#             try:
#                 # 后台启动 test_sensors.exe
#                 # subprocess.Popen(["D:\\machine-monitor-api\\systemConfig\\test_sensors.exe"])
#                 # 命令窗启动 test_sensors.exe
#                 # subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", "D:\\machine-monitor-api\\systemConfig\\test_sensors.exe"])
#                 subprocess.Popen(["start", "cmd", "/k", "D:\\machine-monitor-api\\systemConfig\\test_sensors.exe"],
#                                  shell=True)
#                 test_sensors_running_flag = True
#                 print("test_sensors.exe is starting...")
#             except Exception as e:
#                 print(f"Failed to start test_sensors.exe: {e}")
#
#
# # 检查程序是否在运行
# def is_program_running(program_name):
#     global test_sensors_running_flag
#     try:
#         output = subprocess.check_output('tasklist', shell=True, text=True)
#         is_running = program_name in output
#         test_sensors_running_flag = is_running
#         return is_running
#     except subprocess.CalledProcessError as e:
#         print(f"Error checking running programs: {e}")
#         return False
#
#
# def start_influxdb():
#     try:
#         # 尝试启动 InfluxDB
#         subprocess.run(
#             ["cmd", "/c", "start", "/min", "cmd", "/c",
#              "D:\\influx\\influxdb\\influxdb-1.8.10-1\\influxd -config D:\\influx\\influxdb\\influxdb-1.8.10-1\\influxdb.conf"],
#             check=True
#         )
#         print("InfluxDB is starting...")
#         # 增加等待时间
#         time.sleep(15)
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to start InfluxDB: {e}")


class ConfigMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 检查请求是否为 System_Configuration 或 Adaptive_Learning 应用程序
        if request.path.startswith('/api/config/'):
            return None

        # 只对 System_Configuration 和 Adaptive_Learning 应用程序执行中间件逻辑
        config_list = systemConfig.objects.all()
        is_apply = any(x.is_apply == 1 for x in config_list)

        if not is_apply:
            response = {
                'status': 15,
                'message': '当前无正在应用的配置',
            }
            return JsonResponse(response)

# # 检测时序数据库开启
# class InfluxdbMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         # 检查请求是否为 System_Configuration 或 Adaptive_Learning 应用程序
#         if request.path.startswith('/api/config/'):
#             return None
#
#         # 只对 System_Configuration 和 Adaptive_Learning 应用程序执行中间件逻辑
#         try:
#             # 发送一个简单的请求到 InfluxDB 的 Ping 端点
#             response = requests.get('http://localhost:8086/ping')
#             if response.status_code == 204:
#                 pass
#                 # influxdb正常启动中
#                 # print("InfluxDB is running.")
#             else:
#                 print("InfluxDB is not responding correctly.")
#         except requests.exceptions.ConnectionError as e:
#             print(f"Connection Error: {e}")
#             # 如果连接错误，尝试启动 InfluxDB
#             print("Trying to start InfluxDB...")
#             start_influxdb()
#             # 再次检查 InfluxDB 是否运行
#         except Exception as e:
#             print(f"An error occurred: {e}")


# class SensorDetectMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         # 检查请求是否为 System_Configuration 或 Adaptive_Learning 应用程序
#         if request.path.startswith('/api/config/'):
#             return None
#
#         # 检查 test_sensors.exe 是否在运行
#         if not is_program_running("test_sensors.exe"):
#             print("test_sensors.exe is not running. Starting it now...")
#             start_test_sensors()
#         else:
#             print("test_sensors.exe is already running.")
