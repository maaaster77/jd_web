import datetime
import logging
import time

from jCelery import celery
from jd import db, app
from jd.models.chemical_platform_product_info import ChemicalPlatformProductInfo
from jd.services.chemical import ChemicalPlatformService
from jd.services.spider.mobei_spider import MolbaseSpider

logger = logging.getLogger(__name__)


@celery.task
def deal_spider_chemical(platform_id):
    spider = ChemicalPlatformService.get_engine(platform_id)
    if not spider:
        return
    i = 0
    for data in spider.search_query(page=app.config['SPIDER_DEFAULT_PAGE']):
        print('id', platform_id)
        print('data', data)
        # if ChemicalPlatformProductInfo.query.filter(
        #         ChemicalPlatformProductInfo.product_name == data['product_name'],
        #         platform_id == platform_id).first():
        #     continue
        if not data['contact_number']:
            continue
        obj = ChemicalPlatformProductInfo(platform_id=platform_id, product_name=data['product_name'],
                                          compound_name=data['compound_name'], seller_name=data['seller_name'],
                                          contact_number=data['contact_number'], qq_number=data.get('qq_number', ''))
        db.session.add(obj)
        db.session.flush()
        i += 1
        if i % 20 == 0:
            db.session.commit()

    db.session.commit()


@celery.task
def chemical_data_get_job():
    for platform_id, platform in ChemicalPlatformService.PLATFORM_MAP.items():
        print(f'抓取:{platform}平台信息...')
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.info(f'{now_time}, 抓取:{platform}平台信息...')
        deal_spider_chemical.delay(platform_id)
        time.sleep(600)
