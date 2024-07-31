import os

from jd import app
from jd.models.tg_group import TgGroup
from jd.services.spider.telegram_spider import TelegramAPIs


class TgService:

    @classmethod
    def init_tg(cls):
        tg = TelegramAPIs()
        config_js = app.config['TG_CONFIG']
        session_name = f'{app.static_folder}/utils/{config_js.get("session_name")}'
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
        tg.init_client(
            session_name=session_name, api_id=api_id, api_hash=api_hash, proxy=clash_proxy
        )
        return tg

    @classmethod
    def join_group(cls, tg, group_name):
        result = tg.join_conversation(group_name)
        chat_id = result.get('data', {}).get('id', 0)
        if result.get('result', 'Failed') == 'Failed':
            update_info = {
                'status': TgGroup.StatusType.JOIN_FAIL
            }
        else:
            update_info = {
                'status': TgGroup.StatusType.JOIN_SUCCESS,
                'chat_id': chat_id
            }
        TgGroup.query.filter_by(name=group_name, status=TgGroup.StatusType.NOT_JOIN).update(update_info)
