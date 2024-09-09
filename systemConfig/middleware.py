from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

from systemConfig.models import systemConfig
import requests
import subprocess
import time


def start_influxdb():
    try:
        # 尝试启动 InfluxDB
        subprocess.run(
            ["cmd", "/c", "start", "/min", "cmd", "/c", "D:\\influx\\influxdb\\influxdb-1.8.10-1\\influxd -config D:\\influx\\influxdb\\influxdb-1.8.10-1\\influxdb.conf"],
            check=True
        )
        print("InfluxDB is starting...")
        # 增加等待时间
        time.sleep(15)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start InfluxDB: {e}")


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
        try:
            # 发送一个简单的请求到 InfluxDB 的 Ping 端点
            response = requests.get('http://localhost:8086/ping')
            if response.status_code == 204:
                pass
                # influxdb正常启动中
                # print("InfluxDB is running.")
            else:
                print("InfluxDB is not responding correctly.")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection Error: {e}")
            # 如果连接错误，尝试启动 InfluxDB
            print("Trying to start InfluxDB...")
            start_influxdb()
            # 再次检查 InfluxDB 是否运行
        except Exception as e:
            print(f"An error occurred: {e}")

