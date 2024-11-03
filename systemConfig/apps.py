from django.apps import AppConfig
import threading
import subprocess
import time
import psutil


class SystemConfigurationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'systemConfig'

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'systemConfig'

    def ready(self):
        # 启动后台线程
        thread = threading.Thread(target=self.monitor_test_sensors, daemon=True)
        thread.start()

    def monitor_test_sensors(self):
        while True:
            # 每隔10秒检查一次 test_sensors.exe 是否在运行
            if not self.is_program_running("test_sensors.exe"):
                try:
                    subprocess.Popen(["start", "cmd", "/k", "D:\\machine-monitor-api\\systemConfig\\test_sensors.exe"],
                                     shell=True)
                    print("test_sensors.exe is starting...")
                except Exception as e:
                    print(f"Failed to start test_sensors.exe: {e}")
            time.sleep(5)  # 每10秒检查一次

    # def is_program_running(self, program_name):
    #     try:
    #         output = subprocess.check_output('tasklist', shell=True, text=True)
    #         return program_name in output
    #     except subprocess.CalledProcessError as e:
    #         print(f"Error checking running programs: {e}")
    #         return False
    def is_program_running(self, program_name):
        # 使用 psutil 检查是否有指定的程序正在运行
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == program_name:
                return True
        return False
