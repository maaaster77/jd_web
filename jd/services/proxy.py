import logging

import urllib.request

import string
import zipfile

import requests

from jd import app

logger = logging.getLogger(__name__)


class OxylabsProxy:
    """
    代理
    https://dashboard.oxylabs.io/en/
    """
    proxy_url = f'{app.config["OXYLABS_HOST"]}:{app.config["OXYLABS_PORT"]}'

    @classmethod
    def get_ip(cls):
        username = app.config['OXYLABS_USERNAME']
        password = app.config['OXYLABS_PASSWORD']
        if not username or not password:
            logger.error('未配置oxylabs代理账号密码')
            return ''
        proxy = f'http://{username}:{password}@{cls.proxy_url}'
        proxies = {
            'http': proxy,
            'https': proxy,
        }
        try:
            response = requests.get('https://ip.oxylabs.io/location', proxies=proxies, timeout=10)
            data = response.json()
            logger.info(f'代理数据:{data}')
            status_code = response.status_code
            if status_code != 200:
                logger.warning(f'请求代理ip失败，状态非200：{status_code}')
                return ''
            now_ip = data.get('ip', '')
            logger.info(f'当前代理ip: {now_ip}')
            if now_ip:
                # return f'{now_ip}:{cls.proxy_port}'
                return now_ip
        except Exception as e:
            logger.warning(f'获取代理ip失败:{e}')
            print(e)

        return ''

    @classmethod
    def get_proxy(cls):
        username = app.config['OXYLABS_USERNAME']
        password = app.config['OXYLABS_PASSWORD']
        ip = cls.get_ip()
        if not ip:
            return ''
        return f'http://{username}:{password}@{ip}'


# 创建chrome浏览器插件的方法
def create_proxyauth_extension(proxy_host, proxy_port, proxy_username, proxy_password, scheme='http', plugin_path=None):
    """Proxy Auth Extension
    args:
        proxy_host (str): domain or ip address, ie proxy.domain.com
        proxy_port (int): port
        proxy_username (str): auth username
        proxy_password (str): auth password
    kwargs:
        scheme (str): proxy scheme, default http
        plugin_path (str): absolute path of the extension
    return str -> plugin_path
    """
    if plugin_path is None:
        plugin_path = 'Selenium-Chrome-HTTP-Private-Proxy.zip'
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """
    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                  singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                  },
                  bypassList: ["foobar.com"]
                }
              };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    print(OxylabsProxy().get_ip())
