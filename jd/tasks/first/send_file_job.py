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
def send_file_job():
    """
    tg_group tg_group_chat_history tg_group_use_info

    :return:
    """
    logger.info('ftp send file job start...')
    db.session.remove()
    file_list = []
    # model_list = [TgGroup, TgGroupChatHistory, TgGroupUserInfo]
    model_list = [TgGroupChatHistory]
    for model in model_list:
        add_list, update_list = deal_data(model)
        file_list.extend(add_list)
        file_list.extend(update_list)
    FtpService.send_file_by_file_path(file_list)
    db.session.remove()
    logger.info('ftp send file job end...')


def deal_data(model: Type[TgGroup, TgGroupChatHistory, TgGroupUserInfo]):
    last_id = 0
    file_list = []
    update_file_list = []
    now_time = datetime.datetime.now()
    if now_time.strftime('%Y%m%d') == '20241101':
        # 这一天不处理，等待2号开始处理
        return [], []
    yesterday = now_time - datetime.timedelta(days=1)
    start_time = yesterday.strftime('%Y-%m-%d 00:00:00')
    end_time = yesterday.strftime('%Y-%m-%d 23:59:59')
    while True:
        query = model.query.filter(model.id > last_id)
        if now_time > datetime.datetime(2024, 10, 31, 23, 59, 59):
            # 1号开始，处理昨天的数据
            query = query.filter(model.created_at.between(start_time, end_time))
        rows = query.order_by(model.id.asc()).limit(1000).all()
        if not rows:
            break
        last_id = rows[-1].id
        # 生成文件
        file_path, else_file_path_list = FtpService.save_local_file_from_db(rows, model.__tablename__, 'new', True)
        if file_path:
            file_list.append(file_path)
        file_list.extend(else_file_path_list)
    # 更新的数据
    rows = model.query.filter(model.created_at != model.updated_at,
                              model.updated_at.between(start_time, end_time)).order_by(model.updated_at.asc()).limit(
        1000).all()
    update_file_path, _ = FtpService.save_local_file_from_db(rows, model.__tablename__, 'update')
    if update_file_path:
        update_file_list.append(update_file_path)
    return file_list, update_file_list


if __name__ == '__main__':
    app.ready(db_switch=True, web_switch=False, worker_switch=True)
    send_file_job()
