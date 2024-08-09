import random
import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from jd import app


class ChemicalBookSpider:
    def __init__(self):
        self._url = ''
        self._domain = 'https://www.chemicalbook.com'
        self._page = 0
        self._proxies = app.config['BAIDU_SPIDER_PROXIES']
        self._cookie = ''
        self._headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'Cookie': '_ancsi_=E22B7CE491134C4E8BD8717BEC133308; __ancsi_=E22B7CE491134C4E8BD8717BEC133308; _ancsi_t_=D191F8451076656228A64FACFC8373CA; __ancsi_t_=D191F8451076656228A64FACFC8373CA; ASP.NET_SessionId=ozeie4ihyzh42oxpve4v5mks; Hm_lvt_7d450754590aa33d1fe40874160c2513=1723015024; HMACCOUNT=880130861641254D; _gcl_au=1.1.1197696987.1723088084; _gid=GA1.2.208328484.1723178242; _ga=GA1.2.1209792967.1723178242; _ga_WYVD9WP1XB=GS1.1.1723178242.1.1.1723178482.0.0.0; _book_q_t=2024-08-09 12:41:37; Hm_lpvt_7d450754590aa33d1fe40874160c2513=1723205924',
            'sec-ch-ua-platform': '"macOS"',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',

        }
        self._params = {
        }

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

    def _request_index(self):
        url = f'{self._domain}/ProductIndex.aspx'
        html = self._send_request(url)
        if not html:
            return
        yield from self._parse_category_result(html)

    def _parse_category_result(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        script_tag = soup.find('script', string=re.compile(r'var\s+html\s*=\s*'))

        # 使用正则表达式提取变量值
        pattern = re.compile(r'var\s+html\s*=\s*(["\'].*?["\']);')
        match = pattern.search(script_tag.string)
        html_value = ''
        if match:
            html_value = match.group(1)
        if not html_value:
            return []
        soup = BeautifulSoup(html_value, 'lxml')
        link_list = []
        tag_a_list = soup.find_all('a')
        for tag_a in tag_a_list:
            link = tag_a.get('href')
            if not link or 'ProductChemicalProperties' not in link:
                continue
            product_link = f'{self._domain}{link}'
            link_list.append(product_link)

        for link in link_list:
            yield from self.request_chemical_properties(link)

    def request_chemical_properties(self, link):
        html = self._send_request(link)
        if not html:
            return
        soup = BeautifulSoup(html, 'lxml')
        supply_info = soup.find(id='SupplyInfo')
        factory_link = supply_info.find('a').get('href')
        product_list_link = f'{self._domain}{factory_link}'
        yield from self.request_product_list(product_list_link)

    def request_product_list(self, link):
        product_link_list = []
        for page in range(self._page):
            page = page + 1
            url = f'{link}{str(page)}.htm'
            html = self._send_request(url)
            if not html:
                continue
            soup = BeautifulSoup(html, 'lxml')
            product_list = soup.find_all(class_='factory_ul')
            for product in product_list:
                a_tag = product.find('a')
                if not a_tag:
                    continue
                product_url = a_tag.get('href')
                if product_url in product_link_list:
                    continue
                product_link = f'{self._domain}{product_url}'
                product_link_list.append(product_link)
            time.sleep(1)
        for product_link in product_link_list:
            yield from self.request_product_detail(product_link)

    def request_product_detail(self, link):
        html = self._send_request(link)
        if not html:
            return
        soup = BeautifulSoup(html, 'lxml')
        product_name = soup.find(class_='P_txt_item').find('h1').text.replace(' ', '')
        table = soup.find(class_='Attribute_item').find('table')
        compound_name = ''
        contact_number = ''
        seller_name = ''
        try:
            if table:
                for tr in table.find_all('tr'):
                    td_list = tr.find_all('td')
                    for td in td_list:
                        attribute_name = td.find(class_='attribute_name').text
                        if '英文名称' not in attribute_name:
                            continue
                        compound_name = td.find(class_='attribute_value').text
                        break
                    if compound_name:
                        break
            seller_name = soup.find(id='CompanyName_CN').text
            contact_number = soup.find(id='Phone').text
        except Exception as e:
            print(e)
        yield {
            'product_name': product_name.replace('\r', '').replace('\n', '').replace(' ', ''),
            'seller_name': seller_name,
            'contact_number': contact_number,
            'compound_name': compound_name.replace('\r', '').replace('\n', '')
        }

    def search_query(self, page=1):
        self._set_params(page)
        yield from self._request_index()

    def _set_params(self, page):
        self._page = page


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    m_spider = ChemicalBookSpider()
    for data in m_spider.search_query(page=1):
        print(data)
    # link = m_spider.request_chemical_properties('https://www.chemicalbook.com/ProductChemicalPropertiesCB2126672.htm')
    # print('link:', link)
