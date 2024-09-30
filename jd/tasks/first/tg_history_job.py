from jCelery import celery
from jd.jobs.chat_history import TgChatHistoryJob


@celery.task
def fetch_tg_history_job():
    TgChatHistoryJob().main()