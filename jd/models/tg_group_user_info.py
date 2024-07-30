from jd import db


class TgGroupUserInfo(db.Model):
    __tablename__ = 'tg_group_user_info'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False, default=0, comment='群组id')
    user_id = db.Column(db.Integer, nullable=False, default=0, comment='用户id')
    username = db.Column(db.String(128), nullable=False, default='')
    nickname = db.Column(db.String(128), nullable=False, default='')
    detail = db.Column(db.Text, nullable=False, comment='详细信息')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

