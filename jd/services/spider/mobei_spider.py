import random
import time

import requests
from bs4 import BeautifulSoup

from jd import app


class MolbaseSpider:
    def __init__(self):
        self._url = 'https://yuanliao.molbase.cn/'
        self._page = 0
        self._proxies = app.config['BAIDU_SPIDER_PROXIES']
        self._cookie = ''
        self._headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': '',
            'sec-ch-ua-platform': '"macOS"',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',

        }
        self._params = {
        }

    def _send_request(self):
        for page in range(self._page):
            page = page + 1
            self._params['page'] = page
            print('开始爬取第{}页...'.format(page))
            wait_seconds = random.uniform(1, 2)
            time.sleep(wait_seconds)
            try:
                r = requests.get(self._url, headers=self._headers, params=self._params, proxies=self._proxies,
                                 timeout=20)
                html = r.text
                status_code = r.status_code
                if status_code != 200:
                    continue
                yield from self._parse_result(page, html)
            except Exception as e:
                print(e)

    def _send_detail_request(self, product_link):
        try:
            r = requests.get(product_link, headers=self._headers, proxies=self._proxies, timeout=20)
            html = r.text
            status_code = r.status_code
            if status_code != 200:
                return {}
            return self._parse_product_result(html)
        except Exception as e:
            print(e)

    def _parse_result(self, page, html):
        soup = BeautifulSoup(html, 'html.parser')
        result_list = soup.find_all('dd')
        product_link_list = []
        for result in result_list:
            link_a = result.find('a')
            product_link = ''
            if link_a:
                product_link = link_a.get('href')
            if not product_link:
                continue
            if 'goods' not in product_link:
                continue
            product_id = product_link.split('/')[-2]
            product_link = f'{self._url}goods/{product_id}'
            yield self._send_detail_request(product_link)

    def _parse_product_result(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find(class_='p-right').find('h1').text
        seller_name = soup.find(class_='company').find('dd').text.strip(' ')
        concat = soup.find(class_='cus-second').find('dd').text.replace(' ', '').replace('\n', '').replace('\t', '')
        div_tspec = soup.find(class_='tspec')
        compound_name = ''
        if div_tspec:
            table = div_tspec.find('table')
            if table:
                first_row = table.find('tr')
                if first_row:
                    compound_name = first_row.find('td').text
        return {
            'product_name': title,
            'seller_name': seller_name,
            'contact_number': concat,
            'compound_name': compound_name,
        }

    def search_query(self, page=1):
        self._set_params(page)
        yield from self._send_request()

    def _set_params(self, page):
        self._page = page


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    m_spider = MolbaseSpider()
    for data in m_spider.search_query(page=1):
        print(data)
