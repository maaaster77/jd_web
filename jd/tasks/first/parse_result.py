import json

from jCelery import celery
from jd import db, app
from jd.models.keyword_search import KeywordSearch
from jd.models.keyword_search_parse_result import KeywordSearchParseResult
from jd.services.spider.telegram_spider import TelegramSpider
from utils.search_filter import find_accounts


@celery.task
def parse_search_result(batch_id: str):
    search_result_list = KeywordSearch.query.filter_by(batch_id=batch_id,
                                                       status=KeywordSearch.StatusType.PENDING).all()
    spider = TelegramSpider()

    for search_result in search_result_list:
        if KeywordSearch.query.filter_by(id=search_result.id, status=KeywordSearch.StatusType.PENDING).update(
                {'status': KeywordSearch.StatusType.PROCESSING}) > 0:
            db.session.flush()
        else:
            db.session.rollback()
            continue
        accounts_dict = find_accounts(search_result.result)
        if not accounts_dict:
            KeywordSearch.query.filter_by(id=search_result.id, status=KeywordSearch.StatusType.PROCESSING).update(
                {'status': KeywordSearch.StatusType.PROCESSED})
            db.session.commit()
            continue
        for account_type, account_list in accounts_dict.items():
            if account_type == 'telegram_number':
                for telegram_account in account_list:
                    # 用户
                    data = spider.search_query(f'https://t.me/{telegram_account.replace("@", "")}')
                    if not data:
                        continue
                    if '@' in data['account']:
                        # 个人账户
                        desc = f'account:{telegram_account}, username:{data["username"]}, desc:{data["desc"]}'
                    elif 'subscribers' in data['account']:
                        desc = 'Telegram群组账户'
                    else:
                        desc = 'Telegram其他类型账户'
                    obj = KeywordSearchParseResult(account=telegram_account, desc=desc,
                                                   keyword=search_result.keyword, url='')
                    db.session.add(obj)
            elif account_type == 'qq_number':
                # qq群
                for qq_number in account_list:
                    obj = KeywordSearchParseResult(account=qq_number, desc='qq号',
                                                   keyword=search_result.keyword, url='')
                    db.session.add(obj)
            else:
                phone_numbers = accounts_dict.get('phone_number', [])
                for phone_number in phone_numbers:
                    obj = KeywordSearchParseResult(account=phone_number, desc='手机号',
                                                   keyword=search_result.keyword, url='')
                    db.session.add(obj)
        KeywordSearch.query.filter_by(id=search_result.id, status=KeywordSearch.StatusType.PROCESSING).update(
            {'status': KeywordSearch.StatusType.PROCESSED})
        db.session.commit()

    return f'batch:{batch_id} parse search result end'


if __name__ == '__main__':
    app.ready(db_switch=True, web_switch=False, worker_switch=True)
    parse_search_result('17220885810201')
