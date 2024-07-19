from jCelery import celery
from jd.services.spider.search import SpiderSearchService


@celery.task
def spider_search_baidu(keyword_id_list: str):
    SpiderSearchService.baidu_search(keyword_id_list)

