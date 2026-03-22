from celery import shared_task
from django.utils import timezone
from .models import Host, HostStatistics, IDC, City

"""
shared_task装饰器将函数注册为Celery任务，使其可以被异步调用和定时调度。
1. 异步手动调用：在代码中直接调用change_all_host_passwords.delay()或count_hosts.delay()，任务会被发送到Celery队列异步执行。 前端可以立即得到响应，而不必等待任务完成。
2. 定时调度：使用Celery Beat等工具，可以设置定时任务，例如每隔八小时自动调用change_all_host_passwords()，每天00:00自动调用count_hosts()，实现自动化的定时任务执行。
"""

@shared_task
def change_all_host_passwords():
    """定时任务：每隔八小时修改所有主机密码"""
    hosts = Host.objects.all()
    for host in hosts:
        new_password = Host.generate_random_password()
        host.set_password(new_password)
    return f"已修改 {hosts.count()} 台主机的密码"

@shared_task
def count_hosts():
    """定时任务：每天00:00统计主机数量"""
    today = timezone.now().date()

    # 先删除当天已有的统计数据
    HostStatistics.objects.filter(statistic_date=today).delete()

    cities = City.objects.all()
    for city in cities:
        idcs = IDC.objects.filter(city=city)
        for idc in idcs:
            host_count = Host.objects.filter(idc=idc).count()
            HostStatistics.objects.create(
                city=city,
                idc=idc,
                host_count=host_count,
                statistic_date=today
            )
    return f"已统计 {HostStatistics.objects.filter(statistic_date=today).count()} 条主机统计数据"