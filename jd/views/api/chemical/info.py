from io import BytesIO

import pandas as pd
from flask import render_template, request, url_for, redirect, make_response

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
    search_product_name = get_or_exception('search_product_name', args, 'str', '')
    search_compound_name = get_or_exception('search_compound_name', args, 'str', '')
    search_platform_id_list = args.getlist('search_platform_id', int)

    offset = (page - 1) * page_size
    query = ChemicalPlatformProductInfo.query
    if search_platform_id_list:
        query = query.filter(ChemicalPlatformProductInfo.platform_id.in_(search_platform_id_list))
    if search_product_name:
        query = query.filter(ChemicalPlatformProductInfo.product_name.like('%' + search_product_name + '%'))
    if search_compound_name:
        query = query.filter(ChemicalPlatformProductInfo.compound_name.like('%' + search_compound_name + '%'))
    product_info_list = query.order_by(ChemicalPlatformProductInfo.id.desc()).offset(
        offset).limit(page_size).all()
    total_records = query.count()
    data = [
        {
            'id': item.id,
            'platform_name': ChemicalPlatformService.PLATFORM_MAP[item.platform_id],
            'product_name': item.product_name,
            'compound_name': item.compound_name,
            'seller_name': item.seller_name,
            'contact_number': item.contact_number,
            'qq_number': item.qq_number,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for item in product_info_list
    ]
    total_pages = (total_records + page_size - 1) // page_size
    platform_list = [{'id': k, 'name': v} for k, v in ChemicalPlatformService.PLATFORM_MAP.items()]
    return render_template('chemical_product.html', data=data, platform_list=platform_list, total_pages=total_pages,
                           current_page=page,
                           page_size=page_size, default_search_platform_id=search_platform_id_list,
                           default_search_compound_name=search_compound_name,
                           default_search_product_name=search_product_name, max=max,min=min)


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


@api.route('/chemical/product/info/download', methods=['GET'])
def chemical_product_info_download():
    args = request.args
    search_platform_id = get_or_exception('search_platform_id', args, 'int', 0)
    search_product_name = get_or_exception('search_product_name', args, 'str', '')
    search_compound_name = get_or_exception('search_compound_name', args, 'str', '')
    query = ChemicalPlatformProductInfo.query
    if search_platform_id:
        query = query.filter(ChemicalPlatformProductInfo.platform_id == search_platform_id)
    if search_product_name:
        query = query.filter(ChemicalPlatformProductInfo.product_name.like('%' + search_product_name + '%'))
    if search_compound_name:
        query = query.filter(ChemicalPlatformProductInfo.compound_name.like('%' + search_compound_name + '%'))
    product_info_list = query.order_by(ChemicalPlatformProductInfo.id.desc()).all()
    data = [
        {
            '平台': ChemicalPlatformService.PLATFORM_MAP[item.platform_id],
            '产品名称': item.product_name,
            '化合物名称': item.compound_name,
            '商家名称': item.seller_name,
            '联系方式': item.contact_number,
        } for item in product_info_list]

    # 创建DataFrame
    columns = ['平台', '产品名称', '化合物名称', '商家名称', '联系方式']
    df = pd.DataFrame(data, columns=columns)

    # 将DataFrame保存到Excel文件
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')

    # 设置响应头
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=product.csv"
    response.headers["Content-type"] = "text/csv"

    return response
