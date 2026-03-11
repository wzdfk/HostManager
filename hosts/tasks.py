from celery import shared_task
from django.utils import timezone
from .models import Host, HostStatistics, IDC, City

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