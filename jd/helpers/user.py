from functools import partial
from typing import Any

from flask import request, g, session
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from werkzeug.local import LocalProxy

from jd import app


# def _lookup_req_object(name):
#     if hasattr(g, name):
#         return getattr(g, name)
#
#     try:
#         verify_jwt_in_request(optional=True)
#         identity = get_jwt_identity()
#         user_id = identity.get("user_id") if isinstance(identity, dict) else 0
#         user_id = int(user_id) if user_id else 0
#         app.logger.debug("visit user_id: %s", user_id)
#     except Exception as e:
#         app.logger.info("JWT error: %s", e)
#         user_id = 0
#
#     setattr(g, name, user_id)
#     return user_id


def _lookup_req_object_from_session(name: str) -> Any:
    if hasattr(g, name):
        return getattr(g, name)

    # 获取当前请求的用户
    value = session.get(name)

    if not value:
        value = request.args.get(name) or value

    app.logger.info(f"{name}: {value}")
    if not value:
        return None

    setattr(g, name, value)
    return value


# current_user_id = LocalProxy(partial(_lookup_req_object, 'current_user_id'))
current_user_id = LocalProxy(partial(_lookup_req_object_from_session, "current_user_id"))
