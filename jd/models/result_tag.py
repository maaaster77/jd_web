from jd import db


class ResultTag(db.Model):
    __tablename__ = 'result_tag'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False, default='', comment='名称')
    status = db.Column(db.Integer, nullable=False, default=0, comment='0:有效,1:无效')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class StatusType:
        INVALID = 1  # 无效
        VALID = 0  # 有效
