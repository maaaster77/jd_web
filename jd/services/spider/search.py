import time

from jd import db
from jd.models.black_keyword import BlackKeyword
from jd.models.keyword_search import KeywordSearch
from jd.models.keyword_search_queue import KeywordSearchQueue
from jd.services.spider.baidu_spider import BaiduSpider
from jd.services.spider.google_spider import GoogleSpider
from jd.services.spider.tieba_spider import TiebaSpider


class SpiderSearchService:
    QUEUE_STATUS_MAP = {
        KeywordSearchQueue.StatusType.PENDING: '待处理',
        KeywordSearchQueue.StatusType.PROCESSING: '处理中',
        KeywordSearchQueue.StatusType.PROCESSED: '已处理'
    }

    SEARCH_ENGINE_MAP = {
        KeywordSearchQueue.SearchType.BAIDU: '百度',
        KeywordSearchQueue.SearchType.GOOGLE: '谷歌',
        KeywordSearchQueue.SearchType.TIEBA: '贴吧',
        KeywordSearchQueue.SearchType.TELEGRAM: 'TELEGRAM'
    }

    @classmethod
    def spider_engine(cls, search_type):
        if search_type == KeywordSearch.SearchType.BAIDU:
            return BaiduSpider()
        if search_type == KeywordSearch.SearchType.GOOGLE:
            return GoogleSpider()
        if search_type == KeywordSearch.SearchType.TIEBA:
            return TiebaSpider()

    @classmethod
    def add_search_to_db(cls, batch_id: str, search_type: int, keyword: str, result: str, page: int):
        obj = KeywordSearch(
            batch_id=batch_id,
            keyword=keyword,
            page=page,
            result=result,
            search_type=search_type,
        )
        db.session.add(obj)

    @classmethod
    def generate_batch_id(cls):
        return str(int(time.time() * 10000))
