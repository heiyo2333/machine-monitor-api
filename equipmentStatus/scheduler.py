import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from MachineMonitorApi import settings


def add_thermal_diagram():
    # 这里写入调用接口的代码
    url = f"{settings.BASE_URL}/api/equipmentStatus/addThermalDiagram"
    response = requests.post(url)
    print('接口调用结果:', response.status_code)
    pass


def algorithm_monitor():
    # 这里写入调用接口的代码
    url = f"{settings.BASE_URL}/api/equipmentStatus/algorithmMonitor"
    response = requests.get(url, params={"config_id": 1})
    print('接口调用结果:', response.status_code)
    pass


def home():
    url1 = f"{settings.BASE_URL}/api/equipmentStatus/findParameter"
    response = requests.get(url1, params={"config_id": 1})
    print('接口调用结果:', response.status_code)
    url2 = f"{settings.BASE_URL}/api/equipmentStatus/componentTreeList"
    response = requests.get(url2, params={"config_id": 1})
    print('接口调用结果:', response.status_code)
    url3 = f"{settings.BASE_URL}/api/equipmentStatus/thermalDiagramList"
    response = requests.get(url3, params={"config_id": 1})
    print('接口调用结果:', response.status_code)
    url4 = f"{settings.BASE_URL}/api/equipmentStatus/machineInformation"
    response = requests.get(url4, params={"config_id": 1})
    print('接口调用结果:', response.status_code)
    url5 = f"{settings.BASE_URL}/api/equipmentStatus/remainingLife"
    response = requests.get(url5, params={"component_id": 1})
    print('接口调用结果:', response.status_code)
    url6 = f"{settings.BASE_URL}/api/equipmentStatus/algorithmStatusList"
    response = requests.get(url6, params={"current": 1, "pageSize": 3, "config_id": 1})
    print('接口调用结果:', response.status_code)
    url7 = f"{settings.BASE_URL}/api/equipmentStatus/componentStatus"
    response = requests.get(url7, params={"current": 1, "pageSize": 4, "config_id": 1})
    print('接口调用结果:', response.status_code)
    url8 = f"{settings.BASE_URL}/api/equipmentStatus/faultInformationList"
    response = requests.get(url8, params={"config_id": 1})
    print('接口调用结果:', response.status_code)
    pass


scheduler = BackgroundScheduler()
scheduler.add_job(add_thermal_diagram, trigger=CronTrigger(hour=6, minute=00))
scheduler.add_job(algorithm_monitor, trigger=CronTrigger(hour=2, minute=00))
scheduler.add_job(home, trigger=CronTrigger(hour=7, minute=00))
scheduler.start()
