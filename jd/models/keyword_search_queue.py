from jd import db


class KeywordSearchQueue(db.Model):
    __tablename__ = 'keyword_search_queue'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(126), nullable=False, unique=False, default='', comment='批次id')
    search_type = db.Column(db.Integer, nullable=False, default=1, comment='搜索类型 1-baidu 2-google')
    keyword = db.Column(db.String(126), nullable=False, unique=False, default='', comment='关键词')
    status = db.Column(db.Integer, nullable=False, default=0, comment='状态 0-待处理 1-处理中 2-已处理')
    page = db.Column(db.Integer, nullable=False, default=10, comment='页码')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class StatusType:
        PENDING = 0
        PROCESSING = 1
        PROCESSED = 2

    class SearchType:
        BAIDU = 1
        GOOGLE = 2
        TELEGRAM = 3
        TIEBA = 4


