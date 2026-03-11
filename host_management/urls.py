from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hosts.views import CityViewSet, IDCViewSet, HostViewSet, HostStatisticsViewSet, home

# 注册DRF路由
router = DefaultRouter()
router.register(r"cities", CityViewSet)
router.register(r"idcs", IDCViewSet)
router.register(r"hosts", HostViewSet)
router.register(r"statistics", HostStatisticsViewSet)

urlpatterns = [
    path("", home, name="home"),  # 首页
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),  # API前缀
]