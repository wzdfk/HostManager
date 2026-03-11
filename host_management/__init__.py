# host_management/__init__.py
from .celery_app import app as celery_app  # 对应新文件名

__all__ = ('celery_app',)