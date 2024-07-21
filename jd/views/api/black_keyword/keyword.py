from flask import jsonify, request, render_template, redirect, url_for

from jd import db
from jd.models.black_keyword import BlackKeyword
from jd.models.keyword_search import KeywordSearch
from jd.services.spider.search import SpiderSearchService
from jd.tasks.first.spider_search import spider_search_baidu
from jd.views import get_or_exception, APIException, success
from jd.views.api import api


@api.route('/black_keyword/list', methods=['GET'])
def black_keyword_list():
    """
    黑词列表
    :return:
    """
    args = request.args
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 20)
    offset = (page - 1) * page_size
    # 计算总记录数
    total_records = db.session.query(BlackKeyword).filter(
        BlackKeyword.is_delete == BlackKeyword.DeleteType.NORMAL).count()

    # 计算总页数
    total_pages = (total_records + page_size - 1) // page_size
    rows = (db.session.query(BlackKeyword).filter(BlackKeyword.is_delete == BlackKeyword.DeleteType.NORMAL).
            order_by(BlackKeyword.id.desc()).offset(offset).limit(page_size).all())
    data = [{
        'id': row.id,
        'keyword': row.keyword,
        'status': row.status,
        'created_at': row.created_at.strftime('%Y-%m-%d %H:%M:%S'),
    } for row in rows]

    return render_template('black_words.html', data=data, total_pages=total_pages, current_page=page)


@api.route('/black_keyword/add', methods=['POST'])
def black_keyword_add():
    """
    添加黑词
    :return:
    """
    args = request.form
    keyword_list = get_or_exception('keyword_list', args, 'str')
    keyword_list = keyword_list.split(',')
    if not keyword_list:
        raise APIException('参数错误')
    for keyword in keyword_list:
        black_keyword = BlackKeyword(keyword=keyword.strip())
        db.session.add(black_keyword)
    return redirect(url_for('api.black_keyword_list'))


@api.route('/black_keyword/delete', methods=['GET'])
def black_keyword_delete():
    """
    删除黑词
    :return:
    """
    args = request.args
    keyword_id = get_or_exception('keyword_id', args, 'int')
    black_keyword = db.session.query(BlackKeyword).filter_by(id=keyword_id).first()
    if not black_keyword:
        raise APIException('关键词不存在')
    db.session.query(BlackKeyword).filter(BlackKeyword.id == keyword_id,
                                          BlackKeyword.is_delete == BlackKeyword.DeleteType.NORMAL). \
        update({'is_delete': BlackKeyword.DeleteType.DELETE})
    return redirect(url_for('api.black_keyword_list'))


@api.route('/black_keyword/search', methods=['POST'])
def black_keyword_search():
    args = request.json
    keyword_id_list = get_or_exception('keywords', args, 'str')
    search_type = get_or_exception('search_type', args, 'int', default=1)
    if search_type not in [KeywordSearch.SearchType.BAIDU, KeywordSearch.SearchType.GOOGLE]:
        raise APIException('搜索类型错误')
    spider_search_baidu.delay(keyword_id_list, search_type)

    return success({'msg': '搜索中，请稍后！'})
