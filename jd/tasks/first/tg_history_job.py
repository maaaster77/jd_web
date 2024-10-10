import datetime
import logging

from jCelery import celery
from jd import db
from jd.jobs.chat_history import TgChatHistoryJob
from jd.models.job_queue_log import JobQueueLog

logger = logging.getLogger(__name__)


@celery.task
def fetch_tg_history_job():
    logger.info('start fetch_tg_history_job...')
    job_name = 'fetch_tg_history'
    queue = JobQueueLog.query.filter_by(job_name=job_name).order_by(JobQueueLog.id.desc()).first()
    if not queue or queue.status == JobQueueLog.StatusType.FINISHED:
        queue = JobQueueLog(job_name=job_name, status=JobQueueLog.StatusType.RUNNING)
        db.session.add(queue)
        db.session.commit()
    else:
        return
    TgChatHistoryJob().main()
    db.session.commit()
    JobQueueLog.query.filter_by(id=queue.id, status=JobQueueLog.StatusType.RUNNING).update({
        'status': JobQueueLog.StatusType.FINISHED
    })
    db.session.commit()
    logger.info('end...')

