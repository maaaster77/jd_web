import random
import time

import requests


class SpiderBase:
    def __init__(self):
        self._url = ''
        self._page = 1
        self._proxies = None
        self._cookie = ''
        self._headers = {}
        self._params = {}

    def _send_request(self):
        pass

    def search_query(self, query='', page=1, cookie=None, proxies=None):
        pass

    def _parse_result(self, page, html):
        raise NotImplementedError

    def set_page(self, page):
        raise NotImplementedError

    def set_params(self, query, page, cookie, proxies):
        raise NotImplementedError
