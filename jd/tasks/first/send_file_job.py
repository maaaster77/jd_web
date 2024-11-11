from __future__ import annotations

import datetime
import json
import logging
import os
from typing import Type

from jCelery import celery
from jd import app, db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.models.tg_group_user_info import TgGroupUserInfo
from jd.services.ftp import FtpService

logger = logging.getLogger(__name__)


@celery.task
def send_file_job(data_type=0, is_all=0, start_id=0, max_id=0):
    """
    tg_group tg_group_chat_history tg_group_use_info

    :return:
    """
    logger.info('ftp send file job start...')
    db.session.remove()
    if data_type == 1:
        model_list = [TgGroup]
    elif data_type == 2:
        model_list = [TgGroupChatHistory]
    elif data_type == 3:
        model_list = [TgGroupUserInfo]
    else:
        model_list = [TgGroup, TgGroupChatHistory, TgGroupUserInfo]
    for model in model_list:
        deal_data(model, is_all, start_id, max_id)
    db.session.remove()
    logger.info('ftp send file job end...')


def deal_data(model: Type[TgGroup, TgGroupChatHistory, TgGroupUserInfo], is_all, start_id, max_id):
    last_id = start_id
    now_time = datetime.datetime.now()
    yesterday = now_time - datetime.timedelta(days=1)
    if yesterday.strftime('%Y-%m-%d') == '2024-11-10':
        return
    start_time = yesterday.strftime('%Y-%m-%d 00:00:00')
    end_time = yesterday.strftime('%Y-%m-%d 23:59:59')
    if not max_id:
        max_id = model.query.order_by(model.id.desc()).first().id
    while True:
        query = model.query.filter(model.id > last_id)
        if not is_all:
            # 不处理全部的，只处理昨天的数据
            query = query.filter(model.created_at.between(start_time, end_time))
        else:
            query = query.filter(model.id <= max_id)
        rows = query.order_by(model.id.asc()).limit(1000).all()
        if not rows:
            break
        last_id = rows[-1].id
        # 生成文件
        print(f'deal data:{rows[0].id}-{last_id}')
        logger.info(f'deal data:{rows[0].id}-{last_id}')
        file_path, else_file_path_list = FtpService.save_local_file_from_db(rows, model.__tablename__, 'new', True)
        else_file_path_list.append(file_path)
        FtpService.send_file_by_file_path(else_file_path_list)
    if is_all:
        return
    # 更新的数据
    rows = model.query.filter(model.created_at != model.updated_at,
                              model.updated_at.between(start_time, end_time)).order_by(model.updated_at.asc()).limit(
        1000).all()
    update_file_path, _ = FtpService.save_local_file_from_db(rows, model.__tablename__, 'update')
    if update_file_path:
        FtpService.send_file_by_file_path([update_file_path])


if __name__ == '__main__':
    app.ready(db_switch=True, web_switch=False, worker_switch=True)
    send_file_job(is_all=1)
