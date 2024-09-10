from jd import db


class TgGroup(db.Model):
    __tablename__ = 'tg_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, default='')
    chat_id = db.Column(db.String(128), nullable=False, default='', comment='群组id')
    status = db.Column(db.Integer, nullable=False, default=0, comment='0:未加入 1-加入成功 2-加入失败')
    desc = db.Column(db.String(1024), nullable=False, default='', comment='描述')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    account_id = db.Column(db.String(128), nullable=False, default='', comment='tg_account.user_id')

    class StatusType:
        NOT_JOIN = 0
        JOIN_SUCCESS = 1
        JOIN_FAIL = 2
        JOIN_ONGOING = 3
