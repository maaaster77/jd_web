import asyncio
import datetime
import logging
import os
import time

import requests
from telethon import TelegramClient, errors

from jCelery import celery
from jd import app, db
from jd.models.tg_account import TgAccount
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.models.tg_group_user_info import TgGroupUserInfo
from jd.services.spider.telegram_spider import TelegramSpider, TelegramAPIs
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
                channel_full = await tg.get_full_channel(chat_id)
                logger.info(f'{group_name} group info:{channel_full}')
                update_info = {
                    'status': TgGroup.StatusType.JOIN_SUCCESS,
                    'chat_id': chat_id,
                    'desc': channel_full.get("channel_description", ''),
                    'avatar_path': channel_full.get('photo_path', ''),
                    'title': channel_full.get("title", ''),
                    'group_type': TgGroup.GroupType.CHANNEL if channel_full.get('megagroup',
                                                                                '') == 'channel' else TgGroup.GroupType.GROUP,
                }
            tg_group = TgGroup.query.filter(TgGroup.chat_id == chat_id).first()
            if tg_group:
                # 更新原来的群组信息
                TgGroup.query.filter(TgGroup.chat_id == chat_id).update(update_info)
                # 删除新增的群组
                TgGroup.query.filter_by(name=group_name).delete()
            else:
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
        photo_url = data['photo_url']
        file_path = ''
        if photo_url:
            # 下载图片
            file_path = TgService.download_photo(photo_url, user_id)

        obj = TgGroupUserInfo(chat_id=chat_id, user_id=user_id, nickname=nick_name,
                              username=username,
                              desc=data['desc'], photo=data['photo_url'], avatar_path=file_path)
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
def fetch_person_chat_history(account_id, origin='celery'):
    tg_account = TgAccount.query.filter(TgAccount.id == account_id).first()
    if not tg_account:
        return

    tg = TelegramAPIs()
    session_dir = f'{app.static_folder}/utils'
    session_name = f'{session_dir}/{tg_account.name}/jd_{origin}.session'
    if not os.path.exists(session_name):
        logger.info(f'session {session_name} does not exist')
    try:
        tg.init_client(
            session_name=session_name, api_id=tg_account.api_id, api_hash=tg_account.api_hash
        )
    except Exception as e:
        logger.info(f'init_client error: {e}')
        return

    group_id_list = []

    async def get_person_dialog_list():
        async for chat_info in tg.get_dialog_list():
            temp_data = chat_info.get('data', {})
            _chat_id = temp_data.get('id', 0)
            if not _chat_id:
                logger.info(f'account, {account_id}, chat_id is empty, data:{temp_data}')
                continue

            group_id_list.append(_chat_id)

    async def get_chat_history_list(chat_id):
        param = {
            "limit": 60,
            # "offset_date": datetime.datetime.now() - datetime.timedelta(hours=8) - datetime.timedelta(minutes=20),
            "last_message_id": -1,
        }
        logger.info(f'account:{account_id}, 开始获取群组：{chat_id}，记录')

        try:
            chat = await tg.get_dialog(chat_id)
        except Exception as e:
            logger.info(f'chat_id:{chat_id}, 未获取到群组...{e}')
            return
        history_list = []
        async for data in tg.scan_message(chat, **param):
            history_list.append(data)
        history_list.reverse()
        message_id_list = [str(data.get("message_id", 0)) for data in history_list if data.get("message_id", 0)]
        msg = TgGroupChatHistory.query.filter(TgGroupChatHistory.message_id.in_(message_id_list),
                                              TgGroupChatHistory.chat_id == str(chat_id)).all()
        already_message_id_list = [data.message_id for data in msg]
        for data in history_list:
            user_id = data.get("user_id", 0)
            if user_id == 777000:
                # 客服
                continue
            message_id = str(data.get("message_id", 0))
            if message_id in already_message_id_list:
                continue
            logger.info(f'fetch_person_chat_history data:{data}')
            user_id = str(user_id)
            nickname = data.get("nick_name", "")

            obj = TgGroupChatHistory(
                chat_id=str(chat_id),
                message_id=message_id,
                nickname=nickname,
                username=data.get("user_name", ""),
                user_id=user_id,
                postal_time=data.get("postal_time", datetime.datetime.now()) + datetime.timedelta(hours=8),
                message=data.get("message", ""),
                reply_to_msg_id=str(data.get("reply_to_msg_id", 0)),
                photo_path=data.get("photo", {}).get('file_path', ''),
                document_path=data.get("document", {}).get('file_path', ''),
                document_ext=data.get("document", {}).get('ext', ''),
            )
            db.session.add(obj)
        db.session.commit()

    with tg.client:
        tg.client.loop.run_until_complete(get_person_dialog_list())

    for chat_id in group_id_list:
        with tg.client:
            tg.client.loop.run_until_complete(get_chat_history_list(chat_id))
    tg.close_client()


@celery.task
def fetch_account_channel(account_id, origin='celery'):
    tg_account = TgAccount.query.filter(TgAccount.id == account_id).first()
    if not tg_account:
        return

    tg = TelegramAPIs()
    session_dir = f'{app.static_folder}/utils'
    session_name = f'{session_dir}/{tg_account.name}/jd_{origin}.session'
    tg.init_client(
        session_name=session_name, api_id=tg_account.api_id, api_hash=tg_account.api_hash
    )

    async def get_channel():
        async for result in tg.get_dialog_list():
            data = result.get('data', {})
            print(data)
            chat_id = str(data.get('id', ''))
            if not chat_id:
                continue
            tg_group = TgGroup.query.filter(TgGroup.chat_id == chat_id).first()
            if tg_group:
                TgGroup.query.filter(TgGroup.chat_id == chat_id).update({
                    'account_id': tg_account.user_id,
                    'desc': data.get('channel_description', ''),
                    'avatar_path': data.get('photo_path', ''),
                    'chat_id': chat_id,
                    'title': data.get("title", ''),
                    'group_type': TgGroup.GroupType.CHANNEL if data.get('megagroup',
                                                                        '') == 'channel' else TgGroup.GroupType.GROUP,
                })
            else:
                obj = TgGroup(
                    account_id=tg_account.user_id,
                    chat_id=chat_id,
                    name=data.get('username', ''),
                    desc=data.get('channel_description', ''),
                    status=TgGroup.StatusType.JOIN_SUCCESS,
                    avatar_path=data.get('photo_path', ''),
                    title=data.get("title", ''),
                    group_type=TgGroup.GroupType.CHANNEL if data.get('megagroup',
                                                                     '') == 'channel' else TgGroup.GroupType.GROUP,
                )
                db.session.add(obj)
            db.session.commit()

    with tg.client:
        tg.client.loop.run_until_complete(get_channel())


@celery.task
def send_phone_code(account_id, origin='celery'):
    tg_account = TgAccount.query.filter(TgAccount.id == account_id).first()
    if not tg_account:
        return
    session_name = get_session_name(tg_account.name, origin)
    api_id = tg_account.api_id
    api_hash = tg_account.api_hash
    phone = tg_account.phone
    if not api_id or not api_hash or not phone:
        return

    async def send_code():
        if not client.is_connected():
            await client.connect()
        for i in range(5):
            try:
                res = await client.send_code_request(phone, force_sms=False)
                if res:
                    TgAccount.query.filter(TgAccount.id == tg_account.id).update({
                        'phone_code_hash': res.phone_code_hash,
                    })
                    db.session.commit()
                    break
            except Exception as e:
                logger.info('send_code_request error: {}'.format(e))
            time.sleep(1)
        if client.is_connected():
            client.disconnect()

    client = TelegramClient(session_name, api_id, api_hash)

    for i in range(3):
        try:
            client.loop.run_until_complete(send_code())
            break
        except Exception as e:
            logger.info('send_code_request error: {}'.format(e))
            time.sleep(1)
    db.session.commit()
    return


@celery.task
def login_tg_account(account_id, origin='celery'):
    tg_account = TgAccount.query.filter(TgAccount.id == account_id).first()
    if not tg_account:
        return
    session_name = get_session_name(tg_account.name, origin)
    api_id = tg_account.api_id
    api_hash = tg_account.api_hash
    phone = tg_account.phone
    code = tg_account.code
    if not api_id or not api_hash or not phone or not code:
        return

    async def start_login():
        if not client.is_connected():
            await client.connect()
        user = None
        try:
            if tg_account.two_step:
                user = await client.sign_in(phone=phone, password=tg_account.password)
            else:
                user = await client.sign_in(phone=phone, code=code, phone_code_hash=tg_account.phone_code_hash)
        except errors.SessionPasswordNeededError:
            TgAccount.query.filter(TgAccount.id == tg_account.id).update({'two_step': 1})
            db.session.commit()
            if client.is_connected():
                client.disconnect()
            return
        except Exception as e:
            logger.info('add_account error: {}'.format(e))
            if client.is_connected():
                client.disconnect()
            return
        print('user', user)
        if user:
            TgAccount.query.filter(TgAccount.id == tg_account.id).update({
                'status': TgAccount.StatusType.JOIN_SUCCESS,
                'username': user.username if user.username else '',
                'user_id': user.id,
                'nickname': f'{user.first_name if user.first_name else ""} {user.last_name if user.last_name else ""}',
                'phone_code_hash': '',
                'code': '',
                'api_code': '',
                'two_step': 0,
            })
        else:
            TgAccount.query.filter(TgAccount.id == tg_account.id).update({
                'status': TgAccount.StatusType.JOIN_FAIL,
                'phone_code_hash': '',
                'code': '',
                'api_code': '',
                'two_step': 0,
            })

        if client.is_connected():
            client.disconnect()

    client = TelegramClient(session_name, api_id, api_hash)

    for i in range(3):
        try:
            client.loop.run_until_complete(start_login())
            break
        except Exception as e:
            print('login error:', e)
            time.sleep(1)

    db.session.commit()
    return


def get_session_name(name, origin):
    session_dir = f'{app.static_folder}/utils'
    session_dir = f'{session_dir}/{name}'
    os.makedirs(session_dir, exist_ok=True)
    session_name = f'{session_dir}/jd_{origin}.session'
    return session_name


if __name__ == '__main__':
    app.ready(db_switch=True, web_switch=False, worker_switch=True)
    # send_phone_code(24)
    # 验证码登录
    # login_tg_account(24)
    # 密码登录
    login_tg_account(24)
