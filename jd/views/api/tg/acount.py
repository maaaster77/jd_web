import time

from flask import request, render_template, redirect, url_for
from flask_socketio import emit
from selenium import webdriver
from selenium.webdriver.common.by import By

from jd import db, socketio, app
from jd.models.tg_account import TgAccount
from jd.tasks.first.tg_app import tg_app_init

from jd.tasks.telegram.tg import fetch_person_chat_history, login_tg_account, send_phone_code, fetch_account_channel
from jd.views import get_or_exception, success
from jd.views.api import api


@api.route('/tg/account/add', methods=['POST'])
def tg_account_add():
    args = request.json
    name = get_or_exception('name', request.json, 'str')
    phone = get_or_exception('phone', request.json, 'str')
    name = name.replace(' ', '')
    obj = TgAccount.query.filter_by(phone=phone).first()
    if obj and obj.status == TgAccount.StatusType.JOIN_SUCCESS:
        return redirect(url_for('api.tg_account_index'))
    if not obj:
        obj = TgAccount(name=name, phone=phone)
        db.session.add(obj)
        db.session.flush()
    TgAccount.query.filter_by(phone=phone).update({'status': TgAccount.StatusType.JOIN_ONGOING})
    db.session.commit()
    tg_app_init.delay(phone)

    return success()


@api.route('/tg/account/send_code', methods=['POST'])
def tg_account_send_phone_code():
    """登录tg发送验证码"""
    phone = get_or_exception('phone', request.json, 'str')
    obj = TgAccount.query.filter_by(phone=phone).first()
    if not obj:
        return redirect(url_for('api.tg_account_index'))
    send_phone_code.delay(obj.id)

    return success()


@api.route('/tg/account/verify', methods=['POST'])
def tg_account_verify():
    """登录tg验证code"""
    phone = get_or_exception('phone', request.json, 'str')
    code = get_or_exception('code', request.json, 'str', '')
    obj = TgAccount.query.filter_by(phone=phone).first()
    if not obj:
        return redirect(url_for('api.tg_account_index'))
    TgAccount.query.filter_by(phone=phone).update({'code': code})
    db.session.commit()
    login_tg_account.delay(obj.id)

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
    """
    是否有2FA验证
    :return:
    """
    phone = get_or_exception('phone', request.args, 'str')
    obj = TgAccount.query.filter_by(phone=phone).first()
    if not obj:
        return success({'two_step': 0})
    if obj.user_id:
        # 不需要验证
        return success({'two_step': 2})
    return success({'two_step': obj.two_step})


@api.route('/tg/account/api_check', methods=['GET'])
def tg_account_api_check():
    """
    api_id和api_hash check
    :return:
    """
    phone = get_or_exception('phone', request.args, 'str')
    obj = TgAccount.query.filter_by(phone=phone).first()
    if not obj:
        return success({'code': 0})
    if obj.api_id and obj.api_hash:
        # 不需要验证
        return success({'code': 1})
    return success({'code': -1})


@api.route('/tg/account/update_pwd', methods=['POST'])
def tg_account_update_pwd():
    """
    有2fa验证要输入密码
    :return:
    """

    password = get_or_exception('password', request.form, 'str')
    phone = get_or_exception('phone', request.form, 'str')
    TgAccount.query.filter_by(phone=phone).update({'password': password})
    db.session.commit()
    obj = TgAccount.query.filter_by(phone=phone).first()
    login_tg_account.delay(obj.id)

    return redirect(url_for('api.tg_account_index'))


@api.route('/tg/account/update_api_code', methods=['POST'])
def tg_account_update_api_code():
    code = get_or_exception('code', request.json, 'str')
    phone = get_or_exception('phone', request.json, 'str')
    TgAccount.query.filter_by(phone=phone).update({'api_code': code})
    db.session.commit()
    return success()


@api.route('/tg/account/group/search', methods=['POST'])
def tg_account_group_search():
    account_id = get_or_exception('account_id', request.json, 'str')
    account_id_list = [int(i) for i in account_id.split(',')]
    tg_accounts = TgAccount.query.filter(TgAccount.id.in_(account_id_list),
                                         TgAccount.status == TgAccount.StatusType.JOIN_SUCCESS).all()
    for account in tg_accounts:
        fetch_account_channel.delay(account.id)

    return redirect(url_for('api.tg_account_index'))