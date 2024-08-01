import datetime
import time

from jd import app, db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.services.spider.tg import TgService
from jd.tasks.first.tg import fetch_group_user_info


class TgChatHistoryJob:

    def main(self):
        chat_room_list = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
        if not chat_room_list:
            return

        tg = TgService.init_tg()

        async def fetch_chat_history(group_name, chat_id):
            chat_id = int(chat_id)
            chat = await tg.get_dialog(chat_id)
            if not chat:
                result = await tg.join_conversation(group_name)
                chat_id = result.get('data', {}).get('id', 0)
                if not chat_id:
                    return
                chat = await tg.get_dialog(chat_id)
                if not chat:
                    return
            param = {
                "limit": 60,
                # "offset_date": datetime.datetime.now() - datetime.timedelta(hours=8) - datetime.timedelta(minutes=20),
                "last_message_id": -1,
            }
            history_list = []
            async for data in tg.scan_message(chat, **param):
                print(data)
                history_list.append(data)
            history_list.reverse()
            message_id_list = [str(data.get("message_id", 0)) for data in history_list if data.get("message_id", 0)]
            msg = TgGroupChatHistory.query.filter(TgGroupChatHistory.message_id.in_(message_id_list)).all()
            already_message_id_list = [data.message_id for data in msg]
            for data in history_list:
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
                )
                db.session.add(obj)
            db.session.commit()
            # 获取用户信息
            for data in history_list:
                user_id = str(data.get("user_id", 0))
                nickname = data.get("nick_name", "")
                username = data.get("user_name", "")
                if not username:
                    continue
                fetch_group_user_info.delay(chat_id, user_id, nickname, username)

        for chat_room in chat_room_list:
            chat_id = chat_room.chat_id
            with tg.client:
                tg.client.loop.run_until_complete(fetch_chat_history(chat_room.name, chat_id))


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
