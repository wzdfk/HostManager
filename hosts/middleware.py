# hosts/middleware.py
import time
import logging

# 明确指定日志名称，避免和其他日志混淆
logger = logging.getLogger('request_timing')


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. 记录请求开始时间
        start_time = time.time()

        # 2. 处理请求（执行后续中间件+视图）
        response = self.get_response(request)

        # 3. 计算耗时（毫秒，保留2位小数）
        duration = (time.time() - start_time) * 1000
        duration_str = f"{duration:.2f}ms"

        # 4. 打印日志（强制输出到控制台，避免日志配置问题）
        log_msg = (
            f"[请求耗时统计] "
            f"路径: {request.path} | "
            f"方法: {request.method} | "
            f"状态码: {response.status_code} | "
            f"耗时: {duration_str}"
        )
        # 方式1：logger.info（依赖日志配置）
        logger.info(log_msg)
        # 方式2：print（保底，确保能看到）
        print(log_msg)

        # 5. 添加响应头
        response['X-Request-Duration'] = duration_str

        return response