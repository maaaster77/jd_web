import re
import time

import requests
from bs4 import BeautifulSoup

from jd import app


class IchemistrySpider:

    def __init__(self):
        self._url = ''
        self._domain = 'http://www.ichemistry.cn'
        self._page = 0
        self._proxies = app.config['BAIDU_SPIDER_PROXIES']
        self._cookie = ''
        self._headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Cookie': '_ga=GA1.1.515205347.1723011441; lastip=116.233.213.105; JSESSIONID=aaabCJvtXx8ucaxWNzhez; Hm_lvt_299f3df39c22b857aab68f838aaf0c60=1723011581; HMACCOUNT=880130861641254D; _clientkey_=1723011595762; clientkey=1723011595913_3946; searchkey=; _ga_Y7YWBF0XX5=GS1.1.1723088025.2.1.1723088061.0.0.0; visittimes=46; Hm_lpvt_299f3df39c22b857aab68f838aaf0c60=1723102402; topshow-772=1; view=19713; code=W',
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
            html = r.text
            status_code = r.status_code
            if status_code != 200:
                return None
            return html
        except Exception as e:
            print(e)
        return None

    def request_index(self):
        default_url = 'http://www.ichemistry.cn/chemistry'
        for page in range(self._page):
            url = f'{default_url}/p{str(page+1)}.htm'
            print(f'请求:{url}')
            html = self._send_request(url)
            if html is None:
                return
            time.sleep(1)
            soup = BeautifulSoup(html, 'lxml')
            tr_list = soup.find_all('tr')
            for index, tr in enumerate(tr_list):
                if index == 0:
                    continue
                first_a_tag = tr.find('a')
                if not first_a_tag:
                    continue
                product_link = first_a_tag.get('href')
                if not product_link:
                    continue
                yield from self.parse_product_detail(product_link)

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
                continue
            if index == 1:
                product_name = tr.text
                continue
            if index == 2:
                compound_name = tr.text
                continue
            if index > 2:
                break

        supply_info = soup.find(class_='SupplyInfo')
        if supply_info:
            seller_name = supply_info.find('a').text
            pattern = r"咨询电话：(.*?)$"
            match = re.search(pattern, supply_info.text, re.DOTALL)
            if match:
                contact_number = match.group(1)

        yield {
            'product_name': product_name.replace('中文名:', '').replace('\r', '').replace('\n', '').replace(' ', ''),
            'compound_name': compound_name.replace('英文名:', '').replace('\r', '').replace('\n', ''),
            'seller_name': seller_name,
            'contact_number': contact_number,
        }

    def search_query(self, page=1):
        self._set_params(page)
        yield from self.request_index()

    def _set_params(self, page):
        self._page = page


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    m_spider = IchemistrySpider()
    for data in m_spider.search_query(page=2):
        print(data)
