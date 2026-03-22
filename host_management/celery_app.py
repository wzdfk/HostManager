import os
from celery import Celery
from celery.schedules import crontab

# 设置 django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'host_management.settings')

# 创建celery实例
app = Celery('host_management')
# 从django的settings.py中加载celery配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 配置自动发现任务模块
app.autodiscover_tasks()

# 配置定时任务  celery beat的定时任务配置，使用crontab来设置执行时间
app.conf.beat_schedule = {
    # 每隔八小时修改所有主机密码
    'change-host-password-every-8-hours': {
        'task': 'hosts.tasks.change_all_host_passwords',
        'schedule': crontab(hour='*/8'),  # 每8小时执行一次
    },

    # 每天00:00统计主机数量
    'count-hosts-every-day': {
        'task': 'hosts.tasks.count_hosts',
        'schedule': crontab(hour=0, minute=0),  # 每天00:00执行一次
    },
}
