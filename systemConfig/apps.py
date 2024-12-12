from django.apps import AppConfig
import threading
import subprocess
import time
import psutil


class SystemConfigurationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'systemConfig'

    def ready(self):
        # 启动后台线程
        thread = threading.Thread(target=self.monitor_test_sensors, daemon=True)
        thread.start()

    def monitor_test_sensors(self):
        while True:
            # 每隔 5 秒检查一次 test_sensors.py 是否在运行
            if not self.is_program_running("test_sensors.py"):
                try:
                    # 使用 python 启动 test_sensors.py
                    subprocess.Popen(["python", r"D:\machine-monitor-api\systemConfig\test_sensors.py"])
                    print("test_sensors.py is starting...")
                except FileNotFoundError as fnf_error:
                    print(f"File not found: {fnf_error}")
                except Exception as e:
                    print(f"Failed to start test_sensors.py: {e}")
            time.sleep(5)  # 每 5 秒检查一次

    def is_program_running(self, program_name):
        # 使用 psutil 检查是否有指定的程序正在运行
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            # 检查进程是否为 Python 进程，且命令行中包含目标脚本的路径
            if 'python' in proc.info['name'].lower():
                if any(program_name in part for part in proc.info['cmdline']):
                    return True
        return False
