from flask import jsonify, request, render_template, redirect, url_for

from jd import db
from jd.models.role import Role
from jd.models.user import User
from jd.models.user_role import UserRole
from jd.services.role_service.role import ROLE_SUPER_ADMIN
from jd.views import get_or_exception, APIException, success
from jd.views.api import api


@api.route('/user/create', methods=['POST'], roles=[ROLE_SUPER_ADMIN])
def create_user():
    args = request.form
    username = get_or_exception('username', args, 'str')
    role_id = get_or_exception('role_id', args, 'int', 2)
    user = db.session.query(User).filter(User.username == username).first()
    if user:
        raise APIException('用户名已存在')
    role = db.session.query(Role).filter(Role.id == role_id, Role.status == Role.StatusType.VALID).first()
    if not role:
        raise APIException('角色不存在')
    user1 = User(username=username, password='111111')
    db.session.add(user1)
    db.session.flush()
    db.session.add(UserRole(user_id=user1.id, role_id=role_id, status=Role.StatusType.VALID))
    db.session.commit()
    return redirect(url_for('api.user_manage'))


@api.route('/user/manage', roles=[ROLE_SUPER_ADMIN])
def user_manage():
    rows = db.session.query(User).filter(User.status == User.StatusType.VALID).order_by(User.id.desc()).all()
    user_id_list = [row.id for row in rows]
    user_role = db.session.query(UserRole).filter(UserRole.user_id.in_(user_id_list),
                                                  UserRole.status == UserRole.StatusType.VALID).all()
    user_role_dict = {row.user_id: row.role_id for row in user_role}
    role_id_list = [row.role_id for row in user_role]
    role_list = db.session.query(Role).filter(Role.id.in_(role_id_list), Role.status == Role.StatusType.VALID).all()
    role_info = {row.id: row.name for row in role_list}
    data = []
    for row in rows:
        role_id = user_role_dict.get(row.id, 0)
        u = {
            'id': row.id,
            'username': row.username,
            'role_name': role_info.get(role_id, ''),
            'created_at': row.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'role_id': role_id,
        }
        data.append(u)
    roles = db.session.query(Role).filter(Role.status == Role.StatusType.VALID).all()
    roles = [{
        'id': r.id,
        'name': r.name
    } for r in roles]
    return render_template('user_manage.html', users=data, roles=roles)


@api.route('/user/info')
def user_info():
    args = request.args
    user_id = get_or_exception('user_id', args, 'int')
    user = db.session.query(User).filter(User.id == user_id).first()
    user_role = db.session.query(UserRole).filter(UserRole.user_id == user_id,
                                                  UserRole.status == UserRole.StatusType.VALID).first()
    if not user:
        raise APIException('用户不存在')
    role = None
    if user_role:
        role = db.session.query(Role).filter(Role.id == user_role.role_id,
                                             Role.status == Role.StatusType.VALID).first()
    return success({
        'user_id': user.id,
        'username': user.username,
        'role_name': role.name if role else '',
        'role_id': role.id if role else 0
    })


@api.route('/user/delete', roles=[ROLE_SUPER_ADMIN])
def user_delete():
    args = request.args
    user_id = get_or_exception('user_id', args, 'int')
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        raise APIException('用户不存在')
    db.session.query(User).filter(User.id == user_id, User.status == User.StatusType.VALID).update(
        {'status': User.StatusType.INVALID})
    db.session.commit()
    return redirect(url_for('api.user_manage'))


@api.route('/user/update', methods=['POST'], roles=[ROLE_SUPER_ADMIN])
def user_update():
    args = request.form
    user_id = get_or_exception('edit_user_id', args, 'int')
    role_id = get_or_exception('edit_role_id', args, 'int')
    user = db.session.query(User).filter(User.id == user_id).first()
    if not user:
        raise APIException('用户不存在')
    role = db.session.query(Role).filter(Role.id == role_id, Role.status == Role.StatusType.VALID).first()
    if not role:
        raise APIException('角色不存在')

    user_role = db.session.query(UserRole).filter(UserRole.user_id == user_id,
                                                  UserRole.status == UserRole.StatusType.VALID).first()
    if user_role:
        db.session.query(UserRole).filter(UserRole.user_id == user_id,
                                          UserRole.status == UserRole.StatusType.VALID).update({'role_id': role_id})
    if not user_role:
        db.session.add(UserRole(user_id=user_id, role_id=role_id, status=Role.StatusType.VALID))
    db.session.commit()

    return redirect(url_for('api.user_manage'))
