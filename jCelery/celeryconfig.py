from datetime import timedelta

from celery.schedules import crontab

broker_url = 'redis://127.0.0.1:6379/0'
result_backend = 'redis://127.0.0.1:6379/1'
# 三个队列
task_routes = {
    'jd.tasks.first.*': {'queue': 'jd.celery.first'},  # 优先级高队列
    'jd.tasks.telegram.*': {'queue': 'jd.celery.telegram'},  # tg队列
}
# 默认队列
task_default_queue = 'jd.tasks.first'

beat_schedule = {
    'chemical_data_get_job': {
        'task': 'jd.tasks.first.spider_chemical.chemical_data_get_job',
        'schedule': timedelta(days=1),
    },
    'tg_chat_history_job': {
        'task': 'jd.tasks.first.tg_history_job.fetch_tg_history_job',
        'schedule': timedelta(minutes=10),
    },
    # 'tg_account_history_job': {
    #     'task': 'jd.tasks.first.tg_history_job.fetch_account_history_job',
    #     'schedule': timedelta(minutes=45),
    # },
    'send_file_job': {
        'task': 'jd.tasks.first.send_file_job.send_file_job',
        'schedule': crontab(minute=0, hour=9),
    }
}
