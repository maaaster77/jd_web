import json

from jCelery import celery
from jd import app, db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_user_info import TgGroupUserInfo
from jd.services.spider.telegram_spider import TelegramSpider
from jd.services.spider.tg import TgService


@celery.task
def join_group(group_name):
    tg_group = TgGroup.query.filter(TgGroup.group_name == group_name).first()
    if tg_group:
        if tg_group.status == TgGroup.StatusType.JOIN_SUCCESS:
            return
    else:
        db.session.add(TgGroup(group_name=group_name))
        db.session.commit()
    tg = TgService.init_tg()

    async def join():
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
        TgGroup.query.filter_by(name=group_name, status=TgGroup.StatusType.NOT_JOIN).update(update_info)
        db.session.commit()

    with tg.client:
        tg.client.loop.run_until_complete(join())


@celery.task
def fetch_group_user_info(chat_id, user_id, nick_name, username):
    """
    获取群组用户的信息
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
        tg = TgService.init_tg()

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
def fetch_group_recent_user_info():
    tg = TgService.init_tg()

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
