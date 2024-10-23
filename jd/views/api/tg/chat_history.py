import datetime
import logging
import os

from flask import render_template, request, make_response, send_file
import pandas as pd
from io import BytesIO

from openpyxl.drawing.image import Image
from sqlalchemy import func

from jd import app, db
from jd.models.tg_account import TgAccount
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.models.tg_group_user_info import TgGroupUserInfo
from jd.views import get_or_exception
from jd.views.api import api

logger = logging.getLogger(__name__)


@api.route('/tg/chat_room/history', methods=['GET'])
def tg_chat_room_history():
    args = request.args
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 100)
    search_content = get_or_exception('search_content', args, 'str', '')
    start_date = get_or_exception('start_date', args, 'str', '')
    end_date = get_or_exception('end_date', args, 'str', '')
    message_id = get_or_exception('message_id', args, 'int', 0)
    reply_to_msg_id = get_or_exception('reply_to_msg_id', args, 'int', 0)
    search_chat_id_list = args.getlist('search_group_id')
    search_user_id_list = args.getlist('search_user_id')
    search_account_id_list = args.getlist('search_account_id')

    rows, total_records = fetch_tg_group_chat_history(start_date, end_date, search_chat_id_list, search_user_id_list,
                                                      search_content, page, page_size, search_account_id_list,
                                                      message_id, reply_to_msg_id)
    total_pages = total_records // page_size
    chat_room = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
    group_list = [{'chat_id': c.chat_id, 'group_name': f'{c.name}-{c.title}'} for c in chat_room]
    chat_room = {r.chat_id: r.title for r in chat_room}
    data = []
    for r in rows:
        group_name = chat_room.get(r.chat_id, '')
        reply_to_msg_ids = [int(r) for r in r.reply_to_msg_ids.split(',') if int(r) > 0]
        print(f'chat_id:{r.chat_id}, paths:{r.document_paths}')
        data.append({
            'id': r.id,
            'group_name': group_name,
            'message': r.messages,
            'nickname': r.nickname,
            'postal_time': r.postal_time,
            'username': r.username,
            'user_id': r.user_id,
            'photo_paths': r.photo_paths.split(',') if r.photo_paths else [],
            'document_paths': r.document_paths.split(',') if r.document_paths else [],
            'reply_to_msg_id': reply_to_msg_ids[0] if reply_to_msg_ids else 0,
            'message_ids': r.message_ids,
            'chat_id': r.chat_id
        })
    tg_group_user_info = TgGroupUserInfo.query.filter(TgGroupUserInfo.username != '').all()
    unique_users = {}
    for t in tg_group_user_info:
        unique_users[t.username] = {
            'user_id': t.user_id,
            'chat_id': t.chat_id,
            'nickname': t.nickname,
            'desc': t.desc,
            'photo': t.photo,
            'username': f'{t.username}-{t.nickname}'
        }

    # Convert the dictionary values back into a list
    group_user_list = list(unique_users.values())

    tg_accounts = TgAccount.query.filter(TgAccount.status == TgAccount.StatusType.JOIN_SUCCESS).all()
    tg_accounts_list = [{'account_id': t.id, 'username': t.username} for t in tg_accounts]

    return render_template('chat_room_history.html', data=data, group_list=group_list, total_pages=total_pages,
                           current_page=page, page_size=page_size, group_user_list=group_user_list,
                           default_chat_id=search_chat_id_list,
                           default_user_id=search_user_id_list, default_search_content=search_content,
                           default_start_date=start_date,
                           default_search_account_id=search_account_id_list,
                           default_end_date=end_date, tg_accounts=tg_accounts_list, max=max, min=min)


def fetch_tg_group_chat_history(start_date, end_date, search_chat_id_list, search_user_id_list, search_content,
                                page=None,
                                page_size=None, search_account_id_list=None, message_id=0, reply_to_msg_id=0):
    # 需要修改sql_mode
    # set sql_mode ='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
    query = db.session.query(
        TgGroupChatHistory.id,
        TgGroupChatHistory.chat_id,
        TgGroupChatHistory.user_id,
        TgGroupChatHistory.username,
        TgGroupChatHistory.nickname,
        TgGroupChatHistory.postal_time,
        func.group_concat(TgGroupChatHistory.reply_to_msg_id).label('reply_to_msg_ids'),
        func.group_concat(TgGroupChatHistory.photo_path).label('photo_paths'),
        func.group_concat(TgGroupChatHistory.message).label('messages'),
        func.group_concat(TgGroupChatHistory.document_path).label('document_paths'),
        func.group_concat(TgGroupChatHistory.message_id).label('message_ids'),
    ).group_by(
        TgGroupChatHistory.chat_id,
        TgGroupChatHistory.user_id,
        TgGroupChatHistory.postal_time
    )

    if start_date and end_date:
        f_start_date = start_date + ' 00:00:00'
        f_end_date = end_date + ' 23:59:59'
        query = query.filter(TgGroupChatHistory.postal_time.between(f_start_date, f_end_date))
    search_chat_id_list = [r for r in search_chat_id_list if r]
    if search_chat_id_list:
        query = query.filter(TgGroupChatHistory.chat_id.in_(search_chat_id_list))
    search_user_id_list = [r for r in search_user_id_list if r]
    if search_user_id_list:
        query = query.filter(TgGroupChatHistory.user_id.in_(search_user_id_list))
    if search_content:
        query = query.filter(TgGroupChatHistory.message.like(f'%{search_content}%'))
    search_account_id_list = [r for r in search_account_id_list if r]
    if search_account_id_list:
        tg_accounts = TgAccount.query.filter(TgAccount.id.in_(search_account_id_list)).all()
        user_id_list = [t.user_id for t in tg_accounts]
        his = TgGroupChatHistory.query.filter(TgGroupChatHistory.user_id.in_(user_id_list)).all()
        chat_id_list = [t.chat_id for t in his]
        query = query.filter(TgGroupChatHistory.chat_id.in_(chat_id_list))
    if reply_to_msg_id:
        query = query.filter(TgGroupChatHistory.message_id == reply_to_msg_id)
    if message_id:
        message = query.filter(TgGroupChatHistory.id == message_id).first()
        if message:
            start_time = message.postal_time - datetime.timedelta(hours=1)
            end_time = message.postal_time + datetime.timedelta(minutes=5)
            query = query.filter(TgGroupChatHistory.chat_id == message.chat_id,
                                 TgGroupChatHistory.postal_time >= start_time,
                                 TgGroupChatHistory.postal_time <= end_time)

    total_records = query.count()
    if page and page_size:
        offset = (page - 1) * page_size
        rows = query.order_by(TgGroupChatHistory.id.desc()).offset(offset).limit(page_size).all()
    else:
        rows = query.order_by(TgGroupChatHistory.id.desc()).all()
    return rows, total_records


@api.route('/tg/chat_room/history/download', methods=['GET'])
def tg_chat_room_history_download():
    args = request.args
    search_content = get_or_exception('search_content', args, 'str', '')
    start_date = get_or_exception('start_date', args, 'str', '')
    end_date = get_or_exception('end_date', args, 'str', '')
    search_chat_id_list = args.getlist('search_group_id')
    search_user_id_list = args.getlist('search_user_id')
    search_account_id_list = args.getlist('search_account_id')

    rows, _ = fetch_tg_group_chat_history(start_date, end_date, search_chat_id_list, search_user_id_list,
                                          search_content, search_account_id_list=search_account_id_list)
    chat_room = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
    chat_room = {r.chat_id: r.title for r in chat_room}
    data = []
    for r in rows:
        group_name = chat_room.get(r.chat_id, '')
        data.append({
            '群组名称': group_name,
            # '内容': r.message,
            '昵称': r.nickname,
            '发布时间': r.postal_time.strftime('%Y-%m-%d %H:%M:%S'),
            '用户名': r.username,
            '用户ID': r.user_id,
            '图片': r.photo_paths,
            '内容': r.messages
        })

    # 创建DataFrame
    columns = ['群组名称', '昵称', '发布时间', '用户名', '用户ID', '内容', '图片']
    df = pd.DataFrame(data, columns=columns)

    # 将DataFrame保存到Excel文件
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')

    # 获取Excel工作簿
    workbook = writer.book

    # 加载图片到Excel
    ws = workbook['Sheet1']
    for idx, row in df.iterrows():
        logger.info(f"{row['群组名称']}, photo count:{len(row['图片'].split(','))}")
        if pd.isna(row['图片']):
            continue
        if not row['图片']:
            continue

        i = 0
        for i, img_path in enumerate(row['图片'].split(',')):
            if not img_path:
                continue
            img_path = os.path.join(app.static_folder, img_path)
            if not os.path.exists(img_path):
                continue
            try:
                img = Image(img_path)
            except Exception as e:
                logger.error(f'图片加载错误：{img_path}, error:{e}')
                continue
            # 调整图片大小
            img.width = 65
            img.height = 100
            # 将图片插入到对应的行
            cell = ws.cell(row=idx + 2, column=len(columns) + i)  # 假设图片放在最后一列
            cell.value = ''
            ws.add_image(img, cell.coordinate)
            ws.column_dimensions[chr(64 + len(columns) + i)].width = 65 / 6  # 适当调整比例
        ws.row_dimensions[idx + 2].height = 100  # 适当调整比例
    writer.close()

    # 设置响应头
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=chat_history.xlsx"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return response
