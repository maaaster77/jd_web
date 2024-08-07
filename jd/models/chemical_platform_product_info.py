from jd import db


class ChemicalPlatformProductInfo(db.Model):
    __tablename__ = 'chemical_platform_product_info'
    id = db.Column(db.Integer, primary_key=True)
    platform_id = db.Column(db.Integer, nullable=False, unique=False, default=0, comment='平台id')
    product_name = db.Column(db.String(126), nullable=False, unique=False, default='', comment='产品名称')
    seller_name = db.Column(db.String(126), nullable=False, unique=False, default='', comment='卖家名称')
    compound_name = db.Column(db.String(126), nullable=False, unique=False, default='', comment='化合物名称')
    contact_number = db.Column(db.String(126), nullable=False, unique=False, default='', comment='联系电话')
    status = db.Column(db.Integer, nullable=False, default=0, comment='状态 0-待处理 1-处理中 2-已处理')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())