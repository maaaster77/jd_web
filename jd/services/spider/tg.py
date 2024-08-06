import logging
import os

from jd import app
from jd.models.tg_group import TgGroup
from jd.services.spider.telegram_spider import TelegramAPIs

logger = logging.getLogger(__name__)


class TgService:
    STATUS_MAP = {
        TgGroup.StatusType.NOT_JOIN: '未加入',
        TgGroup.StatusType.JOIN_SUCCESS: '已加入',
        TgGroup.StatusType.JOIN_FAIL: '加入失败',
        TgGroup.StatusType.JOIN_ONGOING: '进行中'
    }

    @classmethod
    def init_tg(cls, origin='celery'):
        tg = TelegramAPIs()
        config_js = app.config['TG_CONFIG']
        session_dir = f'{app.static_folder}/utils'
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
            logger.info(e)
            return None
        return tg
