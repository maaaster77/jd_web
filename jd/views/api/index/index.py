from flask import jsonify

from jd.helpers.user import current_user_id
from jd.views.api import api


@api.route('/index', methods=['GET'], need_login=True)
def index():
    user_id = int(current_user_id)
    return jsonify({'msg': {
        'user_id': user_id
    }})


@api.route('/', need_login=False)
def hello():
    return jsonify({'msg':'hello, jd!'})