from jd import db


class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, default=0, comment='用户id')
    role_id = db.Column(db.Integer, nullable=False, default=0, comment='角色id')
    status = db.Column(db.Integer, nullable=False, default=0, comment='0:无效,1:有效')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class StatusType:
        INVALID = 0  # 无效
        VALID = 1  # 有效
