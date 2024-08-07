from jd import db


class ChemicalPlatform(db.Model):
    __tablename__ = 'chemical_platform'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(126), nullable=False, unique=False, default='', comment='名称')
    url = db.Column(db.String(255), nullable=False, unique=False, default='', comment='网址')
    status = db.Column(db.Integer, nullable=False, default=0, comment='状态 0-待处理 1-处理中 2-已处理')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())