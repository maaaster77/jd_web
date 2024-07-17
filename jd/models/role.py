from jd import db


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, default='')
    detail = db.Column(db.String(50), nullable=False, default='')
    status = db.Column(db.Integer, nullable=False, default=0, comment='0:无效,1:有效')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class StatusType:
        INVALID = 0  # 无效
        VALID = 1  # 有效
