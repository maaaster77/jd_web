from jd import db
from jd.models.base import BaseModel


class TgGroup(BaseModel):
    __tablename__ = 'tg_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, default='')
    chat_id = db.Column(db.String(128), nullable=False, default='', comment='群组id')
    status = db.Column(db.Integer, nullable=False, default=0, comment='0:未加入 1-加入成功 2-加入失败')
    desc = db.Column(db.String(1024), nullable=False, default='', comment='描述')
    title = db.Column(db.String(1024), nullable=False, default='', comment='群组名称')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    account_id = db.Column(db.String(128), nullable=False, default='', comment='tg_account.user_id')
    avatar_path = db.Column(db.String(1024), nullable=False, default='', comment='头像本地地址')
    remark = db.Column(db.String(128), nullable=False, default='', comment='备注')
    group_type = db.Column(db.Integer, nullable=False, default=1, comment='1-群组 2-频道')


    class StatusType:
        NOT_JOIN = 0
        JOIN_SUCCESS = 1
        JOIN_FAIL = 2
        JOIN_ONGOING = 3

    class GroupType:
        GROUP = 1
        CHANNEL = 2
