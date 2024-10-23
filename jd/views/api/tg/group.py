import collections
import datetime

from flask import render_template, request, redirect, url_for
from sqlalchemy import func

from jd import db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.models.tg_group_tag import TgGroupTag
from jd.services.spider.tg import TgService
from jd.services.tag import TagService
from jd.tasks.telegram.tg import join_group
from jd.views import get_or_exception, success
from jd.views.api import api


@api.route('/tg/group/list', methods=['GET'])
def tg_group_list():
    args = request.args
    account_id = get_or_exception('account_id', args, 'str', '')
    group_name = get_or_exception('group_name', args, 'str', '')
    remark = get_or_exception('remark', args, 'str', '')
    query = TgGroup.query
    if account_id:
        query = query.filter(TgGroup.account_id == account_id)
    if group_name:
        query = query.filter(TgGroup.name.like('%' + group_name + '%'))
    if remark:
        query = query.filter(TgGroup.remark.like('%' + remark + '%'))
    groups = query.order_by(TgGroup.id.desc()).all()
    tag_list = TagService.list()
    if not groups:
        return render_template('tg_group_manage.html', data=[], tag_list=tag_list)
    group_id_list = [g.id for g in groups]
    parse_tag_list = TgGroupTag.query.filter(TgGroupTag.group_id.in_(group_id_list)).all()
    parse_tag_result = collections.defaultdict(list)
    for p in parse_tag_list:
        parse_tag_result[p.group_id].append(str(p.tag_id))
    tag_dict = {t['id']: t['name'] for t in tag_list}
    chat_postal_time = TgGroupChatHistory.query.with_entities(TgGroupChatHistory.chat_id,
                                                              func.max(TgGroupChatHistory.postal_time).label(
                                                                  'latest_postal_time')).group_by(
        TgGroupChatHistory.chat_id).all()
    chat_postal_time_dict = {t.chat_id: t.latest_postal_time for t in chat_postal_time}

    data = []
    no_chat_history_group = []
    for g in groups:
        parse_tag = parse_tag_result.get(g.id, [])
        tag_text = ','.join([tag_dict.get(int(t), '') for t in parse_tag if tag_dict.get(int(t), '')])
        latest_postal_time = chat_postal_time_dict.get(g.chat_id, '')
        d = {
            'id': g.id,
            'name': g.name,
            'chat_id': g.chat_id,
            'status': TgService.STATUS_MAP[g.status],
            'desc': g.desc,
            'tag': tag_text,
            'tag_id_list': ','.join(parse_tag) if parse_tag else '',
            'created_at': g.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'account_id': g.account_id,
            'photo': g.avatar_path,
            'title': g.title,
            'remark': g.remark,
            'latest_postal_time': latest_postal_time,
            'three_days_ago': 1 if latest_postal_time and latest_postal_time < (
                    datetime.datetime.now() - datetime.timedelta(days=3)) else 0,
            'group_type': g.group_type,
        }
        if not latest_postal_time:
            no_chat_history_group.append(d)
            continue
        data.append(d)
    data = sorted(data, key=lambda x: x['latest_postal_time'])
    data.extend(no_chat_history_group)
    for d in data:
        if not d['latest_postal_time']:
            continue
        d['latest_postal_time'] = d['latest_postal_time'].strftime('%Y-%m-%d %H:%M:%S') if d[
            'latest_postal_time'] else ''
    return render_template('tg_group_manage.html', data=data, tag_list=tag_list, default_account_id=account_id,
                           default_group_name=group_name, default_remark=remark)


@api.route('/tg/group/delete')
def tg_group_delete():
    group_id = get_or_exception('group_id', request.args, 'int')
    TgGroup.query.filter(TgGroup.id == group_id).delete()

    return redirect(url_for('api.tg_group_list'))


@api.route('/tg/group/add', methods=['POST'])
def tg_group_add():
    name = get_or_exception('name', request.form, 'str')
    name_list = name.split(',')
    for name in name_list:
        if not TgGroup.query.filter(TgGroup.name == name).first():
            db.session.add(TgGroup(name=name))
            db.session.flush()
        TgGroup.query.filter_by(name=name).update(
            {'status': TgGroup.StatusType.JOIN_ONGOING})
        db.session.commit()
        join_group.delay(name, 'web')

    return redirect(url_for('api.tg_group_list'))


@api.route('/tg/group/tag/update', methods=['POST'])
def tg_group_tag_update():
    args = request.json
    group_id = get_or_exception('group_id', args, 'int')
    tag_id_list = get_or_exception('tag_id_list', args, 'str', '')
    remark = get_or_exception('remark', args, 'str', '')
    if tag_id_list:
        tag_id_list = tag_id_list.split(',')
        tag_id_list = [int(t) for t in tag_id_list]
    TgGroupTag.query.filter(TgGroupTag.group_id == group_id).delete()
    for tag_id in tag_id_list:
        obj = TgGroupTag(group_id=group_id, tag_id=tag_id)
        db.session.add(obj)
    TgGroup.query.filter(TgGroup.id == group_id).update({
        'remark': remark
    })
    db.session.commit()
    return success()
