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
    args = request.args or request.form
    page = get_or_exception('page', args, 'int', 1)
    page_size = get_or_exception('page_size', args, 'int', 20)
    search_keyword = get_or_exception('search_keyword', args, 'str', '')
    search_tag = args.getlist('search_tag', int)
    default_tag_id_list = []
    parse_id_list = []
    if search_tag:
        # 标签是与关系
        default_tag_id_list = search_tag
        parse_tag_list = KeywordSearchParseResultTag.query.filter(
            KeywordSearchParseResultTag.tag_id.in_(search_tag)).all()
        result_p_id_list = [t.parse_id for t in parse_tag_list]
        parse_tag_list = KeywordSearchParseResultTag.query.filter(
            KeywordSearchParseResultTag.parse_id.in_(result_p_id_list)).all()
        group_result = collections.defaultdict(list)
        for tag in parse_tag_list:
            group_result[tag.parse_id].append(tag.tag_id)
        for p_id, t_list in group_result.items():
            if len(t_list) == len(search_tag):
                parse_id_list.append(p_id)
        if not parse_id_list:
            return render_template('search_result.html', data=[], total_pages=1, current_page=page,
                                   tag_list=tag_list, search_keyword=search_keyword, search_tag=search_tag,
                                   default_tag_id_list=default_tag_id_list)

    query = KeywordSearchParseResult.query.filter(
        KeywordSearchParseResult.is_delete == KeywordSearchParseResult.DeleteType.NORMAL)
    if search_keyword:
        query = query.filter(KeywordSearchParseResult.keyword.like(f'%{search_keyword}%'))
    if parse_id_list:
        query = query.filter(KeywordSearchParseResult.id.in_(parse_id_list))
    total_records = query.count()
    parse_result = query.order_by(KeywordSearchParseResult.id.desc()).offset((page - 1) * page_size).limit(
        page_size).all()
    parse_id_list = [row.id for row in parse_result]
    parse_tag_list = KeywordSearchParseResultTag.query.filter(
        KeywordSearchParseResultTag.parse_id.in_(parse_id_list)).all()
    parse_tag_result = collections.defaultdict(list)
    for p in parse_tag_list:
        parse_tag_result[p.parse_id].append(str(p.tag_id))

    tag_dict = {t['id']: t['name'] for t in tag_list}

    total_pages = (total_records + page_size - 1) // page_size
    data = []
    for row in parse_result:
        parse_tag = parse_tag_result.get(row.id, [])
        tag_text = ','.join([tag_dict[int(t)] for t in parse_tag])
        data.append({
            'id': row.id,
            'keyword': row.keyword,
            'url': row.url,
            'desc': row.desc,
            'account': row.account,
            'tag': tag_text,
            'tag_id_list': ','.join(parse_tag) if parse_tag else ''
        })

    return render_template('search_result.html', data=data, total_pages=total_pages, current_page=page,
                           tag_list=tag_list, search_keyword=search_keyword, search_tag=search_tag,
                           default_tag_id_list=default_tag_id_list)


@api.route('/black_keyword/result/tag/update', methods=['POST'])
def black_keyword_search_result_tag_update():
    args = request.json
    parse_id = get_or_exception('parse_id', args, 'int')
    tag_id_list = get_or_exception('tag_id_list', args, 'str', '')
    if tag_id_list:
        tag_id_list = tag_id_list.split(',')
        tag_id_list = [int(t) for t in tag_id_list]
    KeywordSearchParseResultTag.query.filter(KeywordSearchParseResultTag.parse_id == parse_id).delete()
    for tag_id in tag_id_list:
        obj = KeywordSearchParseResultTag(parse_id=parse_id, tag_id=tag_id)
        db.session.add(obj)
    db.session.commit()
    return success()


@api.route('/black_keyword/result/delete')
def black_keyword_search_result_delete():
    args = request.args
    parse_id = get_or_exception('parse_id', args, 'int')
    KeywordSearchParseResult.query.filter(KeywordSearchParseResult.id == parse_id).update(
        {'is_delete': KeywordSearchParseResult.DeleteType.DELETE})
    return redirect(url_for('api.black_keyword_search_result'))


@api.route('/black_keyword/result/add', methods=['POST'])
def black_keyword_search_result_add():
    args = request.json
    keyword = get_or_exception('keyword', args, 'str')
    url = get_or_exception('url', args, 'str')
    account = get_or_exception('account', args, 'str')
    desc = get_or_exception('desc', args, 'str')
    tag_id_list = get_or_exception('tag_id_list', args, 'str', '')
    if tag_id_list:
        tag_id_list = tag_id_list.split(',')

    result = KeywordSearchParseResult(keyword=keyword, url=url, account=account, desc=desc)
    db.session.add(result)
    db.session.flush()
    for tag_id in tag_id_list:
        obj = KeywordSearchParseResultTag(parse_id=result.id, tag_id=tag_id)
        db.session.add(obj)

    return success()
