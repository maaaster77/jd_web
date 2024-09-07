import requests


def run():
    url = 'https://my.telegram.org/auth'
    https_proxy = 'https://customer-hunyun__wgIH3-sessid-0008875723-sesstime-10:Wasd12345678+@pr.oxylabs.io:7777'
    http_proxy = 'http://customer-hunyun__wgIH3-sessid-0008875723-sesstime-10:Wasd12345678+@pr.oxylabs.io:7777'

    resp = requests.get(url, proxies={'http': http_proxy, 'https': https_proxy}, timeout=20)

    print(resp.text)
