from jd import db


class KeywordSearchParseResultTag(db.Model):
    __tablename__ = 'keyword_search_parse_result_tag'
    id = db.Column(db.Integer, primary_key=True)
    parse_id = db.Column(db.Integer, nullable=False, unique=False, default=0, comment='keyword_search_parse_result.id')
    tag_id = db.Column(db.Integer, nullable=False, unique=False, default=0, comment='tag.id')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

