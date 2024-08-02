import random
import time

import requests
from bs4 import BeautifulSoup

from jd import app
import os


def save_url(url, response):
    filename = url.split('//')[1]  # 获取最后一部分作为文件名
    filename = filename.split('?')[0]  # 移除 URL 中的查询参数
    # 替换或移除文件名中的非法字符
    filename = filename.replace(':', '_').replace('/', '_').replace('\\', '_')

    # 保存文件的路径
    save_path = os.path.join('log/html', filename)

    # 确保目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # 将内容写入文件
    with open(save_path, 'wb') as file:
        file.write(response.content)


class GoogleSpider:
    def __init__(self):
        self._url = 'https://www.google.com/search'
        self._page = 1
        self._q = ''
        self._proxies = app.config['GOOGLE_SPIDER_PROXIES']
        self._cookie = ''
        self._headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': '',
            'priority': 'u=1, i',
            'referer': 'https://www.google.com/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-arch': '"arm"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version': '"126.0.6478.127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"macOS"',
            'sec-ch-ua-platform-version': '"14.5.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-cookie-deprecation': 'label_only_3',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-client-data': 'CIy2yQEIprbJAQipncoBCOqCywEIkqHLAQiGoM0BCLrIzQEI3aDOAQjjp84BCIiozgEImajOAQiErM4BCNaszgEItK3OAQihrs4BCOWvzgEY9snNARignc4B',
            'x-dos-behavior': 'Embed',
        }
        self._params = {
            'bl': 'JbWy',
            's': 'web',
            'q': '',
            'start': '10',
            'sa': 'N',
            'cs': '0',
        }

    def _send_request(self):
        for page in range(self._page):
            page = page + 1
            self._params['start'] = str(page * 10)
            print('开始爬取第{}页...'.format(page))
            wait_seconds = random.uniform(1, 2)
            time.sleep(wait_seconds)
            try:
                r = requests.get(self._url, headers=self._headers, params=self._params, proxies=self._proxies)
                html = r.text
                status_code = r.status_code
                if status_code != 200:
                    continue
                save_url(f"{self._url}_page{page}", r)
                yield self._parse_result(page, html)
            except Exception as e:
                print(e)

    def _parse_result(self, page, html):
        soup = BeautifulSoup(html, 'html.parser')
        result_list = soup.find_all(class_='dURPMd')
        data = []
        for result in result_list:
            data.append({
                'content': f"{result.text}",
                'page': page,
                'keyword': self._q
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
        self._q = query
        self._page = page
        self._params.update({
            'q': self._q
        })


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    google_spider = GoogleSpider()
    for data in google_spider.search_query('水房', 1):
        print(data)
