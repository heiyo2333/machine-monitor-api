import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from MachineMonitorApi import settings


def data_to_csv():
    # 这里写入调用接口的代码
    url = f"{settings.BASE_URL}/api/methodConfig/dataToCsv"
    response = requests.get(url)
    print('接口调用结果:', response.status_code)
    pass


scheduler = BackgroundScheduler()
scheduler.add_job(data_to_csv, trigger=CronTrigger(hour=1, minute=00))
scheduler.start()
