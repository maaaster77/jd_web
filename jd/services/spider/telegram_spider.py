import requests
from bs4 import BeautifulSoup


class TelegramSpider:

    def __init__(self):
        self._url = ''
        self._headers = {}
        self._proxies = None

    def _send_request(self):
        try:
            r = requests.get(self._url, headers=self._headers, proxies=self._proxies)
            html = r.text
            status_code = r.status_code
            if status_code != 200:
                return {}
            return self._parse_result(html)
        except Exception as e:
            print(e)
        return {}

    def _parse_result(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'photo_url': self._get_div_text(soup, 'tgme_page_photo'),
            'account': self._get_div_text(soup, 'tgme_page_extra'),
            'username': self._get_div_text(soup, 'tgme_page_title'),
            'desc': self._get_div_text(soup, 'tgme_page_description')
        }
        return data

    def _get_div_text(self, soup, class_name):
        div = soup.find_all(class_=class_name, limit=1)
        text = ''
        if div:
            if class_name == 'tgme_page_photo':
                text = div[0].img['src']
            else:
                text = div[0].text.replace('\n', '')
        return text

    def search_query(self, url=''):
        print('start...')
        if not url:
            return {}
        self._set_params(url)
        tel_data = self._send_request()
        print('end...')
        return tel_data

    def _set_params(self, url):
        self._url = url


if __name__ == '__main__':
    spider = TelegramSpider()
    url_list = ['https://t.me/feixingmeiluo', 'https://t.me/huaxuerou', 'https://t.me/ppo995']
    for url in url_list:
        data = spider.search_query(url)
        if data:
            if '@' in data['account']:
                print(f'个人账户：{url}, data:{data}')
            elif 'subscribers' in data['account']:
                print(f'群组账户：{url}, data:{data}')
            else:
                print(f'其他账户：{url}, data:{data}')
        else:
            print(f'{url}, 无数据')
