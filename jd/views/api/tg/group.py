from flask import render_template, request, redirect, url_for

from jd import db
from jd.models.tg_group import TgGroup
from jd.services.spider.tg import TgService
from jd.tasks.first.tg import join_group
from jd.views import get_or_exception
from jd.views.api import api


@api.route('/tg/group/list', methods=['GET'])
def tg_group_list():
    groups = TgGroup.query.order_by(TgGroup.id.desc()).all()
    data = [{
        'id': g.id,
        'name': g.name,
        'chat_id': g.chat_id,
        'status': TgService.STATUS_MAP[g.status],
        'created_at': g.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    } for g in groups]
    return render_template('tg_group_manage.html', data=data)


@api.route('/tg/group/delete')
def tg_group_delete():
    group_id = get_or_exception('group_id', request.args, 'int')
    TgGroup.query.filter(TgGroup.id == group_id).delete()

    return redirect(url_for('api.tg_group_list'))


@api.route('/tg/group/add', methods=['POST'])
def tg_group_add():
    name = get_or_exception('name', request.form, 'str')
    if TgGroup.query.filter(TgGroup.name == name).first():
        return redirect(url_for('api.tg_group_list'))

    obj = TgGroup(name=name)
    db.session.add(obj)
    db.session.commit()
    join_group.delay(name)

    return redirect(url_for('api.tg_group_list'))
