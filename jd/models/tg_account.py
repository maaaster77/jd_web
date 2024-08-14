from jd import db


class TgAccount(db.Model):
    __tablename__ = 'tg_account'

    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.String(32), nullable=False, default='', comment='api_id')
    api_hash = db.Column(db.String(64), nullable=False, default='', comment='api_hash')
    name = db.Column(db.String(32), nullable=False, default='', comment='名称')
    phone = db.Column(db.String(32), nullable=False, default='', comment='手机号')
    phone_code_hash = db.Column(db.String(128), nullable=False, default='', comment='手机号hash')
    password = db.Column(db.String(32), nullable=False, default='', comment='密码')
    user_id = db.Column(db.String(128), nullable=False, default='', comment='用户id')
    username = db.Column(db.String(128), nullable=False, default='')
    nickname = db.Column(db.String(128), nullable=False, default='')
    code = db.Column(db.String(128), nullable=False, default='', comment='验证码')
    two_step = db.Column(db.Integer, nullable=False, default=0, comment='0:未开启 1-开启')
    status = db.Column(db.Integer, nullable=False, default=0, comment='0:未加入 1-加入成功 2-加入失败')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class StatusType:
        NOT_JOIN = 0
        JOIN_SUCCESS = 1
        JOIN_FAIL = 2
        JOIN_ONGOING = 3
