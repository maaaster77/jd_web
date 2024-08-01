from flask import render_template, request

from jd import db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.models.tg_group_user_info import TgGroupUserInfo
from jd.views import get_or_exception
from jd.views.api import api


@api.route('/tg/chat_room/history', methods=['GET'])
def tg_chat_room_history():
    args = request.args
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 20)
    search_content = get_or_exception('search_content', args, 'str', '')
    search_chat_id_list = args.getlist('search_group_id')
    search_user_id_list = args.getlist('search_user_id')
    offset = (page - 1) * page_size

    query = TgGroupChatHistory.query
    if search_chat_id_list:
        query = query.filter(TgGroupChatHistory.chat_id.in_(search_chat_id_list))
    if search_user_id_list:
        query = query.filter(TgGroupChatHistory.user_id.in_(search_user_id_list))
    if search_content:
        query = query.filter(TgGroupChatHistory.message.like(f'%{search_content}%'))
    # 计算总记录数
    total_records = query.count()
    # 计算总页数
    total_pages = (total_records + page_size - 1) // page_size
    chat_room = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
    group_list = [{'chat_id': c.chat_id, 'group_name': c.name} for c in chat_room]
    chat_room = {r.chat_id: r.name for r in chat_room}
    rows = query.order_by(TgGroupChatHistory.id.desc()).offset(offset).limit(page_size).all()
    data = []
    for r in rows:
        group_name = chat_room.get(r.chat_id, '')
        data.append({
            'id': r.id,
            'group_name': group_name,
            'message': r.message,
            'nickname': r.nickname,
            'postal_time': r.postal_time,
            'username': r.username,
            'user_id': r.user_id,
            # 'photo_path': f'http://127.0.0.1:8000/{r.photo_path}'
            'photo_path': r.photo_path
        })
    tg_group_user_info = TgGroupUserInfo.query.all()
    group_user_list = [{
        'user_id': t.user_id,
        'chat_id': t.chat_id,
        'nickname': t.nickname,
        'desc': t.desc,
        'photo': t.photo,
        'username': t.username
    } for t in tg_group_user_info]


    return render_template('chat_room_history.html', data=data, group_list=group_list, total_pages=total_pages,
                           current_page=page, page_size=page_size, group_user_list=group_user_list, default_chat_id=search_chat_id_list,
                           default_user_id=search_user_id_list, default_search_content=search_content)
