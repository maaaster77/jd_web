import decimal
import logging

from flask import jsonify

from jd import app

logger = logging.getLogger(__name__)


def success(payload={}, err_code=0, err_msg=""):
    """

    :param payload:
    :param err_code:
    :param err_msg:
    :return
    """
    return jsonify(err_code=err_code, err_msg=err_msg, payload=payload)


def get_or_exception(key, args, ptype=None, default=None, err_msg=None):
    """获取参数并检查类型抛出异常

    :param key: str
    :param args: dict
    :param ptype: str 参数的数据类型
    :param default
    :param err_msg: str 自定义错误提示
    :return param's value: :ptype

    """

    if key not in args and default is None:
        raise APIException(err_msg=f"缺少参数：%s" % key)
    elif key not in args and default is not None:
        # 如果默认不为None，且无此参数，返回默认值
        return default

    value = args.get(key)
    try:
        if ptype == "int":
            return int(value or default)
        elif ptype == "decimal":
            return decimal.Decimal(value)
        elif ptype == "float":
            return float(value)
        elif ptype == "str":
            return str(value)
        return value
    except Exception as e:
        logger.exception(e)
        if type(err_msg) is str:
            raise APIException(err_msg=err_msg)
        else:
            raise APIException(err_msg=f"参数错误：%s" % key)


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
