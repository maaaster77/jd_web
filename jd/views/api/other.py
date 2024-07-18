from flask import render_template

from jd.views.api import api


@api.route('/user/no_permission', need_login=False)
def user_no_permission():
    return render_template('no_permission.html')