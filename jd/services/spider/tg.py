import logging
import os

import requests

from jd import app
from jd.models.tg_group import TgGroup
from jd.services.spider.telegram_spider import TelegramAPIs, TelegramSpider

logger = logging.getLogger(__name__)


class TgService:
    STATUS_MAP = {
        TgGroup.StatusType.NOT_JOIN: '未加入',
        TgGroup.StatusType.JOIN_SUCCESS: '已加入',
        TgGroup.StatusType.JOIN_FAIL: '加入失败',
        TgGroup.StatusType.JOIN_ONGOING: '进行中'
    }

    @classmethod
    def init_tg(cls, origin='celery', username=''):
        tg = TelegramAPIs()
        config_js = app.config['TG_CONFIG']
        session_dir = f'{app.static_folder}/utils'
        if username:
            session_dir = f'{session_dir}/{username}'
        os.makedirs(session_dir, exist_ok=True)
        if origin == 'web':
            session_name = config_js.get("web_session_name")
        elif origin == 'job':
            session_name = config_js.get("job_session_name")
        elif origin == 'celery':
            session_name = config_js.get("celery_session_name")
        else:
            session_name = config_js.get("session_name")
        session_name = f'{session_dir}/{session_name}'
        api_id = config_js.get("api_id")
        api_hash = config_js.get("api_hash")
        proxy = config_js.get("proxy", {})
        clash_proxy = None
        # 配置代理
        # if proxy:
        #     protocal = proxy.get("protocal", "socks5")
        #     proxy_ip = proxy.get("ip", "127.0.0.1")
        #     proxy_port = proxy.get("port", 7890)
        #     clash_proxy = (protocal, proxy_ip, proxy_port)
        try:
            tg.init_client(
                session_name=session_name, api_id=api_id, api_hash=api_hash, proxy=clash_proxy
            )
        except Exception as e:
            logger.info("init error", e)
            print("here", e)
            return None
        return tg

    @classmethod
    def download_photo(cls, photo_url, user_id):
        try:
            response = requests.get(photo_url)
            image_path = os.path.join(app.static_folder, 'images/avatar')
            os.makedirs(image_path, exist_ok=True)
            file_path = f'{image_path}/{user_id}.jpg'
            # 检查请求是否成功
            if response.status_code == 200:
                # 保存图片到本地
                with open(file_path, 'wb') as file:
                    file.write(response.content)
            else:
                file_path = ''
                print(f"Failed to download photo. Status code: {response.status_code}")
        except Exception as e:
            print(f'{user_id}: 下载头像失败：{e}')
            file_path = ''

        return f'images/avatar/{user_id}.jpg'
