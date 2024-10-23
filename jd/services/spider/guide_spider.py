import random
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from jd import app


class GuideChemSpider:
    def __init__(self):
        self._url = ''
        self._domain = 'https://china.guidechem.com'
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

    def _request_product_category(self):
        self._url = f'{self._domain}/product/'
        html = self._send_request(self._url)
        if not html:
            return
        yield from self._parse_product_category_result(html)

    def _parse_product_category_result(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        category_div_list = soup.find_all('div', class_='pro_tp_center_left')
        for category_div in category_div_list:
            category_uri_list = category_div.find_all('a')
            for a_category_uri in category_uri_list:
                category_uri = a_category_uri.get('href')
                if not category_uri or 'product' not in category_uri:
                    continue
                category_link = f'{self._domain}{category_uri}'
                yield from self._request_product_list(category_link)

    def _request_product_list(self, category_link):
        for page in range(self._page):
            page = page + 1
            url = self.build_next_product_list_url(category_link, page)
            print(f'{category_link}:开始爬取第{page}页...')
            wait_seconds = random.uniform(1, 2)
            time.sleep(wait_seconds)
            print(f'抓取:{url}')
            html = self._send_request(url)
            if not html:
                continue
            yield from self._parse_product_list_result(html)

    def _parse_product_list_result(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        result_list = soup.find_all(class_='ls_cp_main auinfo')
        product_link_list = []
        for result in result_list:
            tag_a_list = result.find_all('a')
            for tag_a in tag_a_list:
                product_link = tag_a.get('href')
                if not product_link or 'pdetail' not in product_link:
                    continue
                product_link = f'{self._domain}{product_link}'
                if product_link in product_link_list:
                    continue
                product_link_list.append(product_link)
        for p_link in product_link_list:
            html = self._send_request(p_link)
            if not html:
                continue
            yield self._parse_product_detail_result(html, p_link)

    def _parse_product_detail_result(self, html, p_link):
        soup = BeautifulSoup(html, 'html.parser')
        try:
            product_name = soup.find(class_='o_det_mai1').find('h1').text.replace(' ', '')
            dd_list = soup.find(class_='in_cen_main_nt4').find_all('dd')
            compound_name = ''
            for index, dd in enumerate(dd_list):
                dd_text = dd.text
                if '英文名称' not in dd_text:
                    continue
                compound_name = dd.find('em').text
            seller_name = soup.find(class_='t_main_ri2').find('a').text
            contact_number = ''

            # 使用selenium 模拟点击查看联系方式，提取class=clearfix k_miat3的div，在从中获取class=det的em框中的文本，获取联系方式号码
            self.driver.get(p_link)
            # 等待联系方式区域加载完成
            WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "qq_jl"))
            )

            # 查找并点击元素
            contact_button = self.driver.find_element(By.CLASS_NAME, "qq_jl")
            contact_button.click()
            time.sleep(1)

            # 在这里我们直接通过class定位，实际情况下可能需要根据页面结构调整选择器
            contact_info_div = self.driver.find_element(By.CLASS_NAME, "clearfix")
            contact_number_div = contact_info_div.find_element(By.CLASS_NAME, "det")
            contact_number = contact_number_div.text
            d = {
                'product_name': product_name.replace('\r', '').replace('\n', '').replace(' ', ''),
                'compound_name': compound_name.replace('\r', '').replace('\n', ''),
                'seller_name': seller_name,
                'contact_number': contact_number,
                'origin': p_link
            }
            print(f'{d}')
            return d
        except Exception as e:
            print(e)
        return {}

    def search_query(self, page=1):
        self._set_params(page)
        self.start_selenium()
        yield from self._request_product_category()
        self.stop_selenium()

    def _set_params(self, page):
        self._page = page

    def build_next_product_list_url(self, url, page):
        # 解析原始URL
        parts = urlparse(url)
        path = parts.path.split('.')
        path[-1] = f'p{page}.html'
        new_url = f'{self._domain}{"-".join(path)}'

        return new_url

    def start_selenium(self):
        # 初始化webdriver实例
        # https://zhuanlan.zhihu.com/p/657757693 安装Chromedrive
        display = Display(visible=False, size=(800, 600))
        display.start()
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 启动无头模式
        chrome_options.add_argument('--disable-gpu')  # 一些系统可能需要禁用 GPU 加速
        chrome_options.add_argument('--no-sandbox')  # Bypass OS
        service = Service()  # 默认情况下，Service 将查找环境变量中的 ChromeDriver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        # self.driver = webdriver.Chrome()

    def stop_selenium(self):
        self.driver.quit()


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    m_spider = GuideChemSpider()
    for data in m_spider.search_query(page=1):
        print(data)
