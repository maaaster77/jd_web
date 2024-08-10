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


class ChemicalNineSpider:
    def __init__(self):
        self._url = ''
        self._domain = 'https://m.chem960.com'
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

    def _request_index(self):
        url = f'{self._domain}/chanpin/'
        html = self._send_request(url)
        if not html:
            return
        yield from self._parse_category_result(html)

    def _parse_category_result(self, html):
        soup = BeautifulSoup(html, 'lxml')
        product_box_list = soup.find_all(class_='multi_product_box')
        link_list = []
        for product_box in product_box_list:
            a_tag_list = product_box.find_all('a')
            for a_tag in a_tag_list:
                link = a_tag.get('href')
                if not link:
                    continue
                if 'chanpin' not in link:
                    continue
                link_list.append(link)
        for link in link_list:
            yield from self.request_product_list(link)

    def request_product_list(self, link):
        for page in range(self._page):
            product_link_list = []
            page = page + 1
            params = {
                'page': str(page)
            }
            html = self._send_request(link, params)
            if not html:
                continue
            soup = BeautifulSoup(html, 'lxml')
            product_list = soup.find(class_='product_search_result').find_all('li')
            for product in product_list:
                a_tag_list = product.find_all('a')
                for a_tag in a_tag_list:
                    p_link = a_tag.get('href')
                    if not p_link or 'offer' not in p_link:
                        continue
                    if p_link in product_link_list:
                        continue
                    product_link_list.append(p_link)
            time.sleep(1)
            # for product_link in product_link_list:
                # yield from self.request_product_detail(product_link)
            for l in product_link_list:
                yield from self.request_product_detail(l)


    def request_product_detail(self, link):
        html = self._send_request(link)
        if not html:
            return
        soup = BeautifulSoup(html, 'lxml')
        product_name = soup.find('h2', class_='baseinfo_header').text
        compound_name = ''
        contact_number = soup.find('a', class_='companyphone').text
        seller_name = soup.find('h3', class_='company_header').text
        product_detail_link = soup.find('span', class_='outside_btn').find('a').get('href')
        if product_detail_link:
            detail_html = self._send_request(product_detail_link)
            soup = BeautifulSoup(detail_html, 'lxml')
            item_list = soup.find_all(class_='item_list item_list_all')
            for item in item_list:
                label = item.find('label').text
                if '英文名称' in label:
                    compound_name = item.find('span', class_='copy_text').text
                    break

        yield {
            'product_name': product_name.replace('\r', '').replace('\n', '').replace(' ', ''),
            'seller_name': seller_name.replace('\n', ''),
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
    m_spider = ChemicalNineSpider()
    for data in m_spider.search_query(page=1):
        print(data)
    # link = m_spider.request_chemical_properties('https://www.chemicalbook.com/ProductChemicalPropertiesCB2126672.htm')
    # print('link:', link)
