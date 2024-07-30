import json

from jCelery import celery
from jd import app, db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_user_info import TgGroupUserInfo
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
    TgService.join_group(tg, group_name)
    db.session.commit()


@celery.task
def fetch_group_user_info(chat_id, user_id, nick_name):
    """
    获取群组用户的信息
    :param nick_name:
    :param chat_id:
    :param user_id:
    :return:
    """
    if not user_id or not nick_name:
        return
    group_user = TgGroupUserInfo.query.filter_by(chat_id=chat_id, user_id=user_id).first()
    if group_user:
        return
    tg = TgService.init_tg()
    user_info = tg.get_chatroom_user_info(chat_id, nick_name)
    detail = json.dumps(user_info, ensure_ascii=False)
    obj = TgGroupUserInfo(chat_id=chat_id, user_id=user_id, nickname=nick_name, detail=detail)
    db.session.add(obj)
    db.session.commit()
