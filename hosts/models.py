import random
import string
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# 配置主机模型
class City(models.Model):
    """城市模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name="城市名称")
    code = models.CharField(max_length=10, unique=True, verbose_name="城市代码")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        # 单数显示名
        verbose_name = "城市"
        # 复数显示名
        verbose_name_plural = "城市列表"
        # 排序规则
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

# 配置机房模型
class IDC(models.Model):
    """机房模型"""
    name = models.CharField(max_length=100, verbose_name="机房名称")
    code = models.CharField(max_length=20, unique=True, verbose_name="机房编码")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="idcs", verbose_name="所属城市")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="机房地址")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "机房"
        verbose_name_plural = "机房列表"
        unique_together = ("name", "city")  # 同一城市内机房名称唯一

    def __str__(self):
        return f"{self.city.name} ({self.code})--{self.name}"

class Host(models.Model):
    """主机模型"""
    STATUS_CHOICES = (
        ("unknown", "未知"),
        ("online", "在线"),
        ("offline", "离线"),
    )

    hostname = models.CharField(max_length=100, unique=True, verbose_name="主机名")
    ip = models.GenericIPAddressField(unique=True, verbose_name="IP地址")
    idc = models.ForeignKey(IDC, on_delete=models.CASCADE, related_name="hosts", verbose_name="所属机房")
    root_password = models.CharField(max_length=255, verbose_name="Root密码（加密）")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unknown", verbose_name="主机状态")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "主机"
        verbose_name_plural = "主机列表"
        ordering = ["hostname"]

    def __str__(self):
        return f"{self.idc.name}--{self.hostname}"

    # 加密存储密码
    def set_password(self, raw_password):
        self.root_password = make_password(raw_password)
        self.save()

    # 验证密码
    def check_password(self, raw_password):
        return check_password(raw_password, self.root_password)

    @staticmethod
    def generate_random_password(length=16):
        """生成随机密码 (字母+数字+字符)"""
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(length))


# 配置统计模型
class HostStatistics(models.Model):
    """主机统计模型"""
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="城市")
    idc = models.ForeignKey(IDC, on_delete=models.CASCADE, verbose_name="机房")
    host_count = models.IntegerField(default=0, verbose_name="主机数量")
    statistic_date = models.DateField(verbose_name="统计日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "主机统计"
        verbose_name_plural = "主机统计"
        unique_together = [["city", "idc", "statistic_date"]]  # 同一日期+城市+机房只存一条

    def __str__(self):
        return f"{self.statistic_date}-{self.city.name}-{self.idc.name}-{self.host_count}台"