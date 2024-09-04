import requests

from jd.services.proxy import OxylabsProxy

if __name__ == '__main__':
    # 设置代理服务器
    # proxy_ip = OxylabsProxy.get_ip()
    # resp = requests.get(url, proxies={
    #     'http': "http://customer-hunyun__wgIH3-sessid-0473277923-sesstime-10:Wasd12345678+@pr.oxylabs.io:7777",
    #     'https': "http://customer-hunyun__wgIH3-sessid-0473277923-sesstime-10:Wasd12345678+@pr.oxylabs.io:7777"},
    #                     timeout=10)
    # url = 'https://www.google.com/'
    url = "https://httpbin.org/ip"

    resp = requests.get(url, proxies={
        'http': f"http://customer-hunyun__wgIH3-cc-us-st-us_louisiana-city-houma-sessid-0452613090-sesstime-1:Wasd12345678+@cnt9t1is.com:8000",
        'https': f"http://customer-hunyun__wgIH3-cc-us-st-us_louisiana-city-houma-sessid-0452613090-sesstime-1:Wasd12345678+@cnt9t1is.com:8000"},
                        timeout=10)

    print(resp.text)
