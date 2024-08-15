import time

from flask import request, render_template, redirect, url_for
from flask_socketio import emit

from jd import db, socketio
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
    TgAccount.query.filter_by(phone=phone).update({'code': code})
    db.session.commit()

    origin = 'celery'
    # add_account.delay(obj.id, code=code, origin=origin)

    return success()


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
    tg_accounts = TgAccount.query.filter(TgAccount.id.in_(account_id_list),
                                         TgAccount.status == TgAccount.StatusType.JOIN_SUCCESS).all()
    for account in tg_accounts:
        fetch_person_chat_history.delay(account.id)

    return redirect(url_for('api.tg_account_index'))


@api.route('/tg/account/tow_step_check', methods=['GET'])
def tg_account_tow_step_check():
    phone = get_or_exception('phone', request.args, 'str')
    obj = TgAccount.query.filter_by(phone=phone).first()
    if not obj:
        return success({'two_step': 0})
    if obj.user_id:
        # 不需要验证
        return success({'two_step': 2})
    return success({'two_step': obj.two_step})


@api.route('/tg/account/update_pwd', methods=['POST'])
def tg_account_update_pwd():
    password = get_or_exception('password', request.form, 'str')
    phone = get_or_exception('phone', request.form, 'str')
    TgAccount.query.filter_by(phone=phone).update({'password': password})
    db.session.commit()
    obj = TgAccount.query.filter_by(phone=phone).first()
    # add_account.delay(obj.id, code=obj.code, origin='celery')

    return redirect(url_for('api.tg_account_index'))


@socketio.on('message', namespace='/tg/account')
def handle_message(data):
    name = data.get('name', '')
    phone = data.get('phone', '')
    code = data.get('code', '')
    if not phone:
        emit('response', {'code': 0, 'msg': '手机号不能为空'})
    obj = TgAccount.query.filter_by(phone=phone).first()
    if not obj:
        obj = TgAccount(name=name, phone=phone)
        db.session.add(obj)
        db.session.commit()
    while True:
        if code:
            break
    api_check_code = 1
    if not obj.api_id or not obj.api_hash:
        # 获取api_id和api_hash逻辑
        api_id, api_hash = get_api_config()
        if api_id and api_hash:
            TgAccount.query.filter_by(id=obj.id).update({'api_id': api_id, 'api_hash': api_hash})
            db.session.commit()
            api_check_code = 1
        else:
            api_check_code = 0
    # 发送验证码登录tg
    # add_account.delay(obj.id, origin='celery')
    print('登录tg发送验证码')

    emit('api_confirm', {'code': api_check_code})


def get_api_config():
    api_id = '28331850'
    api_hash = 'c4f94e284a955113ca4240c7a7c071a6'
    return api_id, api_hash
