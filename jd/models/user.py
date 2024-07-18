# 用户模型
from jd import db


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    status = db.Column(db.Integer, nullable=False, default=1, comment='0:无效,1:有效')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class StatusType:
        INVALID = 0  # 无效
        VALID = 1  # 有效
