from flask import jsonify

from jd import db
from jd.models.user import User
from jd.views.api import api


@api.route('/user/create')
def create_user():
    user1 = User(username='admin', password='111111')
    db.session.add(user1)
    return jsonify({'msg': 'success'})


@api.route('/user/find')
def user_find():
    user1 = db.session.query(User).filter_by(username='admin').first()
    return jsonify({'msg': {
        'username': user1.username,
        'user_id': user1.id
    }})


