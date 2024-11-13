import datetime
import logging

from jCelery import celery
from jd import db, app
from jd.jobs.chat_history import TgChatHistoryJob
from jd.models.job_queue_log import JobQueueLog
from jd.models.tg_account import TgAccount
from jd.services.job_queue import JobQueueLogService
from jd.tasks.telegram.tg import fetch_person_chat_history

logger = logging.getLogger(__name__)


@celery.task
def fetch_tg_history_job():
    db.session.remove()
    logger.info('start fetch_tg_history_job...')
    job_name = 'fetch_tg_history'
    flag, queue = JobQueueLogService.add(job_name)
    db.session.commit()
    if not flag:
        return
    try:
        TgChatHistoryJob().main()
        db.session.commit()
    except Exception as e:
        logger.info(e)
        db.session.rollback()
    JobQueueLogService.finished(queue.id)
    db.session.commit()
    logger.info('end...')
    db.session.remove()


@celery.task
def fetch_account_history_job():
    # 遍历账户，获取每个账户的聊天记录
    db.session.remove()
    logger.info('start fetch_account_history_job...')
    job_name = 'fetch_account_history_job'
    flag, queue = JobQueueLogService.add(job_name)
    db.session.commit()
    if not flag:
        return
    accounts = TgAccount.query.filter_by(status=TgAccount.StatusType.JOIN_SUCCESS).all()
    try:
        for account in accounts:
            fetch_person_chat_history(account.id)
            db.session.commit()
    except Exception as e:
        logger.info(e)
    db.session.commit()
    JobQueueLogService.finished(queue.id)
    db.session.commit()
    db.session.remove()
    logger.info('end...')



if __name__ == '__main__':
    app.ready(db_switch=True, web_switch=False, worker_switch=True)
    # send_phone_code(24)
    # 验证码登录
    # login_tg_account(24)
    # 密码登录
    fetch_account_history_job()
