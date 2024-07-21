import time

from jd import db
from jd.models.black_keyword import BlackKeyword
from jd.models.keyword_search import KeywordSearch
from jd.services.spider.baidu_spider import BaiduSpider
from jd.services.spider.google_spider import GoogleSpider


class SpiderSearchService:

    @classmethod
    def spider_engine(cls, search_type):
        if search_type == KeywordSearch.SearchType.BAIDU:
            return BaiduSpider()
        if search_type == KeywordSearch.SearchType.GOOGLE:
            return GoogleSpider()

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
