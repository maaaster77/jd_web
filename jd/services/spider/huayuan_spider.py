import random
import re
import time
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from jd import app


class HuaYuanSpider:
    def __init__(self):
        self._url = ''
        self._domain = 'https://www.echemsrc.com'
        self._page = 0
        self._proxies = app.config['BAIDU_SPIDER_PROXIES']
        self._cookie = ''
        self._headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Cookie': (
                'Hm_lvt_fed072d037ab06567a53785e77ffdf44=1723212745; '
                'HMACCOUNT=880130861641254D; '
                '__root_domain_v=.echemsrc.com; '
                '_qddaz=QD.838423212745710; '
                '_qdda=3-1.lwnll; '
                '_qddab=3-ekv15k.lzo52yat; '
                'Hm_lpvt_fed072d037ab06567a53785e77ffdf44=1723294781; '
                '_qddac=3-2-1.lwnll.ekv15k.lzo52yat'
            ),
            'Origin': 'https://www.echemsrc.com',
            'Referer': '',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"'
        }
        self._params = {
        }
        self.driver = None

    def _send_request(self, link, params=None):
        if params is None:
            params = {}
        try:
            r = requests.get(link, headers=self._headers, proxies=self._proxies, params=params,
                             timeout=20)
            html = r.text
            status_code = r.status_code
            if status_code != 200:
                return None
            return html
        except Exception as e:
            print(e)
        return None
        # self.driver.get(link)
        # time.sleep(1)
        # return self.driver.page_source

    def _request_product_list(self):
        cid_list = [
            '090101', '090102', '090103', '090104', '090105', '090106', '090107',
            '090201', '090202', '090203', '090204', '090205', '090206', '090207', '090208', '090209', '090210',
            '09020A', '090210B',
            '090301', '090302', '090303', '090304',
            '090401', '090402', '090403', '090404', '090405', '090406', '090407', '090408', '090409', '09040A',
            '09040B', '09040C', '09040D', '09040E', '09040F'
        ]
        url = 'https://www.echemsrc.com/api/search/category'
        for cid in cid_list:
            for page in range(self._page):
                data = {
                    "current": page + 1,
                    "size": 50,
                    "source": "PC",
                    "deliveryTime": 0,
                    "categoryCode": f"{cid}",
                    "purities": [],
                    "specifications": [],
                    "brands": []
                }
                self._headers['Referer'] = f'https://www.echemsrc.com/search?cid={cid}'
                try:
                    resp = requests.post(url, json=data, headers=self._headers)
                    if resp.status_code != 200:
                        continue
                    json_data = resp.json()
                    products = json_data.get('data', {}).get('products', [])
                except Exception as e:
                    continue
                time.sleep(1)
                yield from self.parse_product_detail(products)

    def parse_product_detail(self, products):
        for product in products:
            url = f'https://www.chemsrc.com/cas/{product["casid"]}_{product["chemsrcId"]}.html'
            html = self._send_request(url)
            if html is None:
                continue
            time.sleep(1)
            soup = BeautifulSoup(html, 'lxml')
            product_name = soup.find(class_='flex-center').find('h1').text
            seller_name = ''
            compound_name = ''
            contact_number = ''
            qq_number = ''
            td_list = soup.find('tr', id='firsttr').find_all('td')
            for td in td_list:
                compound_name = td.text
            li_list = soup.find('ul', class_='list-unstyled').find_all('li')
            for li in li_list:
                a_tag = li.find('a')
                if not seller_name and a_tag and 'saler' in a_tag.get('href'):
                    seller_name = a_tag.text
                    continue
                if '联系电话' in li.text:
                    contact_number = li.text.replace('联系电话：', '')
                    continue
                if '联系人' in li.text:
                    a_tag = li.find('a')
                    if not a_tag:
                        continue
                    qq_url = a_tag.get('href')
                    if not qq_url:
                        continue
                    qq_url = f'{self._domain}{qq_url}'
                    parsed_url = urlparse(qq_url)
                    query_params = parse_qs(parsed_url.query)
                    qq_number = query_params.get('qqId', [''])[0]



            yield {
                'product_name': product_name.replace('\r', '').replace('\n', '').replace(' ', ''),
                'seller_name': seller_name.replace('\n', ''),
                'contact_number': contact_number,
                'compound_name': compound_name.replace('\r', '').replace('\n', ''),
                'qq_number': qq_number
            }

    def search_query(self, page=1):
        self._set_params(page)
        yield from self._request_product_list()

    def _set_params(self, page):
        self._page = page


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    m_spider = HuaYuanSpider()
    for data in m_spider.search_query(page=1):
        print(data)
    # link = m_spider.request_chemical_properties('https://www.chemicalbook.com/ProductChemicalPropertiesCB2126672.htm')
    # print('link:', link)
