from jd import db


class KeywordSearchParseResult(db.Model):
    __tablename__ = 'keyword_search_parse_result'
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(126), nullable=False, unique=False, default='', comment='关键词')
    url = db.Column(db.String(1024), nullable=False, unique=False, default='', comment='url')
    account = db.Column(db.String(1024), nullable=False, unique=False, default='', comment='账号')
    desc = db.Column(db.String(1024), nullable=False, unique=False, default='', comment='描述')
    is_delete = db.Column(db.Integer, nullable=False, default=0, comment='是否删除 1-已删除 0-正常')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class DeleteType:
        DELETE = 1
        NORMAL = 0
