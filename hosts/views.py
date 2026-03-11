import subprocess
import platform
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import City, IDC, Host, HostStatistics
from .serializers import CitySerializer, IDCSerializer, HostSerializer, HostStatisticsSerializer
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse(
        "<h1>主机管理系统首页</h1><p>访问 <a href='/api/'>API 接口</a> 或 <a href='/admin/'>后台管理</a></p>")

# 通用的 “CRUD” 视图集
class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer

class IDCViewSet(viewsets.ModelViewSet):
    queryset = IDC.objects.all()
    serializer_class = IDCSerializer

class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

    # 创建主机
    def perform_create(self, serializer):
        """创建主机时自动加密密码"""
        raw_password = serializer.validated_data.pop("root_password", Host.generate_random_password())
        host = serializer.save()
        host.set_password(raw_password)

    # ping 操作
    @action(detail=True, methods=["get"])
    def ping(self, request, pk=None):
        """探测主机是否ping可到达"""
        host = self.get_object()
        ip = host.ip

        # 构造ping命令
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", ip]

        try:
            # 执行ping命令 超市五秒
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                text=True,
            )
            reachable = result.returncode == 0
            # 更新主机状态
            host.status = "online" if reachable else "offline"
            host.save()

            return Response({
                "ip": ip,
                "reachable": reachable,
                "status": host.status,
            })
        except subprocess.TimeoutExpired:
            return Response({
                "ip": ip,
                "reachable": False,
                "error": "Ping超时"
            }, status=status.HTTP_408_REQUEST_TIMEOUT)
        except Exception as e:
            return Response({
                "ip": ip,
                "reachable": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HostStatisticsViewSet(viewsets.ModelViewSet):
    """统计数据只允许查询"""
    queryset = HostStatistics.objects.all()
    serializer_class = HostStatisticsSerializer