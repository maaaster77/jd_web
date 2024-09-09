from jd import db


class TgGroupTag(db.Model):
    __tablename__ = 'tg_group_tag'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False, unique=False, default=0, comment='tg_group.id')
    tag_id = db.Column(db.Integer, nullable=False, unique=False, default=0, comment='tag.id')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

