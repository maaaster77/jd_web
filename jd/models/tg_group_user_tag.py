from jd import db


class TgGroupUserTag(db.Model):
    __tablename__ = 'tg_user_tag'
    id = db.Column(db.Integer, primary_key=True)
    tg_user_id = db.Column(db.Integer, nullable=False, unique=False, default=0, comment='tg_group_user.id')
    tag_id = db.Column(db.Integer, nullable=False, unique=False, default=0, comment='tag.id')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

