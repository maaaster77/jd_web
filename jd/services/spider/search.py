from jd import db
from jd.models.black_keyword import BlackKeyword


class SpiderSearchService:

    @classmethod
    def baidu_search(cls, keyword_id_list):
        keyword_id_list = [int(k) for k in keyword_id_list.split(',')]
        keyword_list = db.session.query(BlackKeyword).filter(BlackKeyword.id.in_(keyword_id_list),
                                                             BlackKeyword.is_delete == BlackKeyword.DeleteType.NORMAL).all()
        black_keywords = [k.keyword.strip() for k in keyword_list]
        print('keywords:', black_keywords)
