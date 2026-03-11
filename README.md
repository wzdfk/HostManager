1. 项目概述
项目名称：企业内部主机管理系统
技术栈：Python 3.8+、Django 4.2、Django REST Framework、Celery 5.3、Redis（Celery broker/backend）
核心功能：
主机 / 城市 / 机房的 CRUD API；
主机 ping 可达性探测；
主机 root 密码定时随机修改 + 加密存储；
按城市 / 机房维度的每日主机数量统计；
全请求耗时统计。
2. 环境部署
2.1 环境准备
bash
运行
# 1. 创建虚拟环境
conda create -n <"名称"> python=3.12.11
# 激活虚拟环境（Windows）
conda activate <"名称">

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动Redis（Celery依赖）
# Windows：下载Redis并启动redis-server.exe
# Linux：sudo systemctl start redis
2.2 项目初始化
bash
运行
# 1. 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 2. 创建超级管理员
python manage.py createsuperuser

# 3. 启动Django服务
python manage.py runserver 0.0.0.0:8000

# 4. 启动Celery Worker（异步任务）
celery -A host_management worker --loglevel=info

# 5. 启动Celery Beat（定时任务）
celery -A host_management beat --loglevel=info
3. API 文档
表格
接口路径	方法	功能	备注
/api/cities/	GET	查询所有城市	支持分页
/api/cities/	POST	创建城市	需传 name、code
/api/cities/{id}/	PUT	更新城市	
/api/cities/{id}/	DELETE	删除城市	需确保无关联机房
/api/idcs/	GET/POST/PUT/DELETE	机房 CRUD	关联城市
/api/hosts/	GET/POST/PUT/DELETE	主机 CRUD	密码自动加密
/api/hosts/{id}/ping/	GET	探测主机 ping 可达性	返回 reachable 状态
/api/statistics/	GET	查询主机统计数据	只支持查询
4. 核心功能说明
4.1 密码管理
密码存储：使用 Django 内置的make_password加密（PBKDF2 算法），前端无法获取明文；
密码修改：Celery 定时任务每 8 小时调用generate_random_password生成 16 位随机密码，覆盖原有密码；
密码验证：提供check_password方法验证明文密码是否匹配加密后的密码。
4.2 定时任务
密码修改：每 8 小时执行change_all_host_password任务，遍历所有主机修改密码；
数量统计：每天 0 点执行statistic_host_count任务，先删除当日已有统计数据，再按城市 + 机房分组统计并写入数据库。
4.3 请求耗时统计
自定义中间件RequestTimingMiddleware拦截所有请求，记录请求开始 / 结束时间，计算耗时；
耗时以日志形式输出（可扩展写入监控系统），并在响应头X-Request-Duration返回耗时（毫秒）。
4.4 Ping 探测
兼容 Windows/Linux 系统的 ping 命令；
超时时间 5 秒，执行后更新主机状态（online/offline）；
返回探测结果（可达性、状态、错误信息）。
5. 生产环境注意事项
密码安全：
禁止在日志中输出密码相关信息；
生产环境建议使用更复杂的密码生成规则（如 20 位以上，包含更多特殊字符）；
可新增密码修改日志模型，记录修改时间、操作人（如有）。
性能优化：
主机数量大时，定时任务可分批处理（避免一次性修改所有主机密码导致数据库压力）；
统计任务可使用 Django ORM 的annotate分组统计，提升效率。
安全配置：
关闭CORS_ALLOW_ALL_ORIGINS，指定允许的前端域名；
开启 Django 的 HTTPS 配置；
给 API 添加认证（如 JWT），避免匿名访问。
监控告警：
给 Celery 任务添加失败重试机制；
监控主机 ping 不可达的数量，超过阈值时告警；
监控定时任务执行状态，避免任务未执行。