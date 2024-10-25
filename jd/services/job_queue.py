import datetime
import logging

from jd import db
from jd.models.job_queue_log import JobQueueLog

logger = logging.getLogger(__name__)


class JobQueueLogService:

    @classmethod
    def add(cls, job_name):
        queue = JobQueueLog.query.filter_by(name=job_name).order_by(JobQueueLog.id.desc()).first()
        if not queue or queue.status == JobQueueLog.StatusType.FINISHED:
            queue = JobQueueLog(name=job_name, status=JobQueueLog.StatusType.RUNNING)
            db.session.add(queue)
            db.session.flush()
            return True, queue
        else:
            logger.info(f'{job_name} is running')
            if job_name == 'fetch_tg_history' \
                    and datetime.datetime.now().timestamp() - queue.created_at.timestamp() >= 3600:
                logger.info(f'{job_name} exception, skip')
                JobQueueLog.query.filter_by(id=queue.id, status=JobQueueLog.StatusType.RUNNING).update({
                    'status': JobQueueLog.StatusType.FINISHED
                })
                return False, None
        return False, None

    @classmethod
    def finished(cls, queue_id):
        JobQueueLog.query.filter_by(id=queue_id, status=JobQueueLog.StatusType.RUNNING).update({
            'status': JobQueueLog.StatusType.FINISHED
        })
