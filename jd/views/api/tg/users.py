import collections
from io import BytesIO

import pandas as pd
from flask import render_template, request, make_response

from jd import db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.models.tg_group_user_info import TgGroupUserInfo
from jd.models.tg_group_user_tag import TgGroupUserTag
from jd.services.tag import TagService
from jd.views import get_or_exception, success
from jd.views.api import api


@api.route('/tg/group_user/list', methods=['GET'])
def tg_group_user_list():
    args = request.args
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 20)
    search_nickname = get_or_exception('search_nickname', args, 'str', '')
    search_desc = get_or_exception('search_desc', args, 'str', '')
    search_group_id = get_or_exception('search_group_id', args, 'str', '')
    search_username = get_or_exception('search_username', args, 'str', '')
    offset = (page - 1) * page_size
    query = TgGroupUserInfo.query
    if search_group_id:
        query = query.filter_by(chat_id=search_group_id)
    if search_username:
        query = query.filter(TgGroupUserInfo.username.like(f'%{search_username}%'))
    if search_nickname:
        query = query.filter(TgGroupUserInfo.nickname.like(f'%{search_nickname}%'))
    if search_desc:
        query = query.filter(TgGroupUserInfo.desc.like(f'%{search_desc}%'))
    total_records = query.count()
    tag_list = TagService.list()
    group_user_list = query.order_by(TgGroupUserInfo.id.desc()).offset(offset).limit(page_size).all()
    chat_room = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
    group_list = [{'chat_id': c.chat_id, 'group_name': c.name} for c in chat_room]
    chat_room = {r.chat_id: r.name for r in chat_room}
    group_user_id_list = [group_user.id for group_user in group_user_list]
    parse_tag_list = TgGroupUserTag.query.filter(TgGroupUserTag.tg_user_id.in_(group_user_id_list)).all()
    parse_tag_result = collections.defaultdict(list)
    for p in parse_tag_list:
        parse_tag_result[p.tg_user_id].append(str(p.tag_id))
    tag_dict = {t['id']: t['name'] for t in tag_list}
    data = []
    for group_user in group_user_list:
        parse_tag = parse_tag_result.get(group_user.id, [])
        tag_text = ','.join([tag_dict.get(int(t), '') for t in parse_tag if tag_dict.get(int(t), '')])
        data.append({
            'id': group_user.id,
            'user_id': group_user.user_id,
            'chat_id': group_user.chat_id,
            'nickname': group_user.nickname,
            'username': group_user.username,
            'photo': group_user.avatar_path,
            'desc': group_user.desc,
            'tag': tag_text,
            'tag_id_list': ','.join(parse_tag) if parse_tag else '',
            'group_name': chat_room.get(group_user.chat_id, '')
        })

    total_pages = (total_records + page_size - 1) // page_size

    return render_template('tg_group_user.html', data=data, group_list=group_list, total_pages=total_pages,
                           current_page=page, page_size=page_size, default_search_group_id=search_group_id,
                           default_search_username=search_username, tag_list=tag_list,
                           default_search_nickname=search_nickname, default_search_desc=search_desc)


@api.route('/tg/group_user/download', methods=['GET'])
def tg_group_user_download():
    args = request.args
    search_nickname = get_or_exception('search_nickname', args, 'str', '')
    search_desc = get_or_exception('search_desc', args, 'str', '')
    search_group_id = get_or_exception('search_group_id', args, 'str', '')
    search_username = get_or_exception('search_username', args, 'str', '')
    query = TgGroupUserInfo.query
    if search_group_id:
        query = query.filter_by(chat_id=search_group_id)
    if search_username:
        query = query.filter(TgGroupUserInfo.username.like(f'%{search_username}%'))
    if search_nickname:
        query = query.filter(TgGroupUserInfo.nickname.like(f'%{search_nickname}%'))
    if search_desc:
        query = query.filter(TgGroupUserInfo.desc.like(f'%{search_desc}%'))
    group_user_list = query.order_by(TgGroupUserInfo.id.desc()).all()
    chat_room = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
    chat_room = {r.chat_id: r.name for r in chat_room}
    unique_user = {}
    group_user = {group_user.user_id: {
        '群组': chat_room.get(group_user.chat_id, ''),
        '用户ID': group_user.user_id,
        '用户昵称': group_user.nickname,
        '用户名': group_user.username,
        '个人简介': group_user.desc,
    } for group_user in group_user_list}
    data = list(group_user.values())

    # 创建DataFrame
    columns = ['群组', '用户ID', '用户昵称', '用户名', '个人简介']
    df = pd.DataFrame(data, columns=columns)

    # 将DataFrame保存到Excel文件
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')

    # 设置响应头
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=users.csv"
    response.headers["Content-type"] = "text/csv"

    return response


@api.route('/tg/group_user/tag/update', methods=['POST'])
def tg_group_user_modify_tag():
    args = request.json
    tg_user_id = get_or_exception('tg_user_id', args, 'int')
    tag_id_list = get_or_exception('tag_id_list', args, 'str', '')
    if tag_id_list:
        tag_id_list = tag_id_list.split(',')
        tag_id_list = [int(t) for t in tag_id_list]
    TgGroupUserTag.query.filter(TgGroupUserTag.tg_user_id == tg_user_id).delete()
    for tag_id in tag_id_list:
        obj = TgGroupUserTag(tg_user_id=tg_user_id, tag_id=tag_id)
        db.session.add(obj)
    db.session.commit()
    return success()
