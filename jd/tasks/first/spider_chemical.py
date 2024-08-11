from jCelery import celery
from jd import db, app
from jd.models.chemical_platform_product_info import ChemicalPlatformProductInfo
from jd.services.chemical import ChemicalPlatformService
from jd.services.spider.mobei_spider import MolbaseSpider


@celery.task
def deal_spider_chemical(platform_id):
    spider = ChemicalPlatformService.get_engine(platform_id)
    if not spider:
        return
    i = 0
    for data in spider.search_query(page=app.config['SPIDER_DEFAULT_PAGE']):
        print('data', data)
        # if ChemicalPlatformProductInfo.query.filter(
        #         ChemicalPlatformProductInfo.product_name == data['product_name'],
        #         platform_id == platform_id).first():
        #     continue
        if not data['contact_number']:
            continue
        obj = ChemicalPlatformProductInfo(platform_id=platform_id, product_name=data['product_name'],
                                          compound_name=data['compound_name'], seller_name=data['seller_name'],
                                          contact_number=data['contact_number'])
        db.session.add(obj)
        db.session.flush()
        i += 1
        if i % 20 == 0:
            db.session.commit()

    db.session.commit()
