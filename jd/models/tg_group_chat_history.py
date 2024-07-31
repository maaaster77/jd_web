from jd import db


class TgGroupChatHistory(db.Model):
    __tablename__ = 'tg_group_chat_history'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(128), nullable=False, default='', comment='群组id')
    message_id = db.Column(db.String(128), nullable=False, default='', comment='消息id')
    user_id = db.Column(db.String(128), nullable=False, default='', comment='用户id')
    username = db.Column(db.String(128), nullable=False, default='')
    nickname = db.Column(db.String(128), nullable=False, default='')
    postal_time = db.Column(db.DateTime, nullable=False, default='1970-10-30 00:00:00')
    reply_to_msg_id = db.Column(db.String(128), nullable=False, default='', comment='回复的消息id')
    message = db.Column(db.Text, nullable=False, comment='消息')
    photo_path = db.Column(db.String(256), nullable=False, default='', comment='图片路径')
    status = db.Column(db.Integer, nullable=False, default=0, comment='')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
