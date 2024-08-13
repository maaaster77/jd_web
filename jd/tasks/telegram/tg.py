import asyncio
import logging
import os

from telethon import TelegramClient, errors

from jCelery import celery
from jd import app, db
from jd.models.tg_account import TgAccount
from jd.models.tg_group import TgGroup
from jd.models.tg_group_user_info import TgGroupUserInfo
from jd.services.spider.telegram_spider import TelegramSpider
from jd.services.spider.tg import TgService

logger = logging.getLogger(__name__)


@celery.task
def join_group(group_name, origin='celery'):
    print(f'{group_name} join...')
    tg = TgService.init_tg(origin)
    if not tg:
        logger.info(f'{group_name}, join_group error')
        return f'{group_name} join group fail'

    async def join():
        try:
            tg_group = TgGroup.query.filter(TgGroup.name == group_name).first()
            if not tg_group:
                return f'{group_name} join group fail, group not exist'
            result = await tg.join_conversation(group_name)
            chat_id = result.get('data', {}).get('id', 0)
            if result.get('result', 'Failed') == 'Failed':
                update_info = {
                    'status': TgGroup.StatusType.JOIN_FAIL
                }
            else:
                update_info = {
                    'status': TgGroup.StatusType.JOIN_SUCCESS,
                    'chat_id': chat_id
                }
            TgGroup.query.filter_by(name=group_name, status=TgGroup.StatusType.JOIN_ONGOING).update(update_info)
            db.session.commit()
        except Exception as e:
            logger.info('join_group error: {}'.format(e))
            db.session.rollback()

    with tg.client:
        tg.client.loop.run_until_complete(join())

    return f'{group_name} join group success'


@celery.task
def fetch_group_user_info(chat_id, user_id, nick_name, username, origin='celery'):
    """
    获取群组用户的信息
    :param origin:
    :param nick_name:
    :param chat_id:
    :param user_id:
    :param username:
    :return:
    """
    if not user_id or not nick_name:
        return
    user_id = str(user_id)
    group_user = TgGroupUserInfo.query.filter_by(user_id=user_id).first()
    if group_user:
        return
    if username:
        url = f'https://t.me/{username}'
        data = TelegramSpider().search_query(url)
        if not data:
            return
        obj = TgGroupUserInfo(chat_id=chat_id, user_id=user_id, nickname=nick_name,
                              username=username,
                              desc=data['desc'], photo=data['photo_url'])
        db.session.add(obj)
        db.session.flush()
        db.session.commit()
    else:
        tg = TgService.init_tg(origin)

        async def get_chat_room_user_info(nickname):
            nickname = nickname.split(' ')
            if len(nickname) > 1:
                nickname = nickname[0]
            user_info = await tg.get_chatroom_user_info(chat_id, nickname)
            for user in user_info:
                uid = str(user['user_id'])
                last_name = user["last_name"] if user["last_name"] else ''
                n_name = f'{user["first_name"]}{last_name}'
                g_user = TgGroupUserInfo.query.filter_by(user_id=uid).first()
                if g_user:
                    continue
                u = TgGroupUserInfo(chat_id=chat_id, user_id=uid, nickname=n_name,
                                    username=user['username'])
                db.session.add(u)
                db.session.flush()
            db.session.commit()

        with tg.client:
            tg.client.loop.run_until_complete(get_chat_room_user_info(nick_name))

    return f'群组:{chat_id}, fetch user:{nick_name} finished'


@celery.task
def fetch_group_recent_user_info(origin='celery'):
    tg = TgService.init_tg(origin)

    async def get_chat_room_user_info(chat_id, group_name):
        join_result = await tg.join_conversation(group_name)
        print(join_result)
        user_info = await tg.get_chatroom_all_user_info(chat_id)
        for user in user_info:
            user_id = str(user["user_id"])
            last_name = user["last_name"] if user["last_name"] else ''
            n_name = f'{user["first_name"]}{last_name}'
            username = user['username']
            if not username:
                obj = TgGroupUserInfo(chat_id=chat_id, user_id=user_id, nickname=n_name,
                                      username=username)
                db.session.add(obj)
                db.session.commit()
            else:
                fetch_group_user_info(chat_id, user_id, n_name, user['username'])

    tg_groups = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
    for group in tg_groups:
        with tg.client:
            tg.client.loop.run_until_complete(get_chat_room_user_info(int(group.chat_id), group.name))

    return f'fetch recent users finished'


@celery.task
def add_account(origin, username, phone, code=''):
    config_js = app.config['TG_CONFIG']
    session_dir = f'{app.static_folder}/utils/{username}'
    if not os.path.exists(session_dir):
        os.makedirs(session_dir, exist_ok=True)
    api_id = config_js.get("api_id")
    api_hash = config_js.get("api_hash")
    session_name = config_js.get(f"{origin}_session_name")
    session_name = f'{session_dir}/{session_name}'
    tg_account = TgAccount.query.filter(TgAccount.phone == phone).first()
    if not tg_account:
        return

    async def start_session(session_name):
        client = TelegramClient(session_name, api_id, api_hash)
        if not client.is_connected():
            await client.connect()
        if not code:
            res = None
            for i in range(3):
                res = await client.send_code_request(phone, force_sms=False)
            if res:
                TgAccount.query.filter(TgAccount.id == tg_account.id).update({
                    'phone_code_hash': res.phone_code_hash,
                })
        else:
            try:
                await client.sign_in(phone=phone, code=code, phone_code_hash=tg_account.phone_code_hash)
            except errors.SessionPasswordNeededError:
                if not tg_account.phone_code_hash:
                    print('phone_code_hash', tg_account.phone_code_hash)
                    return
                user = await client.sign_in(phone=phone, password=tg_account.password)
                print('user', user)
                if user:
                    TgAccount.query.filter(TgAccount.id == tg_account.id).update({
                        'status': TgAccount.StatusType.JOIN_SUCCESS,
                        'username': user.username,
                        'user_id': user.id,
                        'phone': user.phone,
                        'nickname': f'{user.first_name if user.first_name else ""} {user.last_name if user.last_name else ""}',
                        'phone_code_hash': ''
                    })
                else:
                    TgAccount.query.filter(TgAccount.id == tg_account.id).update({
                        'status': TgAccount.StatusType.JOIN_FAIL
                    })
            except Exception as e:
                logger.info('add_account error: {}'.format(e))

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_session(session_name))
        loop.close()
    except Exception as e:
        logger.info('add_account error: {}'.format(e))

    db.session.commit()
    return


if __name__ == '__main__':
    app.ready(db_switch=True, web_switch=False, worker_switch=True)
    add_account('celery', 'tt123', '+56990552148', code='94088')
