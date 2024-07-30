import json

from jCelery import celery
from jd import db, app
from jd.models.keyword_search import KeywordSearch
from jd.models.keyword_search_parse_result import KeywordSearchParseResult
from jd.services.spider.telegram_spider import TelegramSpider
from jd.tasks.first.tg import join_group
from utils.search_filter import find_accounts


def add_or_update_keyword_search_result(account, keyword, url, desc):
    # 首先查找是否存在相同的 account
    existing_record = KeywordSearchParseResult.query.filter_by(account=account,
                                                               is_delete=KeywordSearchParseResult.DeleteType.NORMAL).first()

    if not existing_record:
        # 如果不存在，创建新记录
        new_record = KeywordSearchParseResult(
            account=account,
            keyword=keyword,
            url=url,
            desc=desc,
            is_delete=0
        )
        db.session.add(new_record)


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
        accounts_dict = find_accounts(search_result.result.split("缺少字词")[0])
        if not accounts_dict:
            KeywordSearch.query.filter_by(id=search_result.id, status=KeywordSearch.StatusType.PROCESSING).update(
                {'status': KeywordSearch.StatusType.PROCESSED})
            db.session.commit()
            continue
        for account_type, account_list in accounts_dict.items():
            if account_type == 'telegram_number':
                for telegram_account in account_list:
                    # 用户
                    telegram_account = telegram_account.lower().replace('+', '')
                    telegram_account = telegram_account.split("tele")[0]
                    telegram_account = telegram_account.replace("@", "")
                    url = f'https://t.me/{telegram_account}'
                    data = spider.search_query(url)
                    if not data:
                        continue
                    if '@' in data['account']:
                        # 个人账户
                        desc = f'username:{data["username"]}, desc:{data["desc"]}'
                    elif 'subscribers' in data['account'] or 'members' in data['account'] or 'online' in data['account']:
                        desc = 'Telegram群组账户'
                        # 加入群组
                        join_group.delay(telegram_account)
                    else:
                        # desc = 'Telegram其他类型账户'
                        continue
                    add_or_update_keyword_search_result(account=telegram_account, keyword=search_result.keyword, url=url, desc=desc)
            elif account_type == 'qq_number':
                # qq群
                for qq_number in account_list:
                    desc = 'qq号'
                    url = f"{qq_number}"
                    # add_or_update_keyword_search_result(account=qq_number, keyword=search_result.keyword, url=url, desc=desc)
            else:
                phone_numbers = accounts_dict.get('phone_number', [])
                for phone_number in phone_numbers:
                    desc = "手机号"
                    url = f'{phone_number}'
                    add_or_update_keyword_search_result(account=phone_number, keyword=search_result.keyword, url=url,
                                                        desc=desc)
        KeywordSearch.query.filter_by(id=search_result.id, status=KeywordSearch.StatusType.PROCESSING).update(
            {'status': KeywordSearch.StatusType.PROCESSED})
        db.session.commit()

    return f'batch:{batch_id} parse search result end'


if __name__ == '__main__':
    app.ready(db_switch=True, web_switch=False, worker_switch=True)
    parse_search_result('17220885810201')
