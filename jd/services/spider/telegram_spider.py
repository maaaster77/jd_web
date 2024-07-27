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
        print('telegram data:{}'.format(data))
        return data

    def _get_div_text(self, soup, class_name):
        div = soup.find_all(class_=class_name, limit=1)
        text = ''
        if div:
            if class_name == 'tgme_page_photo':
                text = div[0].img['src']
            else:
                text = div[0].text.replace('\n', '')
            print(f'telegram | class:{class_name}, text:{text}')
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
    # 用户
    data = spider.search_query('https://t.me/feixingmeiluo')
    print('user data:{}'.format(data))

    # 群组, title中包含subscribers
    data = spider.search_query('https://t.me/huaxuerou')
    print('user data:{}'.format(data))
