from flask import request, render_template, redirect, url_for

from jd import db
from jd.models.tg_account import TgAccount

from jd.tasks.telegram.tg import add_account, fetch_person_chat_history
from jd.views import get_or_exception, success
from jd.views.api import api


@api.route('/tg/account/add', methods=['POST'])
def tg_account_add():
    api_id = get_or_exception('api_id', request.form, 'str')
    api_hash = get_or_exception('api_hash', request.form, 'str')
    username = get_or_exception('username', request.form, 'str')
    phone = get_or_exception('phone', request.form, 'str')
    # password = get_or_exception('password', request.form, 'str')
    username = username.replace(' ', '')
    obj = TgAccount.query.filter_by(phone=phone).first()
    if obj and obj.status == TgAccount.StatusType.JOIN_SUCCESS:
        return redirect(url_for('api.tg_account_index'))
    if not obj:
        obj = TgAccount(name=username, phone=phone, api_id=api_id, api_hash=api_hash)
        db.session.add(obj)
        db.session.flush()
    TgAccount.query.filter_by(phone=phone).update({'status': TgAccount.StatusType.JOIN_ONGOING})
    db.session.commit()
    origin = 'celery'
    add_account.delay(obj.id, origin=origin)

    return success()


@api.route('/tg/account/verify', methods=['POST'])
def tg_account_verify():
    phone = get_or_exception('phone', request.form, 'str')
    code = get_or_exception('code', request.form, 'str', '')
    obj = TgAccount.query.filter_by(phone=phone).first()
    if not obj:
        return redirect(url_for('api.tg_account_index'))

    origin = 'celery'
    add_account.delay(obj.id, code=code, origin=origin)

    return redirect(url_for('api.tg_account_index'))


@api.route('/tg/account/index', methods=['GET'])
def tg_account_index():
    account_list = TgAccount.query.order_by(TgAccount.id.desc()).all()
    status_map = {
        TgAccount.StatusType.JOIN_SUCCESS: '加入成功',
        TgAccount.StatusType.JOIN_FAIL: '加入失败',
        TgAccount.StatusType.JOIN_ONGOING: '进行中',
        TgAccount.StatusType.NOT_JOIN: '未加入'
    }
    data = [{
        'id': account.id,
        'phone': account.phone,
        'user_id': account.user_id,
        'nickname': account.nickname,
        'status_text': status_map.get(account.status),
        'status': account.status
    } for account in account_list]
    return render_template('tg_account.html', data=data)


@api.route('/tg/account/delete', methods=['GET'])
def tg_account_delete():
    id = get_or_exception('id', request.args, 'int')
    TgAccount.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('api.tg_account_index'))


@api.route('/tg/account/chat/search', methods=['POST'])
def tg_account_chat_search():
    account_id = get_or_exception('account_id', request.json, 'str')
    account_id_list = [int(i) for i in account_id.split(',')]
    tg_accounts = TgAccount.query.filter(TgAccount.id.in_(account_id_list), TgAccount.status == TgAccount.StatusType.JOIN_SUCCESS).all()
    for account in tg_accounts:
        fetch_person_chat_history.delay(account.id)

    return redirect(url_for('api.tg_account_index'))
