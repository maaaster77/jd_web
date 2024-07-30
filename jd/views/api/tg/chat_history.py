from flask import render_template, request

from jd import db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.views import get_or_exception
from jd.views.api import api


@api.route('/tg/chat_room/history', methods=['GET'])
def tg_chat_room_history():
    args = request.args
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 20)
    offset = (page - 1) * page_size
    # 计算总记录数
    total_records = db.session.query(TgGroupChatHistory).count()
    # 计算总页数
    total_pages = (total_records + page_size - 1) // page_size
    chat_room = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
    chat_room = {r.id: r.name for r in chat_room}
    rows = db.session.query(TgGroupChatHistory).order_by(TgGroupChatHistory.id.desc()).offset(offset).limit(
        page_size).all()
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
            'user_id': r.user_id
        })

    return render_template('chat_room_history.html', data=data, total_pages=total_records, current_page=page)
