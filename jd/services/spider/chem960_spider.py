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
            'Cookie': 'Abp.Localization.CultureName=zh-CN; Hm_lvt_e96d4d23e997677f26ac69b89fc71ec7=1723212645; acw_tc=b4a3921717296738650653693e2a63bdf4e2f90fc0717fa0a601ba0cae; cdn_sec_tc=b4a3921717296738650653693e2a63bdf4e2f90fc0717fa0a601ba0cae; Hm_lvt_5e4cd03aa5344b5b306aa61f32208442=1729673866; HMACCOUNT=880130861641254D; ASP.NET_SessionId=vw3qfuerdoki1wzr1k1bhprh; _clck=iljoxz%7C2%7Cfq9%7C0%7C1682; Hm_lvt_26b035237611eb4fe7e1510be6ef09d4=1729674349; Hm_lpvt_26b035237611eb4fe7e1510be6ef09d4=1729675770; Hm_lpvt_5e4cd03aa5344b5b306aa61f32208442=1729675770; _clsk=2dkd7y%7C1729675771419%7C8%7C1%7Cz.clarity.ms%2Fcollect; acw_sc__v2=6718c39b373a3012a19dafc1f26bcde82c35b889; ssxmod_itna=YqIxyii=K7wxB0Dz=DUDGEtmG7QqGCC7Bz8DAhALqGNUeoDZDiqAPGhDCbf/lg+RpxoUmYxd+fBCSnPFGUBCOTF=s08YdGCmDAoDhx7QDox0=DnxAQDjogheDxpq0rD74irDDxD30xDvsLpKDjmvC9EHHE19HLp5DbpFODiF8DYypDAwhD37z12rhDWaODQvsEPKDExGOfI9mgxGaHFffDlFODm4du1M6DCIvIPFPlZHGEELeeBWubDnDX1e5eW4Y=rDqvn2cslq9W0noK7DTC0PHkx=DixnF4D=; ssxmod_itna2=YqIxyii=K7wxB0Dz=DUDGEtmG7QqGCC7Bz8DAhAqA6cdD/FxKqK7=D2UeD==',
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
                link_list.append('https:' + link)
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
                    product_link_list.append('https:' + p_link)
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
        product_name = soup.find('div', class_='kj-prolistone-h1').text
        compound_name = ''
        contact_number = ''
        seller_name = ''
        qq_number = ''
        contact_li = soup.find(class_='kj-caschangjialist-contact')
        if not contact_li:
            return
        contact_li_list = contact_li.find_all('li')
        for li in contact_li_list:
            li_text = li.text
            if '公司' in li_text:
                seller_name = li_text
                continue
            if '手机' in li_text:
                contact_number = li_text.replace('手机：', '')
                continue
            if 'QQ' in li_text:
                qq_number = li_text.replace('QQ：', '')
        detail = soup.find(id='detail')
        offer_contact_li = detail.find(class_='kj-offer-contact')
        if offer_contact_li:
            li_list = offer_contact_li.find_all('p')
            for li in li_list:
                li_text = li.text
                if '英文别名' in li_text:
                    compound_name = li_text.replace('英文别名：', '')

        return {
            'product_name': product_name.replace('\r', '').replace('\n', '').replace(' ', ''),
            'seller_name': seller_name.replace('\n', ''),
            'contact_number': contact_number,
            'compound_name': compound_name.replace('\r', '').replace('\n', ''),
            'qq_number': qq_number
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
    # m_spider.request_product_detail('https://m.chem960.com/offer/28568805/')
