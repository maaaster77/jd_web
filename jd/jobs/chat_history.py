import datetime
import logging
import time

from jd import app, db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.services.spider.tg import TgService
from jd.tasks.telegram.tg import fetch_group_user_info

logger = logging.getLogger(__name__)


class TgChatHistoryJob:

    def main(self):
        chat_room_list = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).order_by(TgGroup.id.desc()).all()
        if not chat_room_list:
            return

        tg = TgService.init_tg('job')

        async def fetch_chat_history(group_name, chat_id, chat_type='group'):
            chat_id = int(chat_id)
            try:
                chat = await tg.get_dialog(chat_id)
            except Exception as e:
                logger.info(f'{group_name}, 未获取到群组，准备重新加入...{e}')
                chat = None
            if not chat:
                result = await tg.join_conversation(group_name)
                chat_id = result.get('data', {}).get('id', 0)
                if not chat_id:
                    logger.info(f'{group_name}, 未获取到群组id')
                    return
                chat = await tg.get_dialog(chat_id)
                if not chat:
                    logger.info(f'{group_name}, 未加入到到群组')
                    return
            param = {
                "limit": 60,
                # "offset_date": datetime.datetime.now() - datetime.timedelta(hours=8) - datetime.timedelta(minutes=20),
                "last_message_id": -1,
            }
            history_list = []
            async for data in tg.scan_message(chat, **param):
                print("!!!here!!!", data)
                history_list.append(data)
            history_list.reverse()
            message_id_list = [str(data.get("message_id", 0)) for data in history_list if data.get("message_id", 0)]
            msg = TgGroupChatHistory.query.filter(TgGroupChatHistory.message_id.in_(message_id_list),
                                                  TgGroupChatHistory.chat_id == str(chat_id)).all()
            already_message_id_list = [data.message_id for data in msg]
            for data in history_list:
                logger.info(f'add history_data:{data}')
                message_id = str(data.get("message_id", 0))
                if message_id in already_message_id_list:
                    continue
                user_id = str(data.get("user_id", 0))
                nickname = data.get("nick_name", "")

                obj = TgGroupChatHistory(
                    chat_id=str(chat_id),
                    message_id=message_id,
                    nickname=nickname,
                    username=data.get("user_name", ""),
                    user_id=user_id,
                    postal_time=data.get("postal_time", datetime.datetime.now()) + datetime.timedelta(hours=8),
                    message=data.get("message", ""),
                    reply_to_msg_id=str(data.get("reply_to_msg_id", 0)),
                    photo_path=data.get("photo", {}).get('file_path', ''),
                    document_path=data.get("document", {}).get('file_path', ''),
                    document_ext=data.get("document", {}).get('ext', ''),
                )
                db.session.add(obj)
            db.session.commit()
            # 获取用户信息
            if chat_type != 'group':
                return
            for data in history_list:
                user_id = str(data.get("user_id", 0))
                nickname = data.get("nick_name", "")
                username = data.get("user_name", "")
                if not username:
                    continue
                fetch_group_user_info.delay(chat_id, user_id, nickname, username)

        # # 群组聊天
        for chat_room in chat_room_list:
            logger.info(f'开始获取{chat_room.name}记录')
            chat_id = chat_room.chat_id
            with tg.client:
                tg.client.loop.run_until_complete(fetch_chat_history(chat_room.name, chat_id))

        async def get_person_dialog_list():
            chat_list = await tg.get_person_dialog_list()
            for chat in chat_list:
                await fetch_chat_history('私人聊天', chat['id'], chat_type='presion')

        # 私人聊天
        with tg.client:
            tg.client.loop.run_until_complete(get_person_dialog_list())


def run():
    job = TgChatHistoryJob()
    while True:
        try:
            job.main()
            time.sleep(60)
        except Exception as ex:
            print(ex)
            return
    # job.main()
