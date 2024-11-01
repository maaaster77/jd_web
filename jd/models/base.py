import datetime
from decimal import Decimal

from jd import db


class BaseModel(db.Model):
    __abstract__ = True

    def to_dict(self):
        data = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            if isinstance(v, datetime.datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(v, Decimal):
                v = float(v)
            else:
                v = format(v)
            data[k] = v
        return data
