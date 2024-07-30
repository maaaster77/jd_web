import datetime
import time

from jd import app, db
from jd.models.tg_group import TgGroup
from jd.models.tg_group_chat_history import TgGroupChatHistory
from jd.services.spider.telegram_spider import TelegramAPIs
from jd.services.spider.tg import TgService
from jd.tasks.first.tg import fetch_group_user_info


class TgChatHistoryJob:

    def main(self):
        chat_room_list = TgGroup.query.filter_by(status=TgGroup.StatusType.JOIN_SUCCESS).all()
        if not chat_room_list:
            return
        tg = TgService.init_tg()
        offset_date = datetime.datetime.now() - datetime.timedelta(minutes=5)
        for chat_room in chat_room_list:
            chat_id = chat_room.chat_id
            last_chat_history = TgGroupChatHistory.query.filter_by(chat_id=chat_id).order_by(
                TgGroupChatHistory.id.desc()).first()
            if not last_chat_history:
                last_message_id = -1
            else:
                last_message_id = last_chat_history.message_id
            chat = tg.get_dialog(chat_id, is_more=False)
            param = {
                "limit": 3000,
                "offset_date": offset_date,
                "last_message_id": last_message_id,
            }
            for data in tg.scan_message(chat, **param):
                message_id = data.get("message_id", 0)
                msg = TgGroupChatHistory.query.filter_by(message_id=message_id).first()
                if msg:
                    continue
                user_id = data.get("user_id", 0)
                nickname = data.get("nick_name", "")
                obj = TgGroupChatHistory(
                    chat_id=chat_id,
                    message_id=message_id,
                    nickname=nickname,
                    username=data.get("user_name", ""),
                    user_id=user_id,
                    postal_time=data.get("postal_time", datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                    message=data.get("message", ""),
                    reply_to_msg_id=data.get("reply_to_msg_id", 0),
                )
                db.session.add(obj)
                db.session.commit()
                fetch_group_user_info.delay(chat_id, user_id, nickname)


def run():
    job = TgChatHistoryJob()
    while True:
        try:
            job.main()
        except Exception as ex:
            print(ex)
        time.sleep(2)
