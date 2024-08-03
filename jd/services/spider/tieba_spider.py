import random
import time

import requests
from bs4 import BeautifulSoup

from jd import app


class TiebaSpider:
    def __init__(self):
        self._url = 'https://tieba.baidu.com/f'
        self._page = 1
        self._q = ''
        self._proxies = app.config['BAIDU_SPIDER_PROXIES']
        self._cookie = ''
        self._headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Cookie': 'BIDUPSID=27BC6EC24B54E2F826B782255A1A1F52; PSTM=1653906529; MCITY=-289%3A; IS_NEW_USER=80c75160ba4ac91c0d6001fa; TIEBAUID=ba052916b2050d10129f60c0; Hm_lvt_98b9d8c2fd6608d564bf2ac2ae642948=1714896620; BAIDUID=CF8D388406718128A63DE9B6C9742339:FG=1; H_WISE_SIDS_BFESS=60450_60360_60467_60498; BDSFRCVID=vtIOJexroG3QjWjtmTJsMoNihmKK0gOTDYLEqyXakbdN_mkVYxnyEG0Pt_HnkLCbNR1CogKK0eOTHvIF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF=tJkJVI0htKK3DJ5YKtrHq4tehHRxtx39WDTOQJ7TtMj8SncmhJJk3fueXxr32xnitIv9-pbwBp5aJfnpMP5fXl4DMnjkhP683mkjbPb7WnrO8hOPXlKaLP4syP4jKxRnWTcAKfA-b4ncjRcTehoM3xI8LNj405OTbIFO0KJzJCFKMI-9jTL5jjPDbfrDa4_XKKOLVhQCLp7ketn4hUt50tIiMlOLBRvNBCOwBRnEWhk2ep72QhrdQJ_-WMQW5t3wXKjW-fTyatTpsIJM5hn1h4PTLU5wQjomaKviaKJHBMb1flTDBT5h2M4qMxtOLR3pWDTm_q5TtUJMeCnTDMFhe6jWjaAfJ6ttfKresJoq2RbhKROvhjRBLnLgyxoObtRxta6B-bc2axbkqp6vX4rshfPUDMJ9LU3kBgT9LMnx--t58h3_XhjZ2-C-QttjQn3dWIoW2pOtBf_aEn7TyU42bf47yhjA0q4Hb6b9BJcjfU5MSlcNLTjpQT8r5MDOK5OuJRLH_K-yJKD5MDvzbtraMtoH-UnLqb5JWmOZ04n-ah05VJc5MROV3MIyXfnwa4vLW20j0h7m3UTdstjwW-QO-40NBUcWLqcOaj54KKJxbU71DRvsLP5F06_dhUJiB5O-Ban7LqTIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbRO4-TFajTvQDxK; H_PS_PSSID=60450_60360_60467_60498_60515_60568_60553_60572; H_WISE_SIDS=60450_60360_60467_60498_60515_60568_60553_60572; BDSFRCVID_BFESS=vtIOJexroG3QjWjtmTJsMoNihmKK0gOTDYLEqyXakbdN_mkVYxnyEG0Pt_HnkLCbNR1CogKK0eOTHvIF_2uxOjjg8UtVJeC6EG0Ptf8g0M5; H_BDCLCKID_SF_BFESS=tJkJVI0htKK3DJ5YKtrHq4tehHRxtx39WDTOQJ7TtMj8SncmhJJk3fueXxr32xnitIv9-pbwBp5aJfnpMP5fXl4DMnjkhP683mkjbPb7WnrO8hOPXlKaLP4syP4jKxRnWTcAKfA-b4ncjRcTehoM3xI8LNj405OTbIFO0KJzJCFKMI-9jTL5jjPDbfrDa4_XKKOLVhQCLp7ketn4hUt50tIiMlOLBRvNBCOwBRnEWhk2ep72QhrdQJ_-WMQW5t3wXKjW-fTyatTpsIJM5hn1h4PTLU5wQjomaKviaKJHBMb1flTDBT5h2M4qMxtOLR3pWDTm_q5TtUJMeCnTDMFhe6jWjaAfJ6ttfKresJoq2RbhKROvhjRBLnLgyxoObtRxta6B-bc2axbkqp6vX4rshfPUDMJ9LU3kBgT9LMnx--t58h3_XhjZ2-C-QttjQn3dWIoW2pOtBf_aEn7TyU42bf47yhjA0q4Hb6b9BJcjfU5MSlcNLTjpQT8r5MDOK5OuJRLH_K-yJKD5MDvzbtraMtoH-UnLqb5JWmOZ04n-ah05VJc5MROV3MIyXfnwa4vLW20j0h7m3UTdstjwW-QO-40NBUcWLqcOaj54KKJxbU71DRvsLP5F06_dhUJiB5O-Ban7LqTIXKohJh7FM4tW3J0ZyxomtfQxtNRJ0DnjtpChbRO4-TFajTvQDxK; BAIDUID_BFESS=CF8D388406718128A63DE9B6C9742339:FG=1; delPer=0; ZFY=Bruh7OLWwM5y2a4XlfNEucPA6edL2:BevtLr89dB6KMk:C; PSINO=3; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BAIDU_WISE_UID=wapp_1722602911606_860; USER_JUMP=-1; Hm_lvt_292b2e1608b0823c1cb6beef7243ef34=1722602912; HMACCOUNT=880130861641254D; video_bubble0=1; ppfuid=FOCoIC3q5fKa8fgJnwzbE0LGziLN3VHbX8wfShDP6RCsfXQp/69CStRUAcn/QmhIlFDxPrAc/s5tJmCocrihdwitHd04Lvs3Nfz26Zt2holplnIKVacidp8Sue4dMTyfg65BJnOFhn1HthtSiwtygiD7piS4vjG/W9dLb1VAdqN/1ViBCqHxAdK+GFkusuXBO0V6uxgO+hV7+7wZFfXG0MSpuMmh7GsZ4C7fF/kTgmvq/k11nkKpEvJu9aKoOwiuNqiSlcS58Ly9mjkdbS+gNuLgcrFRyrB1NUhD+vuUH5U1v2iwj13daM+9aWJ5GJCQM+RpBohGNhMcqCHhVhtXpVObaDCHgWJZH3ZrTGYHmi7XJB9z3y2o8Kqxep5XBCsugNOW5C73e/g54kuY4PKIS8TtlheGhftBTbUILzt33xSjQXz/gJEgSYx1vUQMipXdSecr9yhMSRLVoFktEC1isMd3ElTWP2BbqdT6AN6/w9mvK/S9Ff5RtLDcahg8QCqqP/JUZA7BRBFh68uqDQax10gfXgGxCNf3Sx8e4KXUBrqV/g3hEEf9luu8oPziRIwanIJY1XZupqPZgmfh8BLwT9YUuyc0u8RKTitzO23hSwGX7sI4U3M5cfLBwVX5m74NveYUNi7Li87S8ZbXy31eyxBDK4IiDGlt1VFsxDIz0RsVHZudegSJ4zYa95fLOW41HdqdlVsa4ORVPwaoYgWzWigT4KUSvejPWWbczD37o0JAMY0Xq/mt7JbC+fPJzgUfd9svt2KsTM2NM3tfRHJpB3BWSLl2pae5DO76/xQFgbnRUmmXSoE2caKfAIbUu9YuHJMc4xeuRg7bfpEY/vwboa87Mf4DRxb3AAPFSzwHIQsKUb2NhurFXPHTBQ0ZqOMmlY+ev7ywybLL8HzYMUKf7xXkuNYCZBWkNbmLJnCAaUcxvvi236pnhRAiCpqFQgkNjC1A5ggMDnpv8k9lbQM2eIu01rzx5KJW22MzZ0c8aSEaiiS5MGq2rHDxd+cheyqXoKDbFUOPsQE72/a0kEWC2KhuPKLM9/6dZ00isWP1M71YVK+GcriYXdSGsdTLua2Z4rsiMpSciOy0GtH0BDIaHROBNUIGus13vk3BD9zddjzj9ZJseUlzwEV+bscicwIjSCwQvM4e3xnzVzlld+zvYN0q7Yw+xx5u95PSoz+nO88s9TqjpS2CuGXeoK3JV0ZsrYL63KbB6FE0u0LGhMX2XqphVNhJG/707P2GcCYlcR4=; st_key_id=17; arialoadData=false; wise_device=0; Hm_lpvt_292b2e1608b0823c1cb6beef7243ef34=1722603169; XFI=1fdd8130-50ce-11ef-bf97-29a4b5101e89; BA_HECTOR=a02g80al2l2k2gak25al0ha438gm9l1japll21v; ab_sr=1.0.1_N2VmZmVlMDUxMTM1MThjNjEzMGEyMTA4N2VkZDk1YTNjNDUyOTUzZjE3MjRiMmZhNTc5ZWQwMjZjMGYwYTgzYmY2NTc2YWMxYTEyZmRlMWNkMDdlNzdjZDc5M2I0MmFkYzYyYmZjMTIyODU0MGM2MjE0YzI3ZDFjYTg1OGNiNTMwZDUxMDFlYjY1M2RmMGU1MjA2ZWJlNWRkMzk2NDA4Mg==; st_data=4b63108efda9126d7756f225d42463513939d2218bd7b5bb06bd07c11e521ea3fbd8ec8d5d5b85341fc1229bb84e4c9b2b76d1422c0b710d448cde589d11b9e259efeafe4d43f5fede2bfb3e166cffdf7af4fe773470b5158afdf2803e55df10b72a51d8c8401c9f238a061ed4198cc986ca94935fd957f3edb807c903b99dc57492f1a9b69c64a33479a45f3bb54cfd; st_sign=3ccecee2; XFCS=17AA137A69BD9A8373ADB7DC2B4DB01E126F0D03586BC25D47C461A0BF76F7F1; XFT=4kqxyaIRnoPGLB77IO8tHVc1VPZU8JGCKsPV+yruccU=; RT="z=1&dm=baidu.com&si=9d6df962-e4a6-492e-bc42-29f0f607eb6e&ss=lzcpaobh&sl=y&tt=bo5&bcn=https%3A%2F%2Ffclog.baidu.com%2Flog%2Fweirwood%3Ftype%3Dperf&ld=5zz9&nu=38382w26&cl=61yg"',
            # 'Referer': 'https://tieba.baidu.com/f?ie=utf-8&kw=%E8%80%81%E5%B8%88&fr=search',
            # 'Sec-Fetch-Dest': 'empty',
            # 'Sec-Fetch-Mode': 'cors',
            # 'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
        }
        self._params = {
            'kw': '',
            'ie': 'utf-8',
            'pn': '0',
        }

    def _send_request(self):
        for page in range(self._page):
            page = page + 1
            self._params['pn'] = str((page - 1) * 50)
            print('开始爬取第{}页...'.format(page))
            wait_seconds = random.uniform(1, 2)
            time.sleep(wait_seconds)
            try:
                r = requests.get(self._url, headers=self._headers, params=self._params, proxies=self._proxies)
                html = r.text
                status_code = r.status_code
                if status_code != 200:
                    continue
                yield self._parse_result(page, html)
            except Exception as e:
                print(e)

    def _parse_result(self, page, html):
        html = html.replace('<!--', '').replace('-->', '')
        soup = BeautifulSoup(html, 'html.parser')
        result_list = soup.find_all(class_='col2_right j_threadlist_li_right')
        res_content = []
        for result in result_list:
            title = ''
            content = ''
            title_a = result.find('a', class_='j_th_tit')
            if title_a:
                title = title_a.text.replace('\n', '').replace(' ', '')
            content_div = result.find('div', class_='threadlist_abs threadlist_abs_onlyline')
            if content_div:
                content = content_div.text.replace('\n', '').replace(' ', '')
            if not title and not content:
                content = result.text.replace('\n', '').replace(' ', '')
            res_content.append(f'{title} {content}')
        print('共查询到{}个结果'.format(len(res_content)))
        res_content = ' '.join(res_content)
        return [{
            'content': res_content,
            'page': page,
            'keyword': self._q
        }]

    def search_query(self, query='', page=1):
        if not query:
            return []
        self._set_params(query, page)
        for parse_data in self._send_request():
            yield parse_data

    def _set_params(self, query, page):
        self._q = query
        self._page = page
        self._params.update({
            'kw': self._q,
        })


if __name__ == '__main__':
    app.ready(db_switch=False, web_switch=False, worker_switch=False)
    tieba_spider = TiebaSpider()
    for data in tieba_spider.search_query('出台', 1):
        print(data)
