from jCelery import celery
from jd import db
from jd.models.chemical_platform_product_info import ChemicalPlatformProductInfo
from jd.services.chemical import ChemicalPlatformService
from jd.services.spider.mobei_spider import MolbaseSpider


@celery.task
def deal_spider_chemical(platform_id):
    if platform_id == ChemicalPlatformService.PLATFORM_MOLBASE:
        m_spider = MolbaseSpider()
        for data in m_spider.search_query():
            print('data', data)
            obj = ChemicalPlatformProductInfo(platform_id=platform_id, product_name=data['product_name'],
                                              compound_name=data['compound_name'], seller_name=data['seller_name'],
                                              contact_number=data['contact_number'])
            db.session.add(obj)

    db.session.commit()
