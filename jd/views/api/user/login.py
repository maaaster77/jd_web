from flask import request, jsonify
from flask_jwt_extended import create_access_token

from jd import db
from jd.models.user import User
from jd.views import APIException
from jd.views.api import api


@api.route("auth/login", need_login=False, methods=["GET", "POST"])
def auth_login():
    """登录获取令牌"""
    args = request.get_json()
    username = args.get("username")
    password = args.get("password")

    user = db.session.query(User).filter_by(username=username).one_or_none()

    if not user:
        raise APIException("账号或密码错误！")
    # if User.encrypt_password(password) != user.password:
    #     return jsonify("Wrong password"), 401
    if user.password != password:
        raise APIException("账号或密码错误！")
    access_token = create_access_token(
        identity={"user_id": user.id, "username": user.username})
    return jsonify(access_token=access_token)
