from flask import jsonify, request

from jd import db
from jd.models.user import User
from jd.views import get_or_exception, APIException, success
from jd.views.api import api


@api.route('/user/create', methods=['POST'])
def create_user():
    args = request.get_json()
    username = get_or_exception('username', args, 'str')
    user = db.session.query(User).filter(User.username == username).first()
    if user:
        raise APIException('用户名已存在')
    user1 = User(username=username, password='111111')
    db.session.add(user1)
    return success()
