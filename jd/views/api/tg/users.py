from flask import render_template, request

from jd import db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.models.tg_group_user_info import TgGroupUserInfo
from jd.views import get_or_exception
from jd.views.api import api


@api.route('/tg/group_user/list', methods=['GET'])
def tg_group_user_list():
    args = request.args
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 20)
    search_group_id = get_or_exception('search_group_id', args, 'str', '')
    search_username = get_or_exception('search_username', args, 'str', '')
    offset = (page - 1) * page_size
    query = TgGroupUserInfo.query
    if search_group_id:
        query = query.filter_by(chat_id=search_group_id)
    if search_username:
        query = query.filter(TgGroupUserInfo.username.like(f'%{search_username}%'))
    total_records = query.count()
    group_user_list = query.order_by(TgGroupUserInfo.id.desc()).offset(offset).limit(page_size).all()
    chat_room = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
    group_list = [{'chat_id': c.chat_id, 'group_name': c.name} for c in chat_room]
    chat_room = {r.chat_id: r.name for r in chat_room}
    data = [{
        'user_id': group_user.user_id,
        'chat_id': group_user.chat_id,
        'nickname': group_user.nickname,
        'username': group_user.username,
        'photo': group_user.photo,
        'desc': group_user.desc,
        'group_name': chat_room.get(group_user.chat_id, '')
    } for group_user in group_user_list]

    total_pages = (total_records + page_size - 1) // page_size

    return render_template('tg_group_user.html', data=data, group_list=group_list, total_pages=total_pages,
                           current_page=page, page_size=page_size, default_search_group_id=search_group_id, default_search_username=search_username)
