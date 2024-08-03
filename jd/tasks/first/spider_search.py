import time

from jCelery import celery
from jd import db
from jd.models.black_keyword import BlackKeyword
from jd.models.keyword_search_queue import KeywordSearchQueue
from jd.services.spider.search import SpiderSearchService
from jd.tasks.first.parse_result import parse_search_result


@celery.task
def deal_spider_search(batch_id: str, search_type: int = 1):
    spider = SpiderSearchService.spider_engine(search_type)
    queue = KeywordSearchQueue.query.filter_by(batch_id=batch_id, status=KeywordSearchQueue.StatusType.PENDING).all()
    for q in queue:
        KeywordSearchQueue.query.filter_by(batch_id=batch_id, status=KeywordSearchQueue.StatusType.PENDING).update(
            {'status': KeywordSearchQueue.StatusType.PROCESSING})
        db.session.flush()
        # TODO: 爬虫注释，需要的时候打开
        for data in spider.search_query(q.keyword, q.page):
            for item in data:
                result = item['content']
                page = item['page']
                SpiderSearchService.add_search_to_db(batch_id, search_type, q.keyword, result, page)
            db.session.commit()
        # TODO:爬虫打开的时候注释掉
        # time.sleep(50)
        KeywordSearchQueue.query.filter_by(batch_id=batch_id, status=KeywordSearchQueue.StatusType.PROCESSING).update(
            {'status': KeywordSearchQueue.StatusType.PROCESSED})
        db.session.commit()
    parse_search_result.delay(batch_id)

    return f'batch:{batch_id} spider end'
