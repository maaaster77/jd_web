from flask import render_template, redirect, url_for, request

from jd import db
from jd.models.result_tag import ResultTag
from jd.services.tag import TagService
from jd.views import get_or_exception
from jd.views.api import api


@api.route('/tag/list', methods=['GET'])
def tag_list():
    tags = ResultTag.query.filter(ResultTag.status == ResultTag.StatusType.VALID).order_by(ResultTag.updated_at.desc()).all()
    data = [{
        'id': row.id,
        'name': row.title,
        'status': TagService.StatusMap[row.status],
        'created_at': row.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    } for row in tags]
    return render_template('tag_manage.html', data=data)


@api.route('/tag/delete')
def tag_delete():
    tag_id = get_or_exception('tag_id', request.args, 'int')
    tag = ResultTag.query.filter_by(id=tag_id).first()
    if tag:
        ResultTag.query.filter_by(id=tag_id, status=ResultTag.StatusType.VALID).update(
            {'status': ResultTag.StatusType.INVALID})

    return redirect(url_for('api.tag_list'))


@api.route('/tag/add', methods=['POST'])
def tag_add():
    name = get_or_exception('name', request.form, 'str')
    tag = ResultTag.query.filter_by(title=name).first()
    if tag:
        ResultTag.query.filter_by(title=name).update({'status': ResultTag.StatusType.VALID})
    else:
        tag = ResultTag(title=name)
        db.session.add(tag)

    return redirect(url_for('api.tag_list'))
