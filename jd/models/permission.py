from jd import db


class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(31), nullable=False, default='')
    perm_key = db.Column(db.String(255), nullable=False, default='', comment='权限标识')
    level = db.Column(db.Integer, nullable=False, default=0,
                      comment='权限级别 1-一级菜单，2-二级菜单，3-三级功能/页面，4-四级功能')
    type = db.Column(db.Integer, nullable=False, default=0, comment='1-菜单，2-功能，3-页面')
    parent_id = db.Column(db.Integer, nullable=False, default=0, comment='父级id')
    priority = db.Column(db.Integer, nullable=False, default=0, comment='排序')
    status = db.Column(db.Integer, nullable=False, default=0, comment='0:无效,1:有效')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    class StatusType:
        INVALID = 0  # 无效
        VALID = 1  # 有效
