import re
import time

import requests
from bs4 import BeautifulSoup
from charset_normalizer import from_bytes

from jd import app


class ChemBkSpider:

    def __init__(self):
        self._url = ''
        self._domain = 'https://www.chembk.com'
        self._page = 0
        self._proxies = app.config['BAIDU_SPIDER_PROXIES']
        self._cookie = ''
        self._headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'sec-ch-ua-platform': '"macOS"',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',

        }
        self._params = {
        }
        self.driver = None

    def _send_request(self, link):
        try:
            r = requests.get(link, headers=self._headers, proxies=self._proxies,
                             timeout=20)
            detected_encoding = from_bytes(r.content).best().encoding
            r.encoding = detected_encoding
            html = r.text
            status_code = r.status_code
            if status_code != 200:
                return None
            return html
        except Exception as e:
            print(e)
        return None

    def request_index(self):
        url = f'{self._domain}/cn'
        html = self._send_request(url)
        if html is None:
            return
        soup = BeautifulSoup(html, 'lxml')
        content = soup.find('div', class_='tab-content')
        if not content:
            return
        td_list = content.find_all('td')
        for td in td_list:
            a_tag = td.find('a')
            if not a_tag:
                continue
            link = a_tag.get('href')
            if 'cn/chem' not in link:
                continue
            yield from self.parse_product_detail(f'{self._domain}{link}')

    def parse_product_detail(self, product_link):
        time.sleep(1)
        html = self._send_request(product_link)
        if html is None:
            return
        soup = BeautifulSoup(html, 'lxml')
        tr_list = soup.find_all('tr')
        product_name = ''
        contact_number = ''
        compound_name = ''
        seller_name = ''
        for index, tr in enumerate(tr_list):
            if index == 0:
                product_name = tr.text
                continue
            if index == 1:
                compound_name = tr.text
                continue
            break

        card_header = soup.find(class_='card-header')
        if card_header:
            seller_name = card_header.text
        card_body_list = soup.find_all(class_='card-body')
        pattern = r"手机: (\d{11})"
        for card_body in card_body_list:
            match = re.search(pattern, card_body.text, re.DOTALL)
            if match:
                contact_number = match.group(1)
                break

        yield {
            'product_name': product_name.replace('中文名 ', '').replace('\r', '').replace('\n', '').replace(' ', ''),
            'compound_name': compound_name.replace('英文名 ', '').strip(' ').replace('\r', '').replace('\n', ''),
            'seller_name': seller_name.strip(' '),
            'contact_number': contact_number.strip(' '),
        }

    def search_query(self, page=1):
        self._set_params(page)
        yield from self.request_index()

    def _set_params(self, page):
        self._page = page


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    m_spider = ChemBkSpider()
    for data in m_spider.search_query(page=2):
        print(data)
