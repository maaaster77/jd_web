broker_url = 'redis://127.0.0.1:6379/0'
result_backend = 'redis://127.0.0.1:6379/1'
# 三个队列
task_routes = {
    'jd.tasks.first.*': {'queue': 'jd.celery.first'},  # 优先级高队列
}
# 默认队列
task_default_queue = 'jd.tasks.first'
