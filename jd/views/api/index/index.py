from flask import jsonify, render_template

from jd import app
from jd.helpers.user import current_user_id
from jd.views.api import api


@api.route('/index', methods=['GET', 'POST'], need_login=False)
def index():
    return render_template('login.html')