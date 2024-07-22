import collections

from flask import jsonify, request, render_template, redirect, url_for

from jd import db
from jd.models.black_keyword import BlackKeyword
from jd.models.keyword_search import KeywordSearch
from jd.models.keyword_search_parse_result import KeywordSearchParseResult
from jd.models.keyword_search_parse_result_tag import KeywordSearchParseResultTag
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


@api.route('/black_keyword/result', methods=['GET'])
def black_keyword_search_result():
    args = request.args
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 20)

    query = KeywordSearchParseResult.query.filter()
    total_records = query.count()
    parse_result = query.order_by(KeywordSearchParseResult.id.desc()).offset((page - 1) * page_size).limit(
        page_size).all()
    parse_id_list = [row.id for row in parse_result]
    parse_tag_list = KeywordSearchParseResultTag.query.filter(
        KeywordSearchParseResultTag.parse_id.in_(parse_id_list)).all()
    parse_tag_result = collections.defaultdict(list)
    for p in parse_tag_list:
        parse_tag_result[p.parse_id].append(p.tag_id)

    tag_list = [
        {
            'id': 1,
            'name': '信件',
        },
        {
            'id': 2,
            'name': '烟油',
        },
        {
            'id': 3,
            'name': '色情',
        },
        {
            'id': 4,
            'name': '暴力',
        },
        {
            'id': 5,
            'name': '毒品',
        },
    ]
    tag_dict = {t['id']: t['name'] for t in tag_list}

    total_pages = (total_records + page_size - 1) // page_size
    data = []
    for row in parse_result:
        parse_tag = parse_tag_result.get(row.id, [])
        tag_text = ','.join([tag_dict[t] for t in parse_tag])
        data.append({
            'id': row.id,
            'keyword': row.keyword,
            'url': row.url,
            'desc': row.desc,
            'account': row.account,
            'tag': tag_text,
            'tag_id_list': parse_tag
        })

    return render_template('search_result.html', data=data, total_pages=total_pages, current_page=page,
                           tag_list=tag_list)
