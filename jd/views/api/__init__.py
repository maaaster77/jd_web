from functools import wraps

from flask import Blueprint
from flask_jwt_extended import JWTManager

from jd import app, db
from jd.helpers.user import current_user_id
from jd.views import APIException

jwtmanager = JWTManager(app)


class ApiBlueprint(Blueprint):

    def route(self, rule, need_login=True, perm_ids=[], **options):
        """
        web api路由
        :param rule:
        :param need_login:
        :param perm_ids: 权限ID列表，拥有 perm_ids 中任何一个权限即可通过，
                         默认None，任何人均无权限，
                         传空数组则不校验权限
        :param options:
        :return:
        """

        def decorator(fn):
            endpoint = options.pop('endpoints', fn.__name__)

            @wraps(fn)
            def decorated_view(*args, **kwargs):
                if need_login and not current_user_id:
                    raise APIException('未登录', 40101, 401)

                # current_perm_ids = []
                # if perm_ids != [] and not pytest_enable:
                #     if perm_ids is None:
                #         raise APIException('权限不足', 40301, 403)
                #
                #     current_perm_ids = current_member.has_perms(perm_ids)
                #     if not current_perm_ids:
                #         raise APIException('权限不足', 40301, 403)

                api_rule = '%s.%s' % ('api', rule.lstrip('/').replace('.', '_'))
                rs = fn(*args, **kwargs)

                db.session.commit()

                return rs

            self.add_url_rule(rule, endpoint,
                              view_func=decorated_view, **options)
            return decorated_view

        return decorator


api = ApiBlueprint('api', 'api')
