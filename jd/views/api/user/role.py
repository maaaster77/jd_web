from jd.views.api import api


@api.route("/role/list", methods=["GET"])
def role_list():

    return "role list"