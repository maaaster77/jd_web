import logging

from jCelery import celery
from jd import db
from jd.jobs.chat_history import TgChatHistoryJob

logger = logging.getLogger(__name__)


@celery.task
def fetch_tg_history_job():
    logger.info('start fetch_tg_history_job...')
    TgChatHistoryJob().main()
    db.session.commit()
    logger.info('end...')

