import random
import time

import requests
from bs4 import BeautifulSoup

from jd import app
class BaiduSpider:

    def __init__(self):
        self._url = 'https://www.baidu.com/s'
        self._page = 1
        self._proxies = app.config['BAIDU_SPIDER_PROXIES']
        self._wd = ''
        self._cookie = ''
        self._headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            # 需要定期更换
            'Cookie': app.config['BAIDU_COOKIE'],
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'is_xhr': '1',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        self._params = {
            'ie': 'utf-8',
            'newi': '1',
            'mod': '1',
            'isbd': '1',
            'wd': '',
            'base_query': '',
            'pn': '10',
            'oq': '',
            'usm': '3',
            'rsv_idx': '2',
            'bs': '',
            '_ss': '1',
            'clist': '',
            'f4s': '1',
            'csor': '6',
            '_cr1': '32802'
        }

    def _send_request(self):
        for page in range(self._page):
            self._params['pn'] = str(page * 10)
            page = page + 1
            print('开始爬取第{}页...'.format(page))
            wait_seconds = random.uniform(1, 2)
            time.sleep(wait_seconds)
            try:
                r = requests.get(self._url, headers=self._headers, params=self._params, proxies=self._proxies)
                html = r.text
                print(html)
                status_code = r.status_code
                if status_code != 200:
                    continue
                yield self._parse_result(page, html)
            except Exception as e:
                print(e)

    def _parse_result(self, page, html):
        soup = BeautifulSoup(html, 'html.parser')
        result_list = soup.find_all(class_='result c-container xpath-log new-pmd')
        data = []
        for result in result_list:
            title = result.find('a').text
            content = result.text.replace('\n', '')
            data.append({
                # 'content': f"<< {title} >> {content}",
                'content': content,
                'page': page,
                'keyword': self._wd
            })
        print('共查询到{}个结果'.format(len(data)))
        return data

    def search_query(self, query='', page=1):
        if not query:
            return []
        self._set_params(query, page)
        for parse_data in self._send_request():
            yield parse_data

    def _set_params(self, query, page):
        self._wd = query
        self._page = page
        self._params.update({
            'wd': self._wd,
            'base_query': self._wd,
            'bs': self._wd,
            'oq': self._wd,
        })


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    for data in BaiduSpider().search_query('水房', 2):
        print(data)
