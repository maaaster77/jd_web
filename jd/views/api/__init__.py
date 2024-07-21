from functools import wraps

from flask import Blueprint, redirect, url_for
from flask_jwt_extended import JWTManager

from jd import app, db
from jd.helpers.user import current_user_id
from jd.models.user_role import UserRole
from jd.services.role_service.role import ROLE_MAP
from jd.views import APIException

jwtmanager = JWTManager(app)


class ApiBlueprint(Blueprint):

    def route(self, rule, need_login=True, roles=[], **options):
        """
        web api路由
        :param rule:
        :param need_login:
        :param roles: 角色列表
        :param options:
        :return:
        """

        def decorator(fn):
            endpoint = options.pop('endpoints', fn.__name__)

            @wraps(fn)
            def decorated_view(*args, **kwargs):
                if need_login and not current_user_id:
                    raise APIException('未登录', 40101, 401)

                if roles:
                    role_ids = [ROLE_MAP.get(role, 0) for role in roles]
                    user_role = db.session.query(UserRole).filter(UserRole.user_id == current_user_id,
                                                                  UserRole.role_id.in_(role_ids),
                                                                  UserRole.status == UserRole.StatusType.VALID).first()
                    if not user_role:
                        return redirect(url_for('api.user_no_permission'))

                api_rule = '%s.%s' % ('api', rule.lstrip('/').replace('.', '_'))
                rs = fn(*args, **kwargs)

                db.session.commit()

                return rs

            self.add_url_rule(rule, endpoint,
                              view_func=decorated_view, **options)
            return decorated_view

        return decorator


api = ApiBlueprint('api', 'api')
