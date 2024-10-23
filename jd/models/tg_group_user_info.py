from jd import db


class TgGroupUserInfo(db.Model):
    __tablename__ = 'tg_group_user_info'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(128), nullable=False, default='', comment='群组id')
    user_id = db.Column(db.String(128), nullable=False, default='', comment='用户id')
    username = db.Column(db.String(128), nullable=False, default='')
    nickname = db.Column(db.String(128), nullable=False, default='')
    desc = db.Column(db.String(1024), nullable=False, default='', comment='描述')
    photo = db.Column(db.String(1024), nullable=False, default='', comment='头像地址')
    avatar_path = db.Column(db.String(1024), nullable=False, default='', comment='头像本地地址')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    remark = db.Column(db.String(128), nullable=False, default='', comment='备注')


