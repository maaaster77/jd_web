from jCelery import celery
from jd import db
from jd.models.black_keyword import BlackKeyword
from jd.services.spider.search import SpiderSearchService


@celery.task
def spider_search_baidu(keyword_id_list: str, search_type: int = 1):
    keyword_id_list = [int(k) for k in keyword_id_list.split(',')]
    keyword_list = db.session.query(BlackKeyword).filter(BlackKeyword.id.in_(keyword_id_list),
                                                         BlackKeyword.is_delete == BlackKeyword.DeleteType.NORMAL).all()
    black_keywords = [k.keyword.strip() for k in keyword_list]
    spider = SpiderSearchService.spider_engine(search_type)
    for keyword in black_keywords:
        batch_id = SpiderSearchService.generate_batch_id()
        for data in spider.search_query(keyword, 10):
            for item in data:
                result = item['content']
                page = item['page']
                SpiderSearchService.add_search_to_db(batch_id, search_type, keyword, result, page)
            db.session.commit()
