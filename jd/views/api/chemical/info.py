from flask import render_template, request, url_for, redirect

from jd.models.chemical_platform import ChemicalPlatform
from jd.models.chemical_platform_product_info import ChemicalPlatformProductInfo
from jd.services.chemical import ChemicalPlatformService
from jd.tasks.first.spider_chemical import deal_spider_chemical
from jd.views import get_or_exception, success
from jd.views.api import api


@api.route('/chemical/product/info/list', methods=['GET'])
def chemical_product_info_list():
    """
    获取产品列表
    :return:
    """
    args = request.args
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 20)
    offset = (page - 1) * page_size
    product_info_list = ChemicalPlatformProductInfo.query.order_by(ChemicalPlatformProductInfo.id.desc()).offset(
        offset).limit(page_size).all()
    total_records = ChemicalPlatformProductInfo.query.count()
    data = [
        {
            'id': item.id,
            'platform_name': ChemicalPlatformService.PLATFORM_MAP[item.platform_id],
            'product_name': item.product_name,
            'compound_name': item.compound_name,
            'seller_name': item.seller_name,
            'contact_number': item.contact_number,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for item in product_info_list
    ]
    total_pages = (total_records + page_size - 1) // page_size
    return render_template('chemical_product.html', data=data, total_pages=total_pages, current_page=page,
                           page_size=page_size)


@api.route('/chemical/product/info/search', methods=['POST'])
def chemical_product_info_search():
    """
    搜索产品
    :return:
    """
    args = request.json
    platform_id = get_or_exception('platform_id', args, 'int')
    deal_spider_chemical.delay(platform_id)
    return success()


@api.route('/chemical/product/info/delete', methods=['GET'])
def chemical_product_info_delete():
    """
    删除产品
    :return:
    """
    args = request.args
    id = get_or_exception('id', args, 'int')
    ChemicalPlatformProductInfo.query.filter_by(id=id).delete()
    return redirect(url_for('api.chemical_product_info_list'))
