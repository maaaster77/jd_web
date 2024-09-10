import collections

from flask import render_template, request, redirect, url_for

from jd import db
from jd.models.tg_group import TgGroup
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
    query = TgGroup.query
    if account_id:
        query = query.filter(TgGroup.account_id == account_id)
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

    data = []
    for g in groups:
        parse_tag = parse_tag_result.get(g.id, [])
        tag_text = ','.join([tag_dict.get(int(t), '') for t in parse_tag if tag_dict.get(int(t), '')])
        data.append({
            'id': g.id,
            'name': g.name,
            'chat_id': g.chat_id,
            'status': TgService.STATUS_MAP[g.status],
            'desc': g.desc,
            'tag': tag_text,
            'tag_id_list': ','.join(parse_tag) if parse_tag else '',
            'created_at': g.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'account_id': g.account_id
        })
    return render_template('tg_group_manage.html', data=data, tag_list=tag_list, default_account_id=account_id)


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
        if TgGroup.query.filter(TgGroup.name == name).first():
            continue
        db.session.add(TgGroup(name=name))
        db.session.flush()
        TgGroup.query.filter_by(name=name, status=TgGroup.StatusType.NOT_JOIN).update(
            {'status': TgGroup.StatusType.JOIN_ONGOING})
        db.session.commit()
        join_group.delay(name, 'web')

    return redirect(url_for('api.tg_group_list'))


@api.route('/tg/group/tag/update', methods=['POST'])
def tg_group_tag_update():
    args = request.json
    group_id = get_or_exception('group_id', args, 'int')
    tag_id_list = get_or_exception('tag_id_list', args, 'str', '')
    if tag_id_list:
        tag_id_list = tag_id_list.split(',')
        tag_id_list = [int(t) for t in tag_id_list]
    TgGroupTag.query.filter(TgGroupTag.group_id == group_id).delete()
    for tag_id in tag_id_list:
        obj = TgGroupTag(group_id=group_id, tag_id=tag_id)
        db.session.add(obj)
    db.session.commit()
    return success()
