from rest_framework import serializers
from .models import City, IDC, Host, HostStatistics

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"

class IDCSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        # 序列化器的核心配置规则

        # 关联的模型
        model = IDC

        # 需要序列化的字段 (可以是一个列表，也可以是 "__all__" 表示所有字段)
        fields = "__all__"

class HostSerializer(serializers.ModelSerializer):
    # 序列化器会自动生成沿用模型框架里的字段。 如果需要额外添加一些字段（比如关联对象的名称），可以如下所示定义。
    # 额外定义的字段，用于显示所属的机房和城市名称
    idc_name = serializers.CharField(source="idc.name", read_only=True)
    city_name = serializers.CharField(source="idc.city.name", read_only=True)

    class Meta:
        model = Host
        fields = "__all__"
        extra_kwargs = {
            "root_password": {"write_only": True}  # 只允许写入，不返回给前端
        }

class HostStatisticsSerializer(serializers.ModelSerializer):
    idc_name = serializers.CharField(source="idc.name", read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = HostStatistics
        fields = "__all__"
