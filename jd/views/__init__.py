from flask import jsonify

from jd import app


class APIException(Exception):

    def __init__(self, err_msg='Unknown', err_code=400, status_code=400, payload=None):
        self.message = err_msg
        self.code = err_code
        self.status_code = status_code
        self.payload = payload or {}

    def __repr__(self):
        return "%s :%d" % (self.message, self.code)


@app.errorhandler(APIException)
def handle_api_exception(e):
    response = jsonify(err_code=e.code, err_msg=e.message, payload=e.payload)
    response.status_code = e.status_code
    return response
