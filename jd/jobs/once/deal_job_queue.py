import logging

from jd import db
from jd.models.job_queue_log import JobQueueLog

logger = logging.getLogger(__name__)


class DealJobQueueJob:

    def main(self):
        JobQueueLog.query.filter(JobQueueLog.status == JobQueueLog.StatusType.RUNNING).update({
            'status': JobQueueLog.StatusType.FINISHED,
        })
        db.session.commit()
        logger.info('deal job queue finished')


def run():
    job = DealJobQueueJob()
    job.main()
