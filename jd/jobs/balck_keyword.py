import time

from jd import db
from jd.models.black_keyword import BlackKeyword
from jd.models.keyword_search_queue import KeywordSearchQueue
from jd.services.spider.search import SpiderSearchService
from jd.tasks.first.spider_search import deal_spider_search


class BlackKeywordSpiderJob:
    def main(self):
        keyword_list = db.session.query(BlackKeyword).filter(
            BlackKeyword.is_delete == BlackKeyword.DeleteType.NORMAL).all()

        for k in keyword_list:
            for search_type in [KeywordSearchQueue.SearchType.BAIDU, KeywordSearchQueue.SearchType.GOOGLE,
                                KeywordSearchQueue.SearchType.TIEBA]:
                batch_id = SpiderSearchService.generate_batch_id()
                obj = KeywordSearchQueue(batch_id=batch_id, keyword=k.keyword, search_type=search_type)
                db.session.add(obj)
                db.session.commit()
                deal_spider_search.delay(batch_id, search_type)
                time.sleep(300)


def run():
    job = BlackKeywordSpiderJob()
    while True:
        try:
            job.main()
            time.sleep(600)
        except Exception as ex:
            print(ex)
            return
