from jd import db


class JobQueueLog(db.Model):
    __tablename__ = 'job_queue_log'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(126), nullable=False, unique=False, default='', comment='job name')
    status = db.Column(db.Integer, nullable=False, default=0, comment='状态 0-待处理 1-处理中 2-已处理')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class StatusType:
        NOT_START = 0
        RUNNING = 1
        FINISHED = 2
